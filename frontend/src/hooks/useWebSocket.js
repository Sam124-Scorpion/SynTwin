import { useRef, useCallback } from 'react';
import { WS_BASE } from '../config';

const useWebSocket = ({ onMessage, onClose, shouldAutoStart = false }) => {
  const wsRef = useRef(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    wsRef.current = new WebSocket(`${WS_BASE}/api/stream/ws`);

    wsRef.current.onopen = () => {
      console.log('WebSocket connected');
      if (shouldAutoStart) {
        wsRef.current.send(JSON.stringify({ action: 'start' }));
      }
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    wsRef.current.onclose = (event) => {
      console.log('WebSocket closed', event.code, event.reason);
      if (onClose) {
        onClose(event);
      }
    };
  }, [onMessage, onClose, shouldAutoStart]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendMessage = useCallback((message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  return {
    connect,
    disconnect,
    sendMessage
  };
};

export default useWebSocket;
