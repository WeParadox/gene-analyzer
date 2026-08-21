import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { fetchStats, fetchAlignments } from '../utils/api';

function Dashboard({ geneId, refreshKey }) {
  const [stats, setStats] = useState(null);
  const [alignments, setAlignments] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [geneId, refreshKey]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, alignmentsData] = await Promise.all([
        fetchStats(geneId),
        fetchAlignments(geneId)
      ]);
      setStats(statsData);
      setAlignments(alignmentsData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-3"><div className="spinner-border spinner-border-sm"></div></div>;
  }

  if (!stats || stats.total_sequences === 0) {
    return null;
  }

  const identities = alignments.map(a => a.identity);
  const gaps = alignments.map(a => a.gaps);

  const identityDistribution = {
    x: identities,
    type: 'histogram',
    name: 'Identity %',
    marker: { color: '#4CAF50' },
    opacity: 0.7
  };

  const gapDistribution = {
    x: gaps,
    type: 'histogram',
    name: 'Gaps',
    marker: { color: '#FF9800' },
    opacity: 0.7
  };

  const identityLayout = {
    title: { text: 'Identity Distribution', font: { size: 14 } },
    xaxis: { title: 'Identity (%)', range: [0, 100] },
    yaxis: { title: 'Count' },
    margin: { t: 40, b: 40, l: 40, r: 20 },
    height: 200,
    bargap: 0.1
  };

  const gapLayout = {
    title: { text: 'Gap Distribution', font: { size: 14 } },
    xaxis: { title: 'Number of Gaps' },
    yaxis: { title: 'Count' },
    margin: { t: 40, b: 40, l: 40, r: 20 },
    height: 200,
    bargap: 0.1
  };

  return (
    <div className="mb-3">
      <div className="row g-3 mb-3">
        <div className="col-md-3">
          <div className="card stats-card text-center p-2">
            <div className="card-body py-2">
              <h4 className="mb-0">{stats.total_sequences}</h4>
              <small>Sequences</small>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-center p-2" style={{ background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)', color: 'white' }}>
            <div className="card-body py-2">
              <h4 className="mb-0">{stats.avg_identity.toFixed(1)}%</h4>
              <small>Avg Identity</small>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-center p-2" style={{ background: 'linear-gradient(135deg, #FC466B 0%, #3F5EFB 100%)', color: 'white' }}>
            <div className="card-body py-2">
              <h4 className="mb-0">{stats.max_identity}%</h4>
              <small>Max Identity</small>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-center p-2" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
            <div className="card-body py-2">
              <h4 className="mb-0">{stats.avg_gaps.toFixed(1)}</h4>
              <small>Avg Gaps</small>
            </div>
          </div>
        </div>
      </div>

      {alignments.length > 2 && (
        <div className="row">
          <div className="col-md-6">
            <Plot
              data={[identityDistribution]}
              layout={identityLayout}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '200px' }}
            />
          </div>
          <div className="col-md-6">
            <Plot
              data={[gapDistribution]}
              layout={gapLayout}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '200px' }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
