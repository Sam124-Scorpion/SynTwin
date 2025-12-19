import { useEffect, useRef, useState } from 'react';
import { API_BASE } from '../config';
import './Charts.css';

const Charts = ({ isDetecting }) => {
  const emotionCanvasRef = useRef(null);
  const postureCanvasRef = useRef(null);
  const sentimentCanvasRef = useRef(null);
  const timelineCanvasRef = useRef(null);

  const [charts, setCharts] = useState({
    emotion: null,
    posture: null,
    sentiment: null,
    timeline: null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadCharts = async () => {
    setLoading(true);
    setError(null);
    try {
      // Destroy existing charts first
      if (charts.emotion) {
        charts.emotion.destroy();
      }
      if (charts.posture) {
        charts.posture.destroy();
      }
      if (charts.sentiment) {
        charts.sentiment.destroy();
      }
      if (charts.timeline) {
        charts.timeline.destroy();
      }

      // Fetch data
      const [statsRes, trendsRes, timelineRes] = await Promise.all([
        fetch(`${API_BASE}/api/detection/stats`),
        fetch(`${API_BASE}/api/analytics/emotion-trends?hours=24`),
        fetch(`${API_BASE}/api/detection/timeline?hours=2`)
      ]);

      const statsData = await statsRes.json();
      const trendsData = await trendsRes.json();
      const timelineData = await timelineRes.json();

      console.log('Charts data loaded:', { statsData, trendsData, timelineData });

      // Extract data from API response
      const stats = statsData.success ? statsData.data : {};
    //   const trends = trendsData.success ? trendsData.data : [];
      const timeline = timelineData.success ? timelineData.data : [];

      // Create new charts
      const Chart = window.Chart;
      const newCharts = {};
      
      // Emotion Distribution
      if (emotionCanvasRef.current) {
        const emotionData = stats.emotion_distribution || {};
        newCharts.emotion = new Chart(emotionCanvasRef.current, {
          type: 'pie',
          data: {
            labels: Object.keys(emotionData),
            datasets: [{
              data: Object.values(emotionData),
              backgroundColor: [
                '#48bb78', '#f56565', '#ed8936', '#4299e1', '#9f7aea', '#ecc94b'
              ]
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom' }
            }
          }
        });
      }

      // Posture Distribution
      if (postureCanvasRef.current) {
        const postureData = stats.posture_distribution || {};
        newCharts.posture = new Chart(postureCanvasRef.current, {
          type: 'doughnut',
          data: {
            labels: Object.keys(postureData),
            datasets: [{
              data: Object.values(postureData),
              backgroundColor: ['#48bb78', '#f56565', '#ed8936', '#4299e1', '#9f7aea']
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom' }
            }
          }
        });
      }

      // Sentiment Trend (from detection/timeline API - showing sentiment over time)
      if (sentimentCanvasRef.current && Array.isArray(timeline) && timeline.length > 0) {
        // Sample data points for better visualization (take every 10th point if too many)
        const sampledTimeline = timeline.length > 100 
          ? timeline.filter((_, i) => i % Math.ceil(timeline.length / 100) === 0)
          : timeline;
        
        const sentimentLabels = sampledTimeline.map(t => {
          const time = new Date(t.timestamp);
          return time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        });
        const sentimentData = sampledTimeline.map(t => parseFloat(t.sentiment) || 0);
        
        newCharts.sentiment = new Chart(sentimentCanvasRef.current, {
          type: 'line',
          data: {
            labels: sentimentLabels,
            datasets: [{
              label: 'Sentiment Score',
              data: sentimentData,
              borderColor: '#667eea',
              backgroundColor: 'rgba(102, 126, 234, 0.1)',
              tension: 0.4,
              fill: true,
              pointRadius: 2,
              pointHoverRadius: 4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: false,
                min: -1,
                max: 1,
                ticks: {
                  callback: function(value) {
                    return value.toFixed(1);
                  }
                }
              }
            },
            plugins: {
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return 'Sentiment: ' + context.parsed.y.toFixed(2);
                  }
                }
              }
            }
          }
        });
      }

      // Activity Timeline (real-time detection activity)
      if (timelineCanvasRef.current && Array.isArray(timeline) && timeline.length > 0) {
        // Take last 50 detections for real-time view
        const recentData = timeline.slice(-50);
        
        const activityLabels = recentData.map(t => {
          const time = new Date(t.timestamp);
          return time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        });
        
        // Create emotion score mapping for visualization
        const emotionScores = recentData.map(t => {
          const emotion = t.emotion?.toLowerCase() || 'neutral';
          const scoreMap = {
            'happy': 1.0,
            'focused': 0.7,
            'neutral': 0.0,
            'sad': -0.5,
            'angry': -0.8,
            'drowsy': -0.3
          };
          return scoreMap[emotion] || 0;
        });
        
        const sentimentValues = recentData.map(t => parseFloat(t.sentiment) || 0);
        
        newCharts.timeline = new Chart(timelineCanvasRef.current, {
          type: 'line',
          data: {
            labels: activityLabels,
            datasets: [
              {
                label: 'Emotion Level',
                data: emotionScores,
                borderColor: '#764ba2',
                backgroundColor: 'rgba(118, 75, 162, 0.2)',
                tension: 0.4,
                fill: true,
                pointRadius: 2,
                pointHoverRadius: 5,
                yAxisID: 'y'
              },
              {
                label: 'Sentiment',
                data: sentimentValues,
                borderColor: '#48bb78',
                backgroundColor: 'rgba(72, 187, 120, 0.1)',
                tension: 0.4,
                fill: false,
                pointRadius: 2,
                pointHoverRadius: 5,
                borderDash: [5, 5],
                yAxisID: 'y'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
              mode: 'index',
              intersect: false
            },
            scales: {
              y: {
                type: 'linear',
                display: true,
                position: 'left',
                min: -1,
                max: 1,
                ticks: {
                  callback: function(value) {
                    return value.toFixed(1);
                  }
                },
                grid: {
                  color: 'rgba(0, 0, 0, 0.1)'
                }
              },
              x: {
                ticks: {
                  maxRotation: 45,
                  minRotation: 45,
                  maxTicksLimit: 10
                }
              }
            },
            plugins: {
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return context.dataset.label + ': ' + context.parsed.y.toFixed(2);
                  }
                }
              },
              legend: {
                display: true,
                position: 'top'
              }
            }
          }
        });
      } else if (timelineCanvasRef.current) {
        // Show placeholder chart if no data
        newCharts.timeline = new Chart(timelineCanvasRef.current, {
          type: 'line',
          data: {
            labels: ['Start detecting to see activity'],
            datasets: [{
              label: 'No Data',
              data: [0],
              borderColor: '#ccc',
              backgroundColor: 'rgba(200, 200, 200, 0.1)'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false
          }
        });
      }

      // Update all charts at once
      setCharts(newCharts);

    } catch (err) {
      console.error('Error loading charts:', err);
      setError('Failed to load charts. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Load charts immediately on mount
    loadCharts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (isDetecting) {
      // Refresh charts every 10 seconds during detection
      const interval = setInterval(loadCharts, 10000);
      return () => clearInterval(interval);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isDetecting]);

  useEffect(() => {
    return () => {
      Object.values(charts).forEach(chart => chart?.destroy());
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <div className="card full-width">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h2 style={{ margin: 0 }}>Visual Analytics Dashboard</h2>
          <button onClick={loadCharts} disabled={loading} className="success">
            {loading ? 'Refreshing...' : 'Refresh Charts'}
          </button>
        </div>
        {error && <div style={{ color: '#f56565', marginBottom: '10px' }}>{error}</div>}
      </div>

      <div className="charts-grid">
        <div className="card chart-card">
          <h2>Emotion Distribution</h2>
          {loading && <p>Loading...</p>}
          <canvas ref={emotionCanvasRef} id="emotionChart"></canvas>
        </div>

        <div className="card chart-card">
          <h2>Posture Analysis</h2>
          {loading && <p>Loading...</p>}
          <canvas ref={postureCanvasRef} id="postureChart"></canvas>
        </div>

        <div className="card chart-card">
          <h2>Sentiment Trend (24h)</h2>
          {loading && <p>Loading...</p>}
          <canvas ref={sentimentCanvasRef} id="sentimentChart"></canvas>
        </div>

        <div className="card chart-card">
          <h2>Activity Timeline (2h)</h2>
          {loading && <p>Loading...</p>}
          <canvas ref={timelineCanvasRef} id="timelineChart"></canvas>
        </div>
      </div>
    </>
  );
};

export default Charts;
