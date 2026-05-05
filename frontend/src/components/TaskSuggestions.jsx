import { useState, useCallback } from 'react';
import { API_BASE } from '../config';
import './TaskSuggestions.css';

/** Convert **bold** markers in a string to <strong> elements. */
const renderLine = (line, idx) => {
  const parts = line.split(/\*\*(.*?)\*\*/g);
  return (
    <span key={idx}>
      {parts.map((part, i) =>
        i % 2 === 1 ? <strong key={i}>{part}</strong> : part
      )}
    </span>
  );
};

const TaskSuggestions = () => {
  const [suggestions, setSuggestions]   = useState([]);   // rule-based list
  const [adviceText, setAdviceText]     = useState('');   // AI raw text
  const [source, setSource]             = useState(null); // 'ai' | 'ai-fallback' | 'rules'
  const [loading, setLoading]           = useState(false);
  const [error, setError]               = useState(null);

  const fetchSuggestions = useCallback(async () => {
    setLoading(true);
    setError(null);

    // ── 1. Try the AI model chain first ────────────────────────────────
    try {
      const aiRes  = await fetch(`${API_BASE}/api/nlp/ai/auto-advice?minutes=10`);
      const aiData = await aiRes.json();
      console.log('AI advice response:', aiData);

      // No detection data yet — stop here, don't call fallback either
      if (aiData.no_data) {
        setSuggestions([]);
        setAdviceText('');
        setSource(null);
        setLoading(false);
        return;
      }

      if (
        aiData.success &&
        aiData.data?.ai_model_available &&
        aiData.data?.advice
      ) {
        setAdviceText(aiData.data.advice);
        setSuggestions([]);
        setSource('ai');
        setLoading(false);
        return;
      }
      // AI returned but flagged as unavailable — still use its fallback text
      if (aiData.success && aiData.data?.advice) {
        setAdviceText(aiData.data.advice);
        setSuggestions([]);
        setSource('ai-fallback');
        setLoading(false);
        return;
      }
    } catch (aiErr) {
      console.warn('AI model chain unavailable, falling back to rule-based:', aiErr);
    }

    // ── 2. Fall back to rule-based suggestions ──────────────────────────
    try {
      const rulesRes  = await fetch(`${API_BASE}/api/nlp/suggestions?minutes=10`);
      const rulesData = await rulesRes.json();
      console.log('Rule-based suggestions:', rulesData);

      if (rulesData.success && rulesData.data) {
        setSuggestions(rulesData.data.suggestions || []);
        setAdviceText('');
        setSource('rules');
      } else {
        setSuggestions([]);
      }
    } catch (rulesErr) {
      console.error('Error fetching rule-based suggestions:', rulesErr);
      setError('Failed to load suggestions');
    } finally {
      setLoading(false);
    }
  }, []);

  // Suggestions are only fetched on explicit button click — no auto-fetch.

  // ── Source badge ──────────────────────────────────────────────────────
  const sourceBadge = () => {

    if (source === 'rules')
      return (
        <span style={{
          fontSize: '0.75rem', background: '#10b981', color: '#fff',
          borderRadius: '12px', padding: '2px 10px', marginLeft: '10px'
        }}>
          Rule-Based Suggestions
        </span>
      );
    if (source === 'ai')
      return (
        <span style={{
          fontSize: '0.75rem', background: '#6366f1', color: '#fff',
          borderRadius: '12px', padding: '2px 10px', marginLeft: '10px'
        }}>
          AI Model Chain
        </span>
      );
    if (source === 'ai-fallback')
      return (
        <span style={{
          fontSize: '0.75rem', background: '#d97706', color: '#fff',
          borderRadius: '12px', padding: '2px 10px', marginLeft: '10px'
        }}>
          AI Fallback
        </span>
      );
    return null;
  };

  return (
    <div className="card full-width">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h2 style={{ margin: 0 }}>
          Smart Task Suggestions
          {sourceBadge()}
        </h2>
        <button onClick={fetchSuggestions} disabled={loading} className="success">
          {loading ? 'Generating...' : 'Get Suggestions'}
        </button>
      </div>

      <div id="taskSuggestions">
        {error && <p style={{ color: '#f56565' }}>{error}</p>}
        {loading && <p>Loading suggestions...</p>}

        {/* AI model chain / fallback — formatted text */}
        {!loading && (source === 'ai' || source === 'ai-fallback') && adviceText && (
          <div className="ai-advice">
            {adviceText.split('\n').filter(l => l.trim()).map((line, idx) => (
              <p key={idx} style={{ margin: '4px 0' }}>
                {renderLine(line, idx)}
              </p>
            ))}
          </div>
        )}

        {/* Rule-based — bullet list */}
        {!loading && source === 'rules' && suggestions.length > 0 && (
          <ul className="suggestions-list">
            {suggestions.map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        )}

        {!loading && !adviceText && suggestions.length === 0 && !error && (
          <p>Click <strong>Get Suggestions</strong> to generate personalised recommendations based on your current detection data.</p>
        )}
      </div>
    </div>
  );
};

export default TaskSuggestions;
