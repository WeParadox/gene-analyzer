const API_BASE = '/api';

export async function fetchGenes() {
  const res = await fetch(`${API_BASE}/genes/`);
  if (!res.ok) throw new Error('Failed to fetch genes');
  return res.json();
}

export async function fetchGene(id) {
  const res = await fetch(`${API_BASE}/genes/${id}`);
  if (!res.ok) throw new Error('Failed to fetch gene');
  return res.json();
}

export async function createGene(gene) {
  const res = await fetch(`${API_BASE}/genes/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(gene)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to create gene');
  }
  return res.json();
}

export async function loadDemoGenes() {
  const res = await fetch(`${API_BASE}/genes/load-demo`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to load demo genes');
  return res.json();
}

export async function deleteGene(id) {
  const res = await fetch(`${API_BASE}/genes/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete gene');
  return res.json();
}

export async function fetchSequences(geneId) {
  const url = geneId ? `${API_BASE}/sequences/?gene_id=${geneId}` : `${API_BASE}/sequences/`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch sequences');
  return res.json();
}

export async function uploadFasta(geneId, file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/sequences/upload?gene_id=${geneId}`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to upload FASTA');
  }
  return res.json();
}

export async function deleteSequence(id) {
  const res = await fetch(`${API_BASE}/sequences/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete sequence');
  return res.json();
}

export async function runAlignment(geneId, sequenceId) {
  const res = await fetch(`${API_BASE}/alignment/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gene_id: geneId, sequence_id: sequenceId })
  });
  if (!res.ok) throw new Error('Failed to run alignment');
  return res.json();
}

export async function runBulkAlignment(geneId, sequenceIds) {
  const res = await fetch(`${API_BASE}/alignment/run-bulk`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gene_id: geneId, sequence_ids: sequenceIds })
  });
  if (!res.ok) throw new Error('Failed to run bulk alignment');
  return res.json();
}

export async function fetchAlignments(geneId) {
  const res = await fetch(`${API_BASE}/alignment/gene/${geneId}`);
  if (!res.ok) throw new Error('Failed to fetch alignments');
  return res.json();
}

export async function fetchStats(geneId) {
  const res = await fetch(`${API_BASE}/alignment/stats/${geneId}`);
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}
