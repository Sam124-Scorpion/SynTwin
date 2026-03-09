import './DetectionInfo.css';

const DetectionInfo = ({ results, sentiment }) => {
  // Get lighting quality class for styling
  const getLightingClass = (quality) => {
    if (!quality) return '';
    if (quality.includes('excellent')) return 'lighting-excellent';
    if (quality.includes('good')) return 'lighting-good';
    if (quality.includes('fair')) return 'lighting-fair';
    if (quality.includes('poor')) return 'lighting-poor';
    return '';
  };

  // Get lighting icon based on condition
  const getLightingIcon = (condition) => {
    if (condition === 'dark') return '🌙';
    if (condition === 'bright') return '☀️';
    return '✓';
  };

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
        <div className="info-item">
          <span className="info-label">Lighting Quality:</span>
          <span className={`info-value ${getLightingClass(results?.lighting_quality)}`} id="lightingDisplay">
            {getLightingIcon(results?.lighting_condition)} {results?.lighting_quality || 'unknown'}
          </span>
        </div>
        {results?.confidence && (
          <div className="info-item">
            <span className="info-label">Confidence:</span>
            <span className="info-value" id="confidenceDisplay">
              {results.confidence}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default DetectionInfo;
