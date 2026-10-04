import { useState } from "react";
import { Link } from "react-router-dom";
import { deleteAllHistory, downloadReport, loadName, saveName } from "../services/api.js";

export default function Report() {
  const [name, setName] = useState(loadName());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  async function handleDownload() {
    setError(""); setInfo(""); setBusy(true);
    saveName(name.trim());
    try {
      await downloadReport(name.trim());
      setInfo("Your report was downloaded.");
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleDeleteAll() {
    if (!window.confirm("Delete ALL your saved measurements? This cannot be undone.")) return;
    setError(""); setInfo("");
    try {
      await deleteAllHistory();
      setInfo("All your measurements were deleted.");
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <>
      <h1>PDF Report</h1>

      <div className="card">
        <p>The report includes your latest measurement, your history table, the PPG
          signal graph, the frequency spectrum, the heart-rate history graph, the
          interpretation and a disclaimer.</p>

        <label className="field">
          <span>Name on the report (optional)</span>
          <input type="text" value={name} maxLength={60} placeholder="Anonymous User"
                 onChange={(e) => setName(e.target.value)} />
        </label>

        {error && <div className="error-box">
          {error} {error.includes("No measurements") && <Link to="/measure">Record one now</Link>}
        </div>}
        {info && <div className="success-box">{info}</div>}

        <button className="btn btn-primary btn-block" onClick={handleDownload} disabled={busy}>
          {busy ? "Creating PDF..." : "Download Report"}
        </button>
      </div>

      <div className="card">
        <h3>Your data</h3>
        <p className="small">
          Measurements are stored on the PulseLens server for this prototype. Videos are
          deleted right after processing. No account is needed. You can delete your saved
          history at any time.
        </p>
        <button className="btn btn-danger" onClick={handleDeleteAll}>Delete all my history</button>
      </div>
    </>
  );
}