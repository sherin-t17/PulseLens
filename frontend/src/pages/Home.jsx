import { Link } from "react-router-dom";

export default function Home() {
  return (
    <>
      <section className="hero">
        <p className="tag">Prototype • Not a medical device</p>
        <h1>PulseLens</h1>
        <p className="hero-sub">See your pulse through your camera.</p>
        <p>
          PulseLens is a student-built prototype that estimates heart rate from a short
          fingertip video using camera-based photoplethysmography (PPG).
        </p>
        <div className="btn-row">
          <Link to="/measure" className="btn btn-primary">Start Measurement</Link>
          <Link to="/history" className="btn btn-secondary">View History</Link>
          <Link to="/report" className="btn btn-secondary">Download Report</Link>
        </div>
      </section>

      <section className="grid-3">
        <div className="card">
          <div className="big-icon">🎥</div>
          <h3>1. Record</h3>
          <p>Record 20-30 seconds with your fingertip over the camera and flash.</p>
        </div>
        <div className="card">
          <div className="big-icon">⬆️</div>
          <h3>2. Upload</h3>
          <p>Upload the video here. It is only used for processing, then deleted.</p>
        </div>
        <div className="card">
          <div className="big-icon">📈</div>
          <h3>3. Analyze</h3>
          <p>The signal is filtered and an FFT finds the dominant pulse frequency.</p>
        </div>
      </section>
    </>
  );
}