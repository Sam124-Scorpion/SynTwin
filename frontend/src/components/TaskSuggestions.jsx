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

const TaskSuggestions = ({ isDetecting }) => {
  const [suggestions, setSuggestions]   = useState([]);   // rule-based list
  const [adviceText, setAdviceText]     = useState('');   // Gemini raw text
  const [source, setSource]             = useState(null); // 'gemini' | 'rules'
  const [loading, setLoading]           = useState(false);
  const [error, setError]               = useState(null);

  const fetchSuggestions = useCallback(async () => {
    setLoading(true);
    setError(null);

    // ── 1. Try Gemini AI first ──────────────────────────────────────────
    try {
      const geminiRes  = await fetch(`${API_BASE}/api/nlp/gemini/auto-advice?minutes=10`);
      const geminiData = await geminiRes.json();
      console.log('Gemini advice response:', geminiData);

      // No detection data yet — stop here, don't call fallback either
      if (geminiData.no_data) {
        setSuggestions([]);
        setAdviceText('');
        setSource(null);
        setLoading(false);
        return;
      }

      if (
        geminiData.success &&
        geminiData.data?.gemini_available &&
        geminiData.data?.advice
      ) {
        setAdviceText(geminiData.data.advice);
        setSuggestions([]);
        setSource('gemini');
        setLoading(false);
        return;
      }
      // Gemini returned but flagged as unavailable — still use its offline fallback text
      if (geminiData.success && geminiData.data?.advice) {
        setAdviceText(geminiData.data.advice);
        setSuggestions([]);
        setSource('gemini-fallback');
        setLoading(false);
        return;
      }
    } catch (geminiErr) {
      console.warn('Gemini unavailable, falling back to rule-based:', geminiErr);
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
    if (source === 'gemini')
      return (
        <span style={{
          fontSize: '0.75rem', background: '#6366f1', color: '#fff',
          borderRadius: '12px', padding: '2px 10px', marginLeft: '10px'
        }}>
         Gemini AI
        </span>
      );
    if (source === 'gemini-fallback')
      return (
        <span style={{
          fontSize: '0.75rem', background: '#d97706', color: '#fff',
          borderRadius: '12px', padding: '2px 10px', marginLeft: '10px'
        }}>
          ⚡ AI Offline Fallback
        </span>
      );
    if (source === 'rules')
      return (
        <span style={{
          fontSize: '0.75rem', background: '#10b981', color: '#fff',
          borderRadius: '12px', padding: '2px 10px', marginLeft: '10px'
        }}>
          📋 Smart Suggestions
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

        {/* Gemini AI / Offline-fallback — formatted text */}
        {!loading && (source === 'gemini' || source === 'gemini-fallback') && adviceText && (
          <div className="gemini-advice">
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
