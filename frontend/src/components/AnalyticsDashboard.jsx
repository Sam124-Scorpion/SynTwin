import { useState } from 'react';
import { API_BASE } from '../config';
import './AnalyticsDashboard.css';

const AnalyticsDashboard = () => {
  const [result, setResult] = useState('Click a button to load analytics');
  const [loading, setLoading] = useState(false);

  const getAnalytics = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/analytics/summary`);
      const data = await response.json();
      
      if (data.success) {
        setResult(JSON.stringify(data.data, null, 2));
      } else {
        setResult(data.message || 'No data available');
      }
    } catch (error) {
      setResult(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getRecentDetections = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/detection/recent?limit=10`);
      const data = await response.json();
      
      if (data.success) {
        setResult(`Recent ${data.count} Detections:\n\n${JSON.stringify(data.data, null, 2)}`);
      } else {
        setResult('No data available');
      }
    } catch (error) {
      setResult(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getStats = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/detection/stats`);
      const data = await response.json();
      
      if (data.success) {
        const stats = data.data;
        const statsDisplay = `
Total Detections: ${stats.total_detections}
Average Sentiment: ${stats.average_sentiment}

${JSON.stringify(stats, null, 2)}`;
        setResult(statsDisplay);
      } else {
        setResult('No data available');
      }
    } catch (error) {
      setResult(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const clearAllData = async () => {
    if (!window.confirm('⚠️ This will permanently delete ALL detection history and analytics data. Are you sure?')) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/detection/clear`, {
        method: 'DELETE'
      });
      const data = await response.json();
      
      if (data.success) {
        setResult('✓ All data has been cleared successfully');
        // Also clear analytics logs
        try {
          await fetch(`${API_BASE}/api/analytics/clear-logs`, {
            method: 'DELETE'
          });
        } catch (err) {
          console.error('Failed to clear analytics logs:', err);
        }
      } else {
        setResult(`Failed to clear data: ${data.message}`);
      }
    } catch (error) {
      setResult(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const downloadExcelReport = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/analytics/export-excel`);
      
      if (response.ok) {
        // Get filename from Content-Disposition header or use default
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `syntwin_report_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.xlsx`;
        
        if (contentDisposition) {
          const match = contentDisposition.match(/filename="?(.+?)"?$/i);
          if (match) filename = match[1];
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        setTimeout(() => {
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
        }, 100);
        
        setResult(`✓ Excel report downloaded: ${filename}`);
      } else {
        const errorText = await response.text();
        setResult(`Failed to generate report: ${errorText}`);
      }
    } catch (error) {
      console.error('Download error:', error);
      setResult(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card full-width">
      <h2>Analytics Dashboard</h2>
      <div className="control-panel">
        <button onClick={getAnalytics} disabled={loading}>
          Summary
        </button>
        <button onClick={getRecentDetections} disabled={loading}>
          Recent Data
        </button>
        <button onClick={getStats} disabled={loading}>
          Statistics
        </button>
        <button onClick={downloadExcelReport} disabled={loading} className="success">
          Download Excel Report
        </button>
        <button onClick={clearAllData} disabled={loading} className="danger" style={{ marginLeft: 'auto' }}>
          Clear All History
        </button>
      </div>
      <div className="analytics-result">
        {loading ? 'Loading...' : <pre>{result}</pre>}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
