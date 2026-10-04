// All communication with the FastAPI backend lives in this one file.

const API = "/api";

// No login system: each browser gets a random anonymous ID, sent with every
// request, so people only see their own measurements.
function getClientId() {
  try {
    let id = localStorage.getItem("pulselens_client_id");
    if (!id) {
      id = "c" + Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
      localStorage.setItem("pulselens_client_id", id);
    }
    return id;
  } catch {
    return "anonymous";
  }
}

// Remember the optional name between visits
export function loadName() {
  try { return localStorage.getItem("pulselens_name") || ""; } catch { return ""; }
}
export function saveName(name) {
  try { localStorage.setItem("pulselens_name", name); } catch { /* ignore */ }
}

async function errorMessage(res) {
  try {
    const data = await res.json();
    if (typeof data.detail === "string") return data.detail;
  } catch { /* ignore */ }
  return "Something went wrong. Please try again.";
}

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(API + path, {
      ...options,
      headers: { "X-Client-Id": getClientId(), ...(options.headers || {}) },
    });
  } catch {
    throw new Error("Cannot reach the server. Make sure the backend is running.");
  }
  if (!res.ok) throw new Error(await errorMessage(res));
  return res;
}

export async function getHistory() {
  return (await request("/history")).json();
}

export async function getMeasurement(id) {
  return (await request(`/history/${id}`)).json();
}

export async function deleteMeasurement(id) {
  await request(`/history/${id}`, { method: "DELETE" });
}

export async function deleteAllHistory() {
  await request("/history", { method: "DELETE" });
}

// The PDF needs our X-Client-Id header, so a plain <a href> link would not work.
// We fetch the file, then trigger a download from the browser.
export async function downloadReport(name) {
  const res = await request(`/report?name=${encodeURIComponent(name || "")}`);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "PulseLens_Report.pdf";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// Upload uses XMLHttpRequest (not fetch) because it can report upload progress.
export function analyzeVideo(file, name, channel, onProgress) {
  return new Promise((resolve, reject) => {
    const form = new FormData();
    form.append("file", file);
    form.append("name", name || "");
    form.append("channel", channel);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API}/analyze`);
    xhr.setRequestHeader("X-Client-Id", getClientId());

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) onProgress(Math.round((e.loaded / e.total) * 100));
    };
    xhr.onload = () => {
      let data = null;
      try { data = JSON.parse(xhr.responseText); } catch { /* ignore */ }
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(data);
      } else {
        const msg = data && typeof data.detail === "string"
          ? data.detail
          : "The video could not be analyzed. Please try again.";
        reject(new Error(msg));
      }
    };
    xhr.onerror = () =>
      reject(new Error("Cannot reach the server. Make sure the backend is running."));
    xhr.send(form);
  });
}