import { useState, useEffect } from 'react';
import { API_BASE } from '../config';
import './StateAnalysis.css';

const StateAnalysis = ({ isDetecting }) => {
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchState = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/nlp/state?minutes=10`);
      const data = await response.json();
      console.log('State loaded:', data);
      
      if (data.success && data.data.data_points > 0) {
        setState(data.data);
      } else {
        setState(null);
        setError('No data available yet');
      }
    } catch (err) {
      console.error('Error fetching state:', err);
      setError('Failed to load state');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Load state on mount
    fetchState();
  }, []);

  useEffect(() => {
    if (isDetecting) {
      // Refresh every 20 seconds during detection
      const interval = setInterval(fetchState, 20000);
      return () => clearInterval(interval);
    }
  }, [isDetecting, fetchState]);

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h2 style={{ margin: 0 }}>Current State Analysis</h2>
        <button onClick={fetchState} disabled={loading} className="success">
          {loading ? 'Refreshing...' : 'Refresh State'}
        </button>
      </div>
      
      {error && <p style={{ color: '#f56565' }}>{error}</p>}
      {loading && <p>Loading state...</p>}
      
      {state && !loading && (
        <div className="stats-grid">
          <div className="stat-box">
            <strong>{state.dominant_emotion}</strong>
            <small>Dominant Emotion</small>
          </div>
          <div className="stat-box">
            <strong>{state.energy_level}</strong>
            <small>Energy Level</small>
          </div>
          <div className="stat-box">
            <strong>{state.avg_sentiment}</strong>
            <small>Avg Sentiment</small>
          </div>
          <div className="stat-box">
            <strong>{state.data_points}</strong>
            <small>Data Points</small>
          </div>
        </div>
      )}
      
      {!state && !loading && !error && (
        <p>Start detection to collect data</p>
      )}
    </div>
  );
};

export default StateAnalysis;
