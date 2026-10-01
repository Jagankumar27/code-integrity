const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const getUser = () => JSON.parse(localStorage.getItem("user") || "null");
export const logout = () => { localStorage.removeItem("token"); localStorage.removeItem("user"); };

async function req(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  const t = localStorage.getItem("token");
  if (t) headers.Authorization = `Bearer ${t}`;
  if (opts.json) { headers["Content-Type"] = "application/json"; opts.body = JSON.stringify(opts.json); }
  const r = await fetch(BASE + path, { ...opts, headers });
  if (!r.ok) {
    let m = r.statusText;
    try { const j = await r.json(); m = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail); } catch {}
    if (r.status === 401 && t) { logout(); location.hash = "#/login"; }
    throw new Error(m);
  }
  return opts.blob ? r.blob() : r.json();
}
export const api = {
  login: (username, password) => req("/api/auth/login", { method: "POST", json: { username, password } }),
  dashboard: () => req("/api/dashboard"),
  submissions: () => req("/api/submissions"),
  comparisons: () => req("/api/comparisons"),
  comparison: (id) => req(`/api/comparisons/${id}`),
  matrix: () => req("/api/matrix"),
  upload: (files, name) => { const f = new FormData(); [...files].forEach((x) => f.append("files", x)); if (name) f.append("student_name", name); return req("/api/submissions/upload", { method: "POST", body: f }); },
  analyzeMany: (ids) => req("/api/analyze/multiple", { method: "POST", json: { submission_ids: ids } }),
  analyzeOne: (id) => req("/api/analyze", { method: "POST", json: { submission_id: id } }),
  demo: () => req("/api/demo/load", { method: "POST" }),
  report: async (id) => {
    const b = await req(`/api/reports/${id}`, { blob: true });
    const a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = `integrity_report_${id}.pdf`; a.click();
  },
};
