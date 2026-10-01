import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, getUser } from "../services/api";
import { Card, Stat, RiskBadge, Note } from "../components/Ui";
import { Distribution, Languages, TopPairs, Network } from "../charts/Charts";
export default function Dashboard() {
  const [d, setD] = useState(null), [err, setErr] = useState(""), nav = useNavigate(), u = getUser();
  useEffect(() => { api.dashboard().then(setD).catch((e) => setErr(e.message)); }, []);
  if (err) return <p className="err">{err}</p>;
  if (!d) return <p>Loading…</p>;
  const go = (id) => nav(`/compare/${id}`);
  return (<div><h2>{u.role === "teacher" ? "Teacher" : "Student"} dashboard</h2>
    {d.pairs_analyzed === 0 && <Card><p>No analysis yet. <Link to="/upload">Upload code and run an analysis</Link>{u.role === "teacher" && " or load the demo data there"}.</p></Card>}
    <div className="grid5"><Stat label="Total submissions" value={d.total_submissions} /><Stat label="Pairs analyzed" value={d.pairs_analyzed} />
      <Stat label="High-similarity pairs" value={d.high_pairs} /><Stat label="Average similarity" value={`${d.average_similarity}%`} />
      <Stat label="Languages" value={d.languages.map((l) => l.name).join(", ") || "—"} /></div>
    <div className="grid2"><Card title="Similarity distribution (pairs)"><Distribution data={d.distribution} /></Card>
      <Card title="Submission languages">{d.languages.length ? <Languages data={d.languages} /> : <p>No data</p>}</Card>
      <Card title="Highest-similarity pairs (click a bar)"><TopPairs data={d.top_pairs} onClick={go} /></Card>
      {u.role === "teacher" && <Card title="Similarity network (edges ≥ moderate)"><Network nodes={d.network.nodes} edges={d.network.edges} onClick={go} /></Card>}</div>
    <Card title="Top pairs requiring review">{d.top_pairs.map((p) => <div className="li" key={p.id}><Link to={`/compare/${p.id}`}>{p.label}</Link><b>{p.overall}%</b><RiskBadge risk={p.risk} /></div>)}</Card>
    <Note /></div>);
}
