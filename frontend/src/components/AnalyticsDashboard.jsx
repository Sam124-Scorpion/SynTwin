import { useState } from 'react';
import { API_BASE } from '../config';
import './AnalyticsDashboard.css';

// ── helpers ──────────────────────────────────────────────────────────────────
const EMOTION_ICONS = { Happy: '😊', Neutral: '😐', Drowsy: '😴' };
const POSTURE_ICONS = { Straight: '🧍', Slouching: '🪑', 'Leaning Sideways': '↔️', 'Leaning Back': '↩️', 'Slouching Forward': '🫱', 'Looking Down': '⬇️' };
const SENTIMENT_COLOR = (v) => v > 0.3 ? '#10b981' : v < -0.3 ? '#ef4444' : '#f59e0b';

const DistBar = ({ label, value, max, icon }) => {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div className="dist-row">
      <span className="dist-label">{icon} {label}</span>
      <div className="dist-track">
        <div className="dist-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="dist-count">{value}</span>
    </div>
  );
};

const MetricCard = ({ label, value, sub, color }) => (
  <div className="metric-card" style={{ borderTopColor: color || '#6366f1' }}>
    <div className="metric-value" style={{ color: color || '#a5b4fc' }}>{value}</div>
    <div className="metric-label">{label}</div>
    {sub && <div className="metric-sub">{sub}</div>}
  </div>
);

// ── view renderers ────────────────────────────────────────────────────────────
const SummaryView = ({ d }) => {
  const emo = d.emotion_distribution || {};
  const pos = d.posture_distribution || {};
  const maxEmo = Math.max(...Object.values(emo), 1);
  const maxPos = Math.max(...Object.values(pos), 1);
  return (
    <div>
      <div className="metrics-row">
        <MetricCard label="Total Entries" value={d.total_entries} color="#6366f1" />
        <MetricCard label="Avg Sentiment" value={d.average_sentiment} color={SENTIMENT_COLOR(d.average_sentiment)} />
        <MetricCard label="Sentiment Trend" value={d.sentiment_trend}
          color={d.sentiment_trend === 'Positive' ? '#10b981' : d.sentiment_trend === 'Negative' ? '#ef4444' : '#f59e0b'} />
      </div>
      <div className="dist-section">
        <h4>Emotion Distribution</h4>
        {Object.entries(emo).map(([k, v]) =>
          <DistBar key={k} label={k} value={v} max={maxEmo} icon={EMOTION_ICONS[k] || '🎭'} />)}
      </div>
      <div className="dist-section">
        <h4>Posture Distribution</h4>
        {Object.entries(pos).map(([k, v]) =>
          <DistBar key={k} label={k} value={v} max={maxPos} icon={POSTURE_ICONS[k] || '🪑'} />)}
      </div>
    </div>
  );
};

