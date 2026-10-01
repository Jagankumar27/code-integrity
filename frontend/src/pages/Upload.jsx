import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, getUser } from "../services/api";
import { Card, RiskBadge } from "../components/Ui";
export default function Upload() {
  const u = getUser(), teacher = u.role === "teacher", nav = useNavigate();
  const [files, setFiles] = useState([]), [name, setName] = useState(""), [subs, setSubs] = useState([]), [sel, setSel] = useState([]);
  const [busy, setBusy] = useState(""), [err, setErr] = useState(""), [res, setRes] = useState(null);
  const load = () => api.submissions().then((s) => { setSubs(s); }).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);
  const run = async (label, fn) => { setBusy(label); setErr(""); try { await fn(); } catch (e) { setErr(e.message); } finally { setBusy(""); } };
  const upload = () => run("Uploading…", async () => { const r = await api.upload(files, name); setFiles([]); await load(); setSel((s) => [...s, ...r.map((x) => x.id)]); });
  const analyze = () => run("Analyzing…", async () => {
    if (teacher) { await api.analyzeMany(sel); nav("/dashboard"); }
    else { const r = await api.analyzeOne(sel[0]); setRes(r); }
  });
  const toggle = (id) => setSel((s) => (teacher ? (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]) : [id]));
  return (<div><h2>Upload & analyze</h2>
    <Card title={teacher ? "1 · Upload student files" : "1 · Upload your code"}>
      <input type="file" multiple={teacher} accept=".py,.java,.c,.cpp,.cc,.h,.hpp" onChange={(e) => setFiles(e.target.files)} />
      {teacher && files.length === 1 && <input placeholder="Student name (optional)" value={name} onChange={(e) => setName(e.target.value)} />}
      <p className="hint">Allowed: .py .java .c .cpp — max 200 KB each. Files are only analysed as text, never executed.</p>
      <button className="btn" disabled={!files.length || !!busy} onClick={upload}>Upload {files.length || ""} file(s)</button>
      {teacher && <button className="btn ghost" disabled={!!busy} onClick={() => run("Loading demo…", async () => { await api.demo(); nav("/dashboard"); })}>Load & analyze demo data (5 samples)</button>}</Card>
    <Card title="2 · Choose submissions & analyze">
      {subs.length === 0 && <p>No submissions yet.</p>}
      {subs.map((s) => <label className="li check" key={s.id}><input type={teacher ? "checkbox" : "radio"} checked={sel.includes(s.id)} onChange={() => toggle(s.id)} />
        <span>{s.student_name} — {s.filename}</span><i>{s.language} · {s.lines} lines</i></label>)}
      <button className="btn" disabled={!!busy || (teacher ? sel.length < 2 : sel.length < 1)} onClick={analyze}>{teacher ? `Analyze ${sel.length} selected` : "Check my submission"}</button>
      {busy && <div className="progress"><div /><span>{busy} normalising code and computing text, token, structural & semantic scores…</span></div>}
      {err && <p className="err">{err}</p>}</Card>
    {res && <Card title="Your similarity results">{res.comparisons.map((c) => <div className="li" key={c.id}><a href={`#/compare/${c.id}`}>vs. {c.b.student}</a><b>{c.scores.overall}%</b><RiskBadge risk={c.risk} /></div>)}</Card>}</div>);
}
