import React, { useState } from 'react';
import { createGene } from '../utils/api';

function GeneSelector({ genes, selectedGene, onSelect, onRefresh }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newGene, setNewGene] = useState({
    name: '',
    description: '',
    organism: '',
    reference_sequence: '',
    category: 'AMR'
  });
  const [adding, setAdding] = useState(false);

  const categories = ['all', ...new Set(genes.map(g => g.category))];

  const filteredGenes = genes.filter(gene => {
    const matchesSearch = gene.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          gene.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === 'all' || gene.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const handleAddGene = async (e) => {
    e.preventDefault();
    setAdding(true);
    try {
      await createGene(newGene);
      setShowAddModal(false);
      setNewGene({ name: '', description: '', organism: '', reference_sequence: '', category: 'AMR' });
      onRefresh();
    } catch (err) {
      alert(err.message);
    } finally {
      setAdding(false);
    }
  };

  const getCategoryBadgeClass = (category) => {
    switch (category) {
      case 'AMR': return 'bg-danger';
      case 'virulence': return 'bg-warning text-dark';
      case 'housekeeping': return 'bg-info';
      default: return 'bg-secondary';
    }
  };

  return (
    <div>
      <div className="mb-3">
        <input
          type="text"
          className="form-control"
          placeholder="Search genes..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="mb-3">
        <select
          className="form-select"
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>
              {cat === 'all' ? 'All Categories' : cat}
            </option>
          ))}
        </select>
      </div>

      <div className="d-flex justify-content-between align-items-center mb-3">
        <small className="text-muted">{filteredGenes.length} genes</small>
        <button
          className="btn btn-sm btn-outline-primary"
          onClick={() => setShowAddModal(true)}
        >
          + Add Gene
        </button>
      </div>

      <div className="list-group" style={{ maxHeight: '500px', overflowY: 'auto' }}>
        {filteredGenes.map(gene => (
          <button
            key={gene.id}
            className={`list-group-item list-group-item-action ${selectedGene?.id === gene.id ? 'active' : ''}`}
            onClick={() => onSelect(gene)}
          >
            <div className="d-flex justify-content-between align-items-start">
              <div>
                <h6 className="mb-1">{gene.name}</h6>
                <small className="text-muted d-block" style={{ maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {gene.description}
                </small>
              </div>
              <span className={`badge category-badge ${getCategoryBadgeClass(gene.category)}`}>
                {gene.category}
              </span>
            </div>
          </button>
        ))}
      </div>

      {showAddModal && (
        <div className="modal show d-block" tabIndex="-1" style={{ background: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Add New Gene</h5>
                <button type="button" className="btn-close" onClick={() => setShowAddModal(false)}></button>
              </div>
              <form onSubmit={handleAddGene}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Gene Name *</label>
                    <input
                      type="text"
                      className="form-control"
                      value={newGene.name}
                      onChange={(e) => setNewGene({ ...newGene, name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Description</label>
                    <textarea
                      className="form-control"
                      rows="2"
                      value={newGene.description}
                      onChange={(e) => setNewGene({ ...newGene, description: e.target.value })}
                    ></textarea>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Organism</label>
                    <input
                      type="text"
                      className="form-control"
                      value={newGene.organism}
                      onChange={(e) => setNewGene({ ...newGene, organism: e.target.value })}
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Category</label>
                    <select
                      className="form-select"
                      value={newGene.category}
                      onChange={(e) => setNewGene({ ...newGene, category: e.target.value })}
                    >
                      <option value="AMR">AMR</option>
                      <option value="virulence">Virulence</option>
                      <option value="housekeeping">Housekeeping</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Reference Sequence *</label>
                    <textarea
                      className="form-control font-monospace"
                      rows="4"
                      value={newGene.reference_sequence}
                      onChange={(e) => setNewGene({ ...newGene, reference_sequence: e.target.value.toUpperCase() })}
                      placeholder="ATCGATCG..."
                      required
                    ></textarea>
                    <small className="text-muted">Length: {newGene.reference_sequence.length} bp</small>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={adding}>
                    {adding ? 'Adding...' : 'Add Gene'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default GeneSelector;
