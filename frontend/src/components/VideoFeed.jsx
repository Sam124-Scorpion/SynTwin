import './VideoFeed.css';

const VideoFeed = ({ isDetecting, frameData }) => {
  return (
    <div className="card">
      <h2>Live Video Feed</h2>
      {isDetecting && frameData ? (
        <img
          id="videoFeed"
          src={`data:image/jpeg;base64,${frameData}`}
          alt="Video feed"
          className="video-feed"
        />
      ) : (
        <div className="video-placeholder">
          {isDetecting ? 'Waiting for camera...' : 'Camera Off'}
        </div>
      )}
    </div>
  );
};

export default VideoFeed;
