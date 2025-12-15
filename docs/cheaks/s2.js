
        const API_BASE = 'http://localhost:8000';
        let ws = null;
        let isDetecting = false;
        let suggestionInterval = null;

        // Check server status
        async function checkServerStatus() {
            const statusDiv = document.getElementById('serverStatus');
            try {
                const response = await fetch(`${API_BASE}/api/health`);
                const data = await response.json();
                statusDiv.innerHTML = '<span class="status online"> Server Online & Ready</span>';
            } catch (error) {
                statusDiv.innerHTML = '<span class="status offline"> Server Offline</span><br><small>Run: python start_api_server.py</small>';
            }
        }

        // Start detection
        async function startDetection() {
            const startBtn = document.getElementById('startDetection');
            const stopBtn = document.getElementById('stopDetection');
            const statusDiv = document.getElementById('detectionStatus');
            const videoFeed = document.getElementById('videoFeed');

            startBtn.disabled = true;
            stopBtn.disabled = false;
            statusDiv.innerHTML = '<span class="status detecting"> Detecting...</span>';
            videoFeed.style.display = 'block';

            // Connect WebSocket
            ws = new WebSocket('ws://localhost:8000/api/stream/ws');

            ws.onopen = () => {
                console.log('WebSocket connected');
                ws.send(JSON.stringify({ action: 'start' }));
                isDetecting = true;

                // Load initial charts
                loadCharts();

                // Start chart auto-updates
                startChartUpdates();

                // Auto-refresh suggestions every 15 seconds
                suggestionInterval = setInterval(() => {
                    getTaskSuggestions();
                }, 15000);
            };

            function handleWebSocketMessage(event) {
                const data = JSON.parse(event.data);

                if (data.type === 'detection') {
                    // Update video feed
                    videoFeed.src = 'data:image/jpeg;base64,' + data.data.frame;

                    // Update detection info with fallback values
                    const results = data.data.results;
                    document.getElementById('emotionDisplay').textContent = results.emotion || 'N/A';
                    document.getElementById('postureDisplay').textContent = results.posture || 'N/A';
                    document.getElementById('eyesDisplay').textContent = results.eyes || 'N/A';

                    // Handle sentiment score safely
                    const sentimentScore = data.data.sentiment && data.data.sentiment.score !== undefined
                        ? data.data.sentiment.score.toFixed(2)
                        : '0.00';
                    document.getElementById('sentimentDisplay').textContent = sentimentScore;
                } else if (data.type === 'error') {
                    console.error('Detection error:', data.message);
                    // Don't stop on errors - let backend handle it
                } else if (data.type === 'keepalive') {
                    // Server keepalive - connection is healthy
                    console.log('Received keepalive from server');
                }
            }

            function handleWebSocketError(error) {
                console.error('WebSocket error:', error);
                const statusDiv = document.getElementById('detectionStatus');
                statusDiv.innerHTML = '<span class="status offline">⚠️ Connection Issue</span>';
            }

            ws.onmessage = handleWebSocketMessage;
            ws.onerror = handleWebSocketError;

            ws.onclose = (event) => {
                console.log('WebSocket closed', event.code, event.reason);

                // Only auto-reconnect if user didn't click stop
                // Code 1000 = normal closure (user clicked stop)
                // Code 1006 = abnormal closure (connection lost)
                if (isDetecting && event.code !== 1000) {
                    console.log('Connection lost, reconnecting in 1 second...');
                    const statusDiv = document.getElementById('detectionStatus');
                    statusDiv.innerHTML = '<span class="status detecting"> Reconnecting...</span>';

                    // Auto-reconnect after 1 second
                    setTimeout(() => {
                        if (isDetecting) {  // Check if user didn't click stop in the meantime
                            console.log('Attempting reconnection...');
                            startDetection();
                        }
                    }, 1000);
                }
            };
        }

        // Stop detection
        function stopDetection() {
            const startBtn = document.getElementById('startDetection');
            const stopBtn = document.getElementById('stopDetection');
            const statusDiv = document.getElementById('detectionStatus');
            const videoFeed = document.getElementById('videoFeed');

            // Send stop command if WebSocket is open
            if (ws && ws.readyState === WebSocket.OPEN) {
                try {
                    ws.send(JSON.stringify({ action: 'stop' }));
                } catch (error) {
                    console.error('Error sending stop command:', error);
                }
            }

            // Close WebSocket connection
            if (ws) {
                try {
                    ws.close();
                } catch (error) {
                    console.error('Error closing WebSocket:', error);
                }
                ws = null;
            }

            // Clear interval
            if (suggestionInterval) {
                clearInterval(suggestionInterval);
                suggestionInterval = null;
            }

            // Stop chart updates and load final data
            stopChartUpdates();
            setTimeout(() => {
                loadCharts(); // Final chart update
            }, 500);

            // Update UI
            isDetecting = false;
            startBtn.disabled = false;
            stopBtn.disabled = true;
            statusDiv.innerHTML = '<span class="status offline">Not Running</span>';
            videoFeed.style.display = 'none';
            videoFeed.src = '';

            // Reset detection info
            document.getElementById('emotionDisplay').textContent = '-';
            document.getElementById('postureDisplay').textContent = '-';
            document.getElementById('eyesDisplay').textContent = '-';
            document.getElementById('sentimentDisplay').textContent = '-';

            // Get final suggestions
            setTimeout(() => {
                getTaskSuggestions();
            }, 500);
        }

        // Get task suggestions
        async function getTaskSuggestions() {
            const resultDiv = document.getElementById('suggestions');
            resultDiv.innerHTML = '<em>Loading...</em>';

            try {
                const response = await fetch(`${API_BASE}/api/nlp/suggestions?minutes=10`);
                const data = await response.json();

                if (data.success && data.data.suggestions.length > 0) {
                    const suggestions = data.data.suggestions;
                    const priority = data.data.priority;
                    const context = data.data.recommendation_context;

                    let html = `<strong>Priority: <span style="color: ${priority === 'high' ? '#f56565' : priority === 'medium' ? '#ed8936' : '#48bb78'}">${priority.toUpperCase()}</span></strong><br>`;
                    html += `<em>${context}</em><br><br>`;
                    html += '<ul class="suggestions-list">';

                    suggestions.forEach(sug => {
                        html += `<li class="priority-${priority}">${sug}</li>`;
                    });

                    html += '</ul>';
                    resultDiv.innerHTML = html;
                } else {
                    resultDiv.innerHTML = `<em>No data yet. Start detection to collect data and get personalized suggestions!</em>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<em>Error: ${error.message}</em>`;
            }
        }

        // Get current state
        async function getCurrentState() {
            const resultDiv = document.getElementById('currentState');
            resultDiv.innerHTML = '<em>Loading...</em>';

            try {
                const response = await fetch(`${API_BASE}/api/nlp/state?minutes=10`);
                const data = await response.json();

                if (data.success && data.data.data_points > 0) {
                    const state = data.data;
                    resultDiv.innerHTML = `
                        <strong>State Analysis:</strong><br><br>
                        <div class="stats-grid">
                            <div style="background: #f0f4ff; padding: 10px; border-radius: 5px;">
                                <strong>${state.dominant_emotion}</strong><br>
                                <small>Dominant Emotion</small>
                            </div>
                            <div style="background: #f0f4ff; padding: 10px; border-radius: 5px;">
                                <strong>${state.energy_level}</strong><br>
                                <small>Energy Level</small>
                            </div>
                            <div style="background: #f0f4ff; padding: 10px; border-radius: 5px;">
                                <strong>${state.avg_sentiment}</strong><br>
                                <small>Avg Sentiment</small>
                            </div>
                            <div style="background: #f0f4ff; padding: 10px; border-radius: 5px;">
                                <strong>${state.data_points}</strong><br>
                                <small>Data Points</small>
                            </div>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = '<em>No data available yet</em>';
                }
            } catch (error) {
                resultDiv.innerHTML = `<em>Error: ${error.message}</em>`;
            }
        }

        // Get analytics
        async function getAnalytics() {
            const resultDiv = document.getElementById('analytics');
            resultDiv.innerHTML = '<em>Loading...</em>';

            try {
                const response = await fetch(`${API_BASE}/api/analytics/summary`);
                const data = await response.json();

                if (data.success) {
                    resultDiv.innerHTML = `<pre>${JSON.stringify(data.data, null, 2)}</pre>`;
                } else {
                    resultDiv.innerHTML = data.message || '<em>No data available</em>';
                }
            } catch (error) {
                resultDiv.innerHTML = `<em>Error: ${error.message}</em>`;
            }
        }

        // Get recent detections
        async function getRecentDetections() {
            const resultDiv = document.getElementById('analytics');
            resultDiv.innerHTML = '<em>Loading...</em>';

            try {
                const response = await fetch(`${API_BASE}/api/detection/recent?limit=10`);
                const data = await response.json();

                if (data.success) {
                    resultDiv.innerHTML = `<strong>Recent ${data.count} Detections:</strong><pre>${JSON.stringify(data.data, null, 2)}</pre>`;
                } else {
                    resultDiv.innerHTML = '<em>No data available</em>';
                }
            } catch (error) {
                resultDiv.innerHTML = `<em>Error: ${error.message}</em>`;
            }
        }

        // Get statistics
        async function getStats() {
            const resultDiv = document.getElementById('analytics');
            resultDiv.innerHTML = '<em>Loading...</em>';

            try {
                const response = await fetch(`${API_BASE}/api/detection/stats`);
                const data = await response.json();

                if (data.success) {
                    const stats = data.data;
                    resultDiv.innerHTML = `
                        <div class="stats-grid">
                            <div class="stat-box">
                                <h3>${stats.total_detections}</h3>
                                <p>Total Detections</p>
                            </div>
                            <div class="stat-box">
                                <h3>${stats.average_sentiment}</h3>
                                <p>Avg Sentiment</p>
                            </div>
                        </div>
                        <pre style="margin-top: 15px;">${JSON.stringify(stats, null, 2)}</pre>
                    `;
                } else {
                    resultDiv.innerHTML = '<em>No data available</em>';
                }
            } catch (error) {
                resultDiv.innerHTML = `<em>Error: ${error.message}</em>`;
            }
        }

        // Clear all detection history
        async function clearAllData() {
            // Confirmation dialog
            const confirmation = confirm(
                '⚠️ WARNING: This will permanently delete ALL detection history from the database!\n\n' +
                'This includes:\n' +
                '- All detection records\n' +
                '- Emotion and posture data\n' +
                '- Sentiment history\n' +
                '- Analytics data\n\n' +
                'This action CANNOT be undone!\n\n' +
                'Are you sure you want to continue?'
            );

            if (!confirmation) {
                return;
            }

            // Second confirmation for safety
            const secondConfirmation = confirm(
                '🚨 FINAL CONFIRMATION\n\n' +
                'Type confirmation: Are you ABSOLUTELY SURE?\n\n' +
                'Click OK to permanently delete all data.'
            );

            if (!secondConfirmation) {
                return;
            }

            const resultDiv = document.getElementById('analytics');
            resultDiv.innerHTML = '<em>Clearing all data...</em>';

            try {
                const response = await fetch(`${API_BASE}/api/detection/clear`, {
                    method: 'DELETE'
                });
                const data = await response.json();

                if (data.success) {
                    resultDiv.innerHTML = `
                        <div style="background: #48bb78; color: white; padding: 20px; border-radius: 8px; text-align: center;">
                            <h3 style="margin: 0 0 10px 0;">✅ Success!</h3>
                            <p style="margin: 0;">${data.message}</p>
                            <p style="margin: 10px 0 0 0; font-size: 0.9em;">Database cleared. All charts and statistics have been reset.</p>
                        </div>
                    `;

                    // Refresh charts to show empty state
                    setTimeout(() => {
                        loadCharts();
                    }, 2000);

                    // Clear current state display
                    document.getElementById('emotionDisplay').textContent = '--';
                    document.getElementById('postureDisplay').textContent = '--';
                    document.getElementById('eyesDisplay').textContent = '--';
                    document.getElementById('sentimentDisplay').textContent = '--';

                    // Clear AI suggestions display
                    document.getElementById('suggestions').innerHTML = '<em>No data yet. Start detection to collect data and get personalized suggestions!</em>';

                    // Clear current state display
                    document.getElementById('currentState').innerHTML = '<em>No data available yet</em>';

                    alert('✅ Database cleared successfully!\n\nStart detection again to collect new data.');
                } else {
                    resultDiv.innerHTML = `
                        <div style="background: #f56565; color: white; padding: 20px; border-radius: 8px;">
                            <h3 style="margin: 0 0 10px 0;">❌ Error</h3>
                            <p style="margin: 0;">${data.message || 'Failed to clear data'}</p>
                        </div>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `
                    <div style="background: #f56565; color: white; padding: 20px; border-radius: 8px;">
                        <h3 style="margin: 0 0 10px 0;">❌ Error</h3>
                        <p style="margin: 0;">Failed to clear data: ${error.message}</p>
                    </div>
                `;
            }
        }

        // Chart instances
        let emotionChart = null;
        let postureChart = null;
        let sentimentChart = null;
        let timelineChart = null;

        // Load all charts
        async function loadCharts() {
            await Promise.all([
                createEmotionChart(),
                createPostureChart(),
                createSentimentChart(),
                createTimelineChart()
            ]);
        }

        // Create Emotion Distribution Chart
        async function createEmotionChart() {
            try {
                const response = await fetch(`${API_BASE}/api/detection/stats`);
                const data = await response.json();

                if (!data.success || !data.data.emotion_distribution) {
                    return;
                }

                const emotions = data.data.emotion_distribution;
                const labels = Object.keys(emotions);
                const values = Object.values(emotions);

                const ctx = document.getElementById('emotionChart').getContext('2d');

                if (emotionChart) {
                    emotionChart.destroy();
                }

                emotionChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: [
                                '#48bb78',
                                '#f56565',
                                '#4299e1',
                                '#ed8936',
                                '#9f7aea',
                                '#ecc94b'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    boxWidth: 15,
                                    padding: 10,
                                    font: {
                                        size: window.innerWidth < 768 ? 10 : 12
                                    }
                                }
                            },
                            title: {
                                display: false
                            },
                            tooltip: {
                                enabled: true,
                                callbacks: {
                                    label: function (context) {
                                        let label = context.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        label += context.parsed + ' detections';
                                        return label;
                                    }
                                }
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Error creating emotion chart:', error);
            }
        }

        // Create Posture Analysis Chart
        async function createPostureChart() {
            try {
                const response = await fetch(`${API_BASE}/api/detection/stats`);
                const data = await response.json();

                if (!data.success || !data.data.posture_distribution) {
                    return;
                }

                const postures = data.data.posture_distribution;
                const labels = Object.keys(postures);
                const values = Object.values(postures);

                const ctx = document.getElementById('postureChart').getContext('2d');

                if (postureChart) {
                    postureChart.destroy();
                }

                postureChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Posture Count',
                            data: values,
                            backgroundColor: '#667eea',
                            borderColor: '#5568d3',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                enabled: true
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    font: {
                                        size: window.innerWidth < 768 ? 10 : 12
                                    }
                                }
                            },
                            x: {
                                ticks: {
                                    font: {
                                        size: window.innerWidth < 768 ? 10 : 12
                                    }
                                }
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Error creating posture chart:', error);
            }
        }

        // Create Sentiment Trend Chart
        async function createSentimentChart() {
            try {
                const response = await fetch(`${API_BASE}/api/detection/timeline?hours=2`);
                const data = await response.json();

                if (!data.success || !data.data || data.data.length === 0) {
                    return;
                }

                const timeline = data.data;
                const labels = timeline.map(item => {
                    const time = new Date(item.timestamp);
                    return time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
                });
                const sentiments = timeline.map(item => item.sentiment || 0);

                const ctx = document.getElementById('sentimentChart').getContext('2d');

                if (sentimentChart) {
                    sentimentChart.destroy();
                }

                sentimentChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Sentiment Score',
                            data: sentiments,
                            borderColor: '#48bb78',
                            backgroundColor: 'rgba(72, 187, 120, 0.1)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top',
                                labels: {
                                    boxWidth: 15,
                                    padding: 10,
                                    font: {
                                        size: window.innerWidth < 768 ? 10 : 12
                                    }
                                }
                            },
                            tooltip: {
                                enabled: true
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: false,
                                ticks: {
                                    font: {
                                        size: window.innerWidth < 768 ? 10 : 12
                                    }
                                }
                            },
                            x: {
                                ticks: {
                                    font: {
                                        size: window.innerWidth < 768 ? 9 : 11
                                    },
                                    maxRotation: 45,
                                    minRotation: 0
                                }
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Error creating sentiment chart:', error);
            }
        }

        // Create Timeline Chart
        async function createTimelineChart() {
            try {
                const response = await fetch(`${API_BASE}/api/analytics/emotion-trends?hours=24`);
                const data = await response.json();

                const ctx = document.getElementById('timelineChart').getContext('2d');

                if (timelineChart) {
                    timelineChart.destroy();
                }

                // Default empty chart if no data
                let labels = ['No data yet'];
                let counts = [0];

                if (data.success && data.data && data.data.length > 0) {
                    const trends = data.data;
                    labels = trends.map(item => {
                        const time = new Date(item.hour);
                        return time.toLocaleString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit'
                        });
                    });
                    counts = trends.map(item => item.total_detections);
                }

                timelineChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Detections per Hour',
                            data: counts,
                            borderColor: '#764ba2',
                            backgroundColor: 'rgba(118, 75, 162, 0.1)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top',
                                labels: {
                                    boxWidth: 15,
                                    padding: 10,
                                    font: {
                                        size: window.innerWidth < 768 ? 10 : 12
                                    }
                                }
                            },
                            tooltip: {
                                enabled: true
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    font: {
                                        size: window.innerWidth < 768 ? 10 : 12
                                    }
                                }
                            },
                            x: {
                                ticks: {
                                    font: {
                                        size: window.innerWidth < 768 ? 8 : 10
                                    },
                                    maxRotation: 45,
                                    minRotation: 0
                                }
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Error creating timeline chart:', error);
            }
        }

        // Auto-update charts during detection
        let chartUpdateInterval = null;

        function startChartUpdates() {
            chartUpdateInterval = setInterval(() => {
                if (isDetecting) {
                    loadCharts();
                }
            }, 30000); // Update every 30 seconds
        }

        function stopChartUpdates() {
            if (chartUpdateInterval) {
                clearInterval(chartUpdateInterval);
                chartUpdateInterval = null;
            }
        }

        // Handle window resize to update charts
        let resizeTimeout;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function () {
                // Redraw charts with new dimensions
                if (emotionChart || postureChart || sentimentChart || timelineChart) {
                    loadCharts();
                }
            }, 250); // Debounce resize events
        });

        // Check server status on load
        checkServerStatus();

        // Auto-refresh status every 5 seconds
        setInterval(checkServerStatus, 5000);

        // Add keyboard shortcuts
        document.addEventListener('keydown', function (event) {
            // Press 'S' to start detection
            if (event.key === 's' || event.key === 'S') {
                const startBtn = document.getElementById('startDetection');
                if (!startBtn.disabled) {
                    startDetection();
                }
            }
            // Press 'Q' or 'Esc' to stop detection
            if (event.key === 'q' || event.key === 'Q' || event.key === 'Escape') {
                if (isDetecting) {
                    stopDetection();
                }
            }
        });

        // Handle page unload - just close WebSocket cleanly, don't stop detection
        // This allows detection to continue if page is accidentally closed or refreshed
        window.addEventListener('beforeunload', function (event) {
            if (ws && ws.readyState === WebSocket.OPEN) {
                // Just close the connection, don't send stop command
                ws.close();
            }
        });

        console.log('SynTwin Dashboard Loaded!');
        console.log('Keyboard shortcuts: S = Start, Q/Esc = Stop');
  