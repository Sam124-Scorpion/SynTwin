import './DetectionControl.css';

const DetectionControl = ({ isDetecting, onStart, onStop, disabled }) => {
  return (
    <div className="card">
      <h2>Detection Control</h2>
      <div id="detectionStatus">
        {isDetecting ? (
          <span className="status detecting">Detecting...</span>
        ) : (
          <span className="status offline">Not Running</span>
        )}
      </div>
      <div style={{ marginTop: '15px' }}>
        <button
          onClick={onStart}
          disabled={isDetecting || disabled}
          className="success"
        >
          Start Detection
        </button>
        <button
          onClick={onStop}
          disabled={!isDetecting}
          className="danger"
        >
          Stop Detection
        </button>
      </div>
      <p style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
        Shortcuts: <kbd>S</kbd> = Start | <kbd>Q</kbd>/<kbd>Esc</kbd> = Stop
      </p>
    </div>
  );
};

export default DetectionControl;
