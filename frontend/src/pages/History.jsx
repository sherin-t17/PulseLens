import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import LineChart from "../components/LineChart.jsx";
import StatCard from "../components/StatCard.jsx";
import { deleteMeasurement, getHistory } from "../services/api.js";

export default function History() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  function load() {
    getHistory().then(setData).catch((e) => setError(e.message));
  }
  useEffect(load, []);

  async function handleDelete(id) {
    if (!window.confirm("Delete this measurement?")) return;
    try {
      await deleteMeasurement(id);
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  if (error) return <div className="error-box">{error}</div>;
  if (!data) return <p className="muted">Loading history...</p>;

  const { stats, items } = data;
  if (items.length === 0) {
    return (
      <div className="card">
        <h1>Measurement History</h1>
        <p>No measurements yet.</p>
        <Link to="/measure" className="btn btn-primary">Start Measurement</Link>
      </div>
    );
  }

  const recent = items.slice(0, 30).reverse(); // oldest -> newest for the chart

  return (
    <>
      <h1>Measurement History</h1>

      <div className="grid-stats">
        <StatCard label="Latest" value={stats.latest} unit="BPM" />
        <StatCard label="Average" value={stats.average} unit="BPM" />
        <StatCard label="Minimum" value={stats.minimum} unit="BPM" />
        <StatCard label="Maximum" value={stats.maximum} unit="BPM" />
        <StatCard label="Measurements" value={stats.count} />
      </div>

      <div className="card">
        <h3>Heart rate history</h3>
        <LineChart xs={recent.map((_, i) => i + 1)} ys={recent.map((r) => r.bpm)}
                   xLabel="Measurement (oldest to newest)" yLabel="Estimated BPM"
                   showDots xDecimals={0} />
        <p className="muted small">
          For information only. No medical conclusions should be drawn from these values.
        </p>
      </div>

      <ul className="history-list">
        {items.map((m) => (
          <li key={m.id} className="history-item">
            <Link to={`/result/${m.id}`} className="history-main">
              <div className="muted small">{m.date} - {m.time}</div>
              <div className="history-bpm">❤️ {Math.round(m.bpm)} BPM</div>
              <div className="small">
                Signal Quality: {m.quality_label.charAt(0) + m.quality_label.slice(1).toLowerCase()}
              </div>
            </Link>
            <button className="icon-btn" onClick={() => handleDelete(m.id)}
                    aria-label="Delete measurement">🗑️</button>
          </li>
        ))}
      </ul>
    </>
  );
}