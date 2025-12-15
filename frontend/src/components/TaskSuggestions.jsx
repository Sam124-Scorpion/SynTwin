import { useState, useEffect } from 'react';
import { API_BASE } from '../config';
import './TaskSuggestions.css';

const TaskSuggestions = ({ isDetecting }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSuggestions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/nlp/suggestions?minutes=10`);
      const data = await response.json();
      console.log('Suggestions loaded:', data);
      
      if (data.success && data.data) {
        setSuggestions(data.data.suggestions || []);
      } else {
        setSuggestions([]);
      }
    } catch (err) {
      console.error('Error fetching suggestions:', err);
      setError('Failed to load suggestions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Load suggestions on mount
    fetchSuggestions();
  }, []);

  useEffect(() => {
    if (isDetecting) {
      // Refresh every 15 seconds during detection
      const interval = setInterval(fetchSuggestions, 15000);
      return () => clearInterval(interval);
    }
  }, [isDetecting, fetchSuggestions]);

  return (
    <div className="card full-width">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h2 style={{ margin: 0 }}>Smart Task Suggestions</h2>
        <button onClick={fetchSuggestions} disabled={loading} className="success">
          {loading ? 'Refreshing...' : 'Refresh Suggestions'}
        </button>
      </div>
      <div id="taskSuggestions">
        {error && <p style={{ color: '#f56565' }}>{error}</p>}
        {loading && <p>Loading suggestions...</p>}
        {!loading && suggestions.length > 0 && (
          <ul className="suggestions-list">
            {suggestions.map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        )}
        {!loading && suggestions.length === 0 && !error && (
          <p>No suggestions yet. Start detection to get personalized recommendations!</p>
        )}
      </div>
    </div>
  );
};

export default TaskSuggestions;
