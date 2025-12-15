import { useState, useEffect, useCallback } from 'react';
import './App.css';
import Header from './components/Header';
import ServerStatus from './components/ServerStatus';
import DetectionControl from './components/DetectionControl';
import VideoFeed from './components/VideoFeed';
import DetectionInfo from './components/DetectionInfo';
import TaskSuggestions from './components/TaskSuggestions';
import StateAnalysis from './components/StateAnalysis';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import Charts from './components/Charts';
import useWebSocket from './hooks/useWebSocket';
import { API_BASE } from './config';

function App() {
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectionData, setDetectionData] = useState(null);
  const [serverOnline, setServerOnline] = useState(false);
  const [shouldReconnect, setShouldReconnect] = useState(true);

  const handleStartDetection = useCallback(() => {
    setIsDetecting(true);
    setShouldReconnect(true);
  }, []);

  const handleStopDetection = useCallback(() => {
    setShouldReconnect(false); // Disable reconnection first
    setIsDetecting(false);
    setDetectionData(null);
  }, []);

  const { connect, disconnect, sendMessage } = useWebSocket({
    onMessage: (data) => {
      if (data.type === 'detection') {
        setDetectionData(data.data);
      } else if (data.type === 'error') {
        console.error('Detection error:', data.message);
      } else if (data.type === 'keepalive') {
        console.log('Received keepalive from server');
      }
    },
    onClose: (event) => {
      // Only reconnect if connection was lost unexpectedly (not user-initiated stop)
      if (shouldReconnect && event.code !== 1000) {
        console.log('Connection lost, reconnecting in 1 second...');
        setTimeout(() => {
          setIsDetecting(prev => {
            if (prev) {
              connect();
            }
            return prev;
          });
        }, 1000);
      }
    }
  });

  // Connect/disconnect based on isDetecting
  useEffect(() => {
    if (isDetecting) {
      connect();
    } else {
      sendMessage({ action: 'stop' });
      disconnect();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isDetecting]);

  // Check server status
  useEffect(() => {
    const checkStatus = async () => {
      try {
        await fetch(`${API_BASE}/api/health`);
        setServerOnline(true);
      } catch {
        setServerOnline(false);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 's' || event.key === 'S') {
        if (!isDetecting) {
          handleStartDetection();
        }
      }
      if (event.key === 'q' || event.key === 'Q' || event.key === 'Escape') {
        if (isDetecting) {
          handleStopDetection();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isDetecting, handleStartDetection, handleStopDetection]);

  return (
    <div className="app">
      <div className="container">
        <Header />
        
        <ServerStatus online={serverOnline} />
        
        <DetectionControl
          isDetecting={isDetecting}
          onStart={handleStartDetection}
          onStop={handleStopDetection}
          disabled={!serverOnline}
        />

        <div className="grid">
          <VideoFeed
            isDetecting={isDetecting}
            frameData={detectionData?.frame}
          />

          <DetectionInfo
            results={detectionData?.results}
            sentiment={detectionData?.sentiment}
          />

          <TaskSuggestions isDetecting={isDetecting} />

          <StateAnalysis isDetecting={isDetecting} />

          <AnalyticsDashboard />

          <Charts isDetecting={isDetecting} />
        </div>
      </div>
    </div>
  );
}

export default App;
