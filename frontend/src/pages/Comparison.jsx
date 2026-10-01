import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../services/api";
import { Card, ScoreBar, RiskBadge, Note } from "../components/Ui";

function CodePanel({ side, blocks, which }) {
  const lines = (side.code || "").split("\n"), hit = new Set();
  blocks.forEach((b) => { for (let i = b[which][0]; i <= b[which][1]; i++) hit.add(i); });
  return (<div className="panel"><div className="ph">{side.student} <i>{side.filename}</i></div>
    {side.code == null ? <p className="hint pad">Other student's code is hidden for privacy.</p> :
      <pre>{lines.map((l, i) => <div key={i} className={`ln ${hit.has(i + 1) ? "hit" : ""}`}><span>{i + 1}</span>{l || " "}</div>)}</pre>}</div>);
}
const useComparison = () => { const { id } = useParams(); const [c, setC] = useState(null), [err, setErr] = useState(""); useEffect(() => { api.comparison(id).then(setC).catch((e) => setErr(e.message)); }, [id]); return [c, err, id]; };

export default function Comparison() {
  const [c, err, id] = useComparison();
  if (err) return <p className="err">{err}</p>;
  if (!c) return <p>Loading…</p>;
  const s = c.scores;
  return (<div><div className="row between"><h2>{c.a.student} ↔ {c.b.student}</h2>
    <div className="row"><RiskBadge risk={c.risk} /><button className="btn" onClick={() => api.report(id)}>⬇ Download PDF report</button></div></div>
    <div className="grid2"><Card title="Overall similarity"><div className="big">{s.overall}%</div><p className="hint">Structural method: {c.method}. Requires human review.</p></Card>
      <Card title="Score breakdown"><ScoreBar label="Text similarity" value={s.text} /><ScoreBar label="Token similarity" value={s.token} />
        <ScoreBar label="Structural similarity" value={s.structural} /><ScoreBar label="Semantic similarity" value={s.semantic} /></Card></div>
    <Card title="Why was this pair flagged?">{c.explanations.map((e, i) => <div className="why" key={i}><b>{e.title}</b><p>{e.evidence}</p></div>)}
      {c.renames.length > 0 && <div className="chips">{c.renames.map((r, i) => <span key={i}>{r.a} → {r.b}</span>)}</div>}</Card>
    <Card title="Side-by-side comparison"><p className="hint"><span className="legend" /> Highlighted lines align after normalisation (comments, whitespace, identifier names ignored).</p>
      <div className="split"><CodePanel side={c.a} blocks={c.blocks} which="a" /><CodePanel side={c.b} blocks={c.blocks} which="b" /></div></Card>
    <Note /></div>);
}
export function Report() {
  const [c, err, id] = useComparison();
  if (err) return <p className="err">{err}</p>;
  if (!c) return <p>Loading…</p>;
  return (<div className="narrow"><Card title="AI Code Integrity Report"><p>{c.a.student} ({c.a.filename}) vs {c.b.student}</p>
    <p>Overall {c.scores.overall}% — <RiskBadge risk={c.risk} /></p><button className="btn" onClick={() => api.report(id)}>⬇ Download PDF</button>{" "}
    <Link className="btn ghost" to={`/compare/${id}`}>Open comparison</Link></Card><Note /></div>);
}
