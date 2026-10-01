import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { Card, RiskBadge } from "../components/Ui";
export default function History() {
  const [subs, setS] = useState([]), [cmp, setC] = useState([]), [err, setErr] = useState("");
  useEffect(() => { Promise.all([api.submissions(), api.comparisons()]).then(([a, b]) => { setS(a); setC(b); }).catch((e) => setErr(e.message)); }, []);
  return (<div><h2>Submission history</h2>{err && <p className="err">{err}</p>}
    <Card title="Analysis results (highest first)">{cmp.length === 0 && <p>No analyses yet.</p>}
      {cmp.map((c) => <div className="li" key={c.id}><Link to={`/compare/${c.id}`}>{c.a.student} ↔ {c.b.student}</Link><b>{c.scores.overall}%</b><RiskBadge risk={c.risk} />
        <Link to={`/report/${c.id}`}>Report</Link></div>)}</Card>
    <Card title="Submissions">{subs.map((s) => <div className="li" key={s.id}><span>{s.student_name} — {s.filename}</span><i>{s.language} · {new Date(s.uploaded_at).toLocaleString()}</i></div>)}</Card></div>);
}
