import './DetectionInfo.css';

const DetectionInfo = ({ results, sentiment }) => {
  return (
    <div className="card">
      <h2>Detection Results</h2>
      <div className="info-grid">
        <div className="info-item">
          <span className="info-label">Emotion:</span>
          <span className="info-value" id="emotionDisplay">
            {results?.emotion || '-'}
          </span>
        </div>
        <div className="info-item">
          <span className="info-label">Posture:</span>
          <span className="info-value" id="postureDisplay">
            {results?.posture || '-'}
          </span>
        </div>
        <div className="info-item">
          <span className="info-label">Eyes:</span>
          <span className="info-value" id="eyesDisplay">
            {results?.eyes || '-'}
          </span>
        </div>
        <div className="info-item">
          <span className="info-label">Sentiment Score:</span>
          <span className="info-value" id="sentimentDisplay">
            {sentiment?.score !== undefined ? sentiment.score.toFixed(2) : '-'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default DetectionInfo;
