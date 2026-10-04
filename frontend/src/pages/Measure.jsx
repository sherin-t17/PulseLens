import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeVideo, loadName, saveName } from "../services/api.js";

const MAX_MB = 100;
const ALLOWED = [".mp4", ".avi", ".mov"];
const MESSAGES = [
  "Analyzing your video...",
  "Extracting PPG signal...",
  "Processing heart-rate frequency...",
];

export default function Measure() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [name, setName] = useState(loadName());
  const [channel, setChannel] = useState("green");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [pct, setPct] = useState(0);
  const [msgIndex, setMsgIndex] = useState(0);

  // Rotate the "processing" messages so the screen never looks frozen
  useEffect(() => {
    if (!busy) return;
    const id = setInterval(() => setMsgIndex((i) => (i + 1) % MESSAGES.length), 3000);
    return () => clearInterval(id);
  }, [busy]);

  function handlePick(e) {
    const f = e.target.files[0];
    setError("");
    if (!f) { setFile(null); return; }
    const ext = f.name.slice(f.name.lastIndexOf(".")).toLowerCase();
    if (!ALLOWED.includes(ext)) {
      setFile(null);
      setError("Please choose an MP4, AVI or MOV video.");
      return;
    }
    if (f.size > MAX_MB * 1024 * 1024) {
      setFile(null);
      setError(`This video is larger than ${MAX_MB} MB. Try recording at 720p.`);
      return;
    }
    setFile(f);
  }

  async function handleAnalyze() {
    if (!file) { setError("Please select a video first."); return; }
    setError("");
    setBusy(true);
    setPct(0);
    setMsgIndex(0);
    saveName(name.trim());
    try {
      const result = await analyzeVideo(file, name.trim(), channel, setPct);
      navigate(`/result/${result.id}`);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <>
      <h1>New Measurement</h1>

      <div className="card">
        <h3>How to record</h3>
        <ol className="steps">
          <li>Sit comfortably.</li>
          <li>Keep your hand steady.</li>
          <li>Place your fingertip gently over the phone camera (turn the flash ON).</li>
          <li>Record approximately 20-30 seconds.</li>
          <li>Upload the recorded video below.</li>
        </ol>
        <p className="notice">
          This prototype analyzes a <strong>recorded video</strong>. The website does not
          control your phone's camera or flash. Uploaded videos are used only for
          processing and are deleted afterwards.
        </p>
      </div>

      <div className="card">
        <label className="field">
          <span>Name (optional)</span>
          <input type="text" value={name} maxLength={60} placeholder="Anonymous User"
                 onChange={(e) => setName(e.target.value)} disabled={busy} />
        </label>

        <label className="upload-box">
          <input type="file" accept=".mp4,.avi,.mov,video/mp4,video/quicktime,video/x-msvideo"
                 onChange={handlePick} disabled={busy} />
          <span className="upload-icon">📹</span>
          <span className="upload-text">{file ? "Choose a different video" : "Upload Video"}</span>
        </label>

        {file && (
          <p className="file-info">
            Selected: <strong>{file.name}</strong> ({(file.size / 1024 / 1024).toFixed(1)} MB)
          </p>
        )}

        <details className="advanced">
          <summary>Advanced</summary>
          <label className="field">
            <span>Color channel used for the signal</span>
            <select value={channel} onChange={(e) => setChannel(e.target.value)} disabled={busy}>
              <option value="green">Green (default)</option>
              <option value="red">Red (often stronger with flash)</option>
            </select>
          </label>
        </details>

        {error && <div className="error-box">{error}</div>}

        {busy ? (
          <div className="busy">
            {pct < 100 ? (
              <>
                <p>Uploading video... {pct}%</p>
                <div className="progress"><div style={{ width: `${pct}%` }} /></div>
              </>
            ) : (
              <>
                <div className="spinner" />
                <p>{MESSAGES[msgIndex]}</p>
              </>
            )}
          </div>
        ) : (
          <button className="btn btn-primary btn-block" onClick={handleAnalyze}>
            Analyze Video
          </button>
        )}
      </div>
    </>
  );
}