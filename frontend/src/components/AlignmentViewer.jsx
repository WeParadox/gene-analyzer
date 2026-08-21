import React, { useState, useEffect } from 'react';
import { fetchSequences, fetchAlignments, runAlignment, runBulkAlignment, deleteSequence } from '../utils/api';

function AlignmentViewer({ geneId, refreshKey }) {
  const [sequences, setSequences] = useState([]);
  const [alignments, setAlignments] = useState([]);
  const [selectedAlignment, setSelectedAlignment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aligning, setAligning] = useState(false);

  useEffect(() => {
    loadData();
  }, [geneId, refreshKey]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [seqs, aligns] = await Promise.all([
        fetchSequences(geneId),
        fetchAlignments(geneId)
      ]);
      setSequences(seqs);
      setAlignments(aligns);
      if (aligns.length > 0 && !selectedAlignment) {
        setSelectedAlignment(aligns[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAlignAll = async () => {
    setAligning(true);
    try {
      const sequenceIds = sequences.map(s => s.id);
      await runBulkAlignment(geneId, sequenceIds);
      await loadData();
    } catch (err) {
      alert(err.message);
    } finally {
      setAligning(false);
    }
  };

  const handleAlignSingle = async (sequenceId) => {
    setAligning(true);
    try {
      const result = await runAlignment(geneId, sequenceId);
      await loadData();
      setSelectedAlignment(result);
    } catch (err) {
      alert(err.message);
    } finally {
      setAligning(false);
    }
  };

  const handleDelete = async (seqId) => {
    if (!confirm('Delete this sequence?')) return;
    try {
      await deleteSequence(seqId);
      await loadData();
    } catch (err) {
      alert(err.message);
    }
  };

  const formatAlignment = (alignment) => {
    if (!alignment) return null;

    const lineLength = 60;
    const lines = [];
    const ref = alignment.aligned_ref;
    const query = alignment.aligned_query;
    const match = alignment.match_string;

    for (let i = 0; i < ref.length; i += lineLength) {
      lines.push({
        ref: ref.slice(i, i + lineLength),
        query: query.slice(i, i + lineLength),
        match: match.slice(i, i + lineLength)
      });
    }

    return lines;
  };

  const renderMatchChar = (char) => {
    if (char === '|') return <span className="match-pipe">{char}</span>;
    if (char === '.') return <span className="mismatch">{char}</span>;
    return <span>{char}</span>;
  };

  if (loading) {
    return <div className="text-center py-3"><div className="spinner-border spinner-border-sm"></div></div>;
  }

  if (sequences.length === 0) {
    return (
      <div className="text-center py-4 text-muted">
        <p>No sequences uploaded yet.</p>
        <p>Upload a FASTA file to begin analysis.</p>
      </div>
    );
  }

  const alignmentLines = formatAlignment(selectedAlignment);

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h6 className="mb-0">Sequences ({sequences.length})</h6>
        <button
          className="btn btn-sm btn-primary"
          onClick={handleAlignAll}
          disabled={aligning}
        >
          {aligning ? (
            <>
              <span className="spinner-border spinner-border-sm me-1"></span>
              Aligning...
            </>
          ) : (
            'Align All'
          )}
        </button>
      </div>

      <div className="row">
        <div className="col-md-4">
          <div className="list-group list-group-flush" style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {sequences.map(seq => {
              const seqAlignment = alignments.find(a => a.sequence_id === seq.id);
              return (
                <div
                  key={seq.id}
                  className={`list-group-item list-group-item-action ${selectedAlignment?.sequence_id === seq.id ? 'active' : ''}`}
                  onClick={() => seqAlignment && setSelectedAlignment(seqAlignment)}
                >
                  <div className="d-flex justify-content-between align-items-center">
                    <div className="text-truncate" style={{ maxWidth: '150px' }}>
                      <small className="fw-bold">{seq.name}</small>
                      <br />
                      <small className="text-muted">{seq.length}bp</small>
                    </div>
                    <div className="btn-group btn-group-sm">
                      <button
                        className="btn btn-outline-light btn-sm"
                        onClick={(e) => { e.stopPropagation(); handleAlignSingle(seq.id); }}
                        title="Align"
                      >
                        🎯
                      </button>
                      <button
                        className="btn btn-outline-danger btn-sm"
                        onClick={(e) => { e.stopPropagation(); handleDelete(seq.id); }}
                        title="Delete"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                  {seqAlignment && (
                    <div className="mt-1">
                      <small className="badge bg-success">{seqAlignment.identity}% identity</small>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="col-md-8">
          {selectedAlignment ? (
            <div>
              <div className="d-flex justify-content-between align-items-center mb-2">
                <h6 className="mb-0">Alignment Result</h6>
                <div>
                  <span className="badge bg-primary me-2">Score: {selectedAlignment.score}</span>
                  <span className="badge bg-success me-2">Identity: {selectedAlignment.identity}%</span>
                  <span className="badge bg-warning">Gaps: {selectedAlignment.gaps}</span>
                </div>
              </div>

              <div className="alignment-viewer">
                {alignmentLines?.map((line, i) => (
                  <div key={i} className="sequence-line">
                    <div><span className="label">Ref:  </span><span className="sequence ref">{line.ref}</span></div>
                    <div><span className="label">      </span><span className="sequence match">{line.match.split('').map((c, j) => renderMatchChar(c))}</span></div>
                    <div><span className="label">Query:</span><span className="sequence query">{line.query}</span></div>
                    <div style={{ height: '10px' }}></div>
                  </div>
                ))}
              </div>

              <div className="mt-2">
                <small className="text-muted">
                  Legend: <span className="text-primary">|</span> = Match, <span className="text-danger">.</span> = Mismatch, <span className="text-muted"> </span> = Gap
                </small>
              </div>
            </div>
          ) : (
            <div className="text-center py-4 text-muted">
              <p>Select a sequence with alignment results</p>
              <p>Or click "Align" to run alignment</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AlignmentViewer;
