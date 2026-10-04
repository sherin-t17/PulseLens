import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import LineChart from "../components/LineChart.jsx";
import QualityBadge from "../components/QualityBadge.jsx";
import StatCard from "../components/StatCard.jsx";
import { getMeasurement } from "../services/api.js";

export default function Result() {
  const { id } = useParams();
  const [m, setM] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setM(null);
    setError("");
    getMeasurement(id).then(setM).catch((e) => setError(e.message));
  }, [id]);

  if (error) {
    return (
      <div className="card">
        <div className="error-box">{error}</div>
        <Link to="/history" className="btn btn-secondary">Back to history</Link>
      </div>
    );
  }
  if (!m) return <p className="muted">Loading result...</p>;

  return (
    <>
      <h1>Result</h1>

      <div className="card bpm-card">
        <div className="muted">Estimated Heart Rate</div>
        <div className="bpm">❤️ {Math.round(m.bpm)} <span>BPM</span></div>
        <QualityBadge label={m.quality_label} />
        <p className="muted small">{m.date} - {m.time}</p>
      </div>

      <div className="card">
        <p className="interpretation">{m.interpretation}</p>
        <p className="muted small">
          Informational only. This is not a diagnosis and not a medical device.
        </p>
      </div>

      <div className="grid-stats three">
        <StatCard label="Quality score" value={m.quality_score.toFixed(2)} />
        <StatCard label="Duration" value={Math.round(m.duration_seconds)} unit="s" />
        <StatCard label="Dominant frequency" value={m.dominant_frequency_hz.toFixed(2)} unit="Hz" />
      </div>

      <div className="card">
        <h3>PPG signal</h3>
        <LineChart xs={m.ppg.t} ys={m.ppg.y} xLabel="Time (s)" yLabel="Amplitude (normalized)" />
      </div>

      <div className="card">
        <h3>Frequency spectrum</h3>
        <LineChart xs={m.spectrum.f} ys={m.spectrum.p} xLabel="Frequency (Hz)"
                   yLabel="Relative power" color="#2563eb"
                   markerX={m.dominant_frequency_hz}
                   markerLabel={`${Math.round(m.bpm)} BPM`} xDecimals={1} />
      </div>

      <details className="card">
        <summary><strong>How was this calculated?</strong></summary>
        <ol className="steps">
          <li><strong>Video:</strong> your fingertip video, frame by frame.</li>
          <li><strong>Green-channel signal:</strong> the average brightness of the centre of each frame.</li>
          <li><strong>Filtering:</strong> slow drift and fast noise are removed (0.7-4.0 Hz kept).</li>
          <li><strong>FFT:</strong> splits the signal into its frequencies.</li>
          <li><strong>Dominant frequency:</strong> the strongest peak, here {m.dominant_frequency_hz.toFixed(2)} Hz.</li>
          <li><strong>BPM:</strong> {m.dominant_frequency_hz.toFixed(2)} Hz x 60 = {Math.round(m.bpm)} beats per minute.</li>
        </ol>
        <p className="muted small">
          Channel used: {m.channel}. The quality score shows how much of the signal energy
          sits in one clear peak. It is a simple measure and not clinically validated.
        </p>
      </details>

      <div className="btn-row">
        <Link to="/measure" className="btn btn-primary">Measure again</Link>
        <Link to="/history" className="btn btn-secondary">View history</Link>
        <Link to="/report" className="btn btn-secondary">Download report</Link>
      </div>
    </>
  );
}