import React, { useState, useEffect } from 'react';
import GeneSelector from './components/GeneSelector';
import SequenceUpload from './components/SequenceUpload';
import AlignmentViewer from './components/AlignmentViewer';
import Dashboard from './components/Dashboard';
import { fetchGenes, loadDemoGenes } from './utils/api';

function App() {
  const [genes, setGenes] = useState([]);
  const [selectedGene, setSelectedGene] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadGenes();
  }, [refreshKey]);

  const loadGenes = async () => {
    try {
      setLoading(true);
      let data = await fetchGenes();
      if (data.length === 0) {
        await loadDemoGenes();
        data = await fetchGenes();
      }
      setGenes(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneSelect = (gene) => {
    setSelectedGene(gene);
  };

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center vh-100">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-vh-100" style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)' }}>
      <nav className="navbar navbar-dark bg-dark shadow-sm">
        <div className="container">
          <span className="navbar-brand mb-0 h1">
            <span className="me-2">🧬</span>
            Gene Analyzer
          </span>
          <span className="text-muted">Sequence Alignment Tool</span>
        </div>
      </nav>

      <div className="container py-4">
        {error && (
          <div className="alert alert-danger alert-dismissible fade show" role="alert">
            {error}
            <button type="button" className="btn-close" onClick={() => setError(null)}></button>
          </div>
        )}

        <div className="row g-4">
          <div className="col-lg-4">
            <div className="card shadow-sm h-100">
              <div className="card-header bg-primary text-white">
                <h5 className="mb-0">Select Gene Target</h5>
              </div>
              <div className="card-body">
                <GeneSelector
                  genes={genes}
                  selectedGene={selectedGene}
                  onSelect={handleGeneSelect}
                  onRefresh={handleRefresh}
                />
              </div>
            </div>
          </div>

          <div className="col-lg-8">
            {selectedGene ? (
              <div className="card shadow-sm">
                <div className="card-header bg-success text-white d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">{selectedGene.name}</h5>
                  <span className="badge bg-light text-dark">{selectedGene.category}</span>
                </div>
                <div className="card-body">
                  <div className="row mb-3">
                    <div className="col-md-8">
                      <p className="text-muted mb-2">{selectedGene.description}</p>
                      <small className="text-muted">
                        Organism: {selectedGene.organism} | Length: {selectedGene.length}bp | GC: {selectedGene.gc_content}%
                      </small>
                    </div>
                    <div className="col-md-4 text-end">
                      <SequenceUpload geneId={selectedGene.id} onUpload={handleRefresh} />
                    </div>
                  </div>
                  <Dashboard geneId={selectedGene.id} refreshKey={refreshKey} />
                  <hr />
                  <AlignmentViewer geneId={selectedGene.id} refreshKey={refreshKey} />
                </div>
              </div>
            ) : (
              <div className="card shadow-sm">
                <div className="card-body text-center py-5">
                  <h4 className="text-muted">Select a gene to begin analysis</h4>
                  <p className="text-muted">Choose a gene target from the list on the left</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
