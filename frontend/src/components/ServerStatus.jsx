import './ServerStatus.css';

const ServerStatus = ({ online }) => {
  return (
    <div id="serverStatus" className="card">
      <h2>Server Status</h2>
      {online ? (
        <span className="status online">🟢 Server Online & Ready</span>
      ) : (
        <>
          <span className="status offline">🔴 Server Offline</span>
          <br />
          <small>Run: python start_api_server.py</small>
        </>
      )}
    </div>
  );
};

export default ServerStatus;