const RecentView = ({ rows }) => (
  <div className="table-wrap">
    <table className="det-table">
      <thead>
        <tr>
          <th>#</th><th>Time</th><th>Emotion</th><th>Eyes</th><th>Smile</th><th>Posture</th><th>Sentiment</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={i}>
            <td className="td-num">{i + 1}</td>
            <td className="td-time">{r.timestamp ? String(r.timestamp).slice(0, 19).replace('T', ' ') : '—'}</td>
            <td><span className="badge-emotion">{EMOTION_ICONS[r.emotion] || '🎭'} {r.emotion}</span></td>
            <td>{r.eyes || '—'}</td>
            <td>{r.smile || '—'}</td>
            <td>{r.posture || '—'}</td>
            <td style={{ color: SENTIMENT_COLOR(r.sentiment) }}>
              {r.sentiment !== undefined && r.sentiment !== null ? Number(r.sentiment).toFixed(2) : '—'}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const StatsView = ({ d }) => {
  const emo = d.emotion_distribution || d.emotion_counts || {};
  const pos = d.posture_distribution || d.posture_counts || {};
  const maxEmo = Math.max(...Object.values(emo), 1);
  const maxPos = Math.max(...Object.values(pos), 1);
  return (
    <div>
      <div className="metrics-row">
        <MetricCard label="Total Detections" value={d.total_detections} color="#6366f1" />
        <MetricCard label="Avg Sentiment" value={typeof d.average_sentiment === 'number' ? d.average_sentiment.toFixed(2) : d.average_sentiment}
          color={SENTIMENT_COLOR(d.average_sentiment)} />
      </div>
      <div className="dist-section">
        <h4>Emotion Breakdown</h4>
        {Object.entries(emo).map(([k, v]) =>
          <DistBar key={k} label={k} value={v} max={maxEmo} icon={EMOTION_ICONS[k] || '🎭'} />)}
      </div>
      <div className="dist-section">
        <h4>Posture Breakdown</h4>
        {Object.entries(pos).map(([k, v]) =>
          <DistBar key={k} label={k} value={v} max={maxPos} icon={POSTURE_ICONS[k] || '🪑'} />)}
      </div>
    </div>
  );
};

// ── main component ────────────────────────────────────────────────────────────
const AnalyticsDashboard = () => {
  const [view, setView]       = useState(null);   // 'summary' | 'recent' | 'stats'
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('Select a view below to load analytics.');

  const load = async (key, url, transform) => {
    setLoading(true);
    setData(null);
    setMessage('');
    setView(key);
    try {
      const res = await fetch(url);
      const json = await res.json();
      if (json.success) {
        setData(transform(json));
      } else {
        setMessage(json.message || 'No data available.');
      }
    } catch (e) {
      setMessage(`Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getAnalytics       = () => load('summary', `${API_BASE}/api/analytics/summary`,      j => j.data);
  const getRecentDetections = () => load('recent',  `${API_BASE}/api/detection/recent?limit=20`, j => j.data);
  const getStats           = () => load('stats',   `${API_BASE}/api/detection/stats`,         j => j.data);

  const clearAllData = async () => {
    if (!window.confirm('⚠️ This will permanently delete ALL detection history and analytics data. Are you sure?')) return;
    setLoading(true);
    try {
      const res  = await fetch(`${API_BASE}/api/detection/clear`, { method: 'DELETE' });
      const json = await res.json();
      setView(null); setData(null);
      setMessage(json.success ? '✓ All data cleared successfully.' : `Failed: ${json.message}`);
      try { await fetch(`${API_BASE}/api/analytics/clear-logs`, { method: 'DELETE' }); } catch (_) {}
    } catch (e) { setMessage(`Error: ${e.message}`); }
    finally { setLoading(false); }
  };

  const downloadExcelReport = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/analytics/export-excel`);
      if (response.ok) {
        const cd  = response.headers.get('Content-Disposition');
        let fname = `syntwin_report_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.xlsx`;
        if (cd) { const m = cd.match(/filename="?(.+?)"?$/i); if (m) fname = m[1]; }
        const blob = await response.blob();
        const url  = window.URL.createObjectURL(blob);
        const a    = document.createElement('a');
        a.href = url; a.download = fname;
        document.body.appendChild(a); a.click();
        setTimeout(() => { window.URL.revokeObjectURL(url); document.body.removeChild(a); }, 100);
        setMessage(`✓ Downloaded: ${fname}`);
      } else {
        setMessage(`Failed to generate report: ${await response.text()}`);
      }
    } catch (e) { setMessage(`Error: ${e.message}`); }
    finally { setLoading(false); }
  };

  return (
    <div className="card full-width ad-card">
      <h2>Analytics Dashboard</h2>

      {/* action bar */}
      <div className="control-panel">
        <button onClick={getAnalytics}        disabled={loading} className={view === 'summary' ? 'tab-active' : ''}>📊 Summary</button>
        <button onClick={getRecentDetections} disabled={loading} className={view === 'recent'  ? 'tab-active' : ''}>🕑 Recent Data</button>
        <button onClick={getStats}            disabled={loading} className={view === 'stats'   ? 'tab-active' : ''}>📈 Statistics</button>
        <button onClick={downloadExcelReport} disabled={loading} className="success">⬇ Excel Report</button>
        <button onClick={clearAllData}        disabled={loading} className="danger" style={{ marginLeft: 'auto' }}>🗑 Clear History</button>
      </div>

      {/* content area */}
      <div className="analytics-content">
        {loading && (
          <div className="ad-loading">
            <div className="ad-spinner" />
            <span>Loading…</span>
          </div>
        )}

        {!loading && message && <p className="ad-message">{message}</p>}

        {!loading && data && view === 'summary' && <SummaryView d={data} />}
        {!loading && data && view === 'recent'  && <RecentView  rows={Array.isArray(data) ? data : []} />}
        {!loading && data && view === 'stats'   && <StatsView   d={data} />}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
