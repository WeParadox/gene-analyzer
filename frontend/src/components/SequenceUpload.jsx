import React, { useState, useRef } from 'react';
import { uploadFasta } from '../utils/api';

function SequenceUpload({ geneId, onUpload }) {
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleFile = async (file) => {
    if (!file) return;

    setUploading(true);
    setResult(null);

    try {
      const response = await uploadFasta(geneId, file);
      setResult(response);
      onUpload();
    } catch (err) {
      setResult({ message: err.message, errors: [err.message] });
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  return (
    <div>
      <input
        type="file"
        ref={fileInputRef}
        className="d-none"
        accept=".fasta,.fa,.fna,.txt"
        onChange={(e) => handleFile(e.target.files[0])}
      />

      <div
        className={`upload-zone ${dragOver ? 'dragover' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current.click()}
        style={{ cursor: 'pointer', padding: '1rem' }}
      >
        {uploading ? (
          <div className="d-flex align-items-center justify-content-center">
            <div className="spinner-border spinner-border-sm me-2" role="status"></div>
            <span>Uploading...</span>
          </div>
        ) : (
          <div>
            <div className="mb-1">📁 Upload FASTA</div>
            <small className="text-muted">Click or drag & drop</small>
          </div>
        )}
      </div>

      {result && (
        <div className={`mt-2 alert ${result.errors?.length ? 'alert-warning' : 'alert-success'} py-2`} style={{ fontSize: '0.85rem' }}>
          {result.message}
          {result.errors?.length > 0 && (
            <ul className="mb-0 mt-1">
              {result.errors.map((err, i) => <li key={i}>{err}</li>)}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default SequenceUpload;
