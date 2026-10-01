import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { Card, riskClass, Note } from "../components/Ui";
export default function Matrix() {
  const [m, setM] = useState(null), [err, setErr] = useState(""), nav = useNavigate();
  useEffect(() => { api.matrix().then(setM).catch((e) => setErr(e.message)); }, []);
  if (err) return <p className="err">{err}</p>;
  if (!m) return <p>Loading…</p>;
  if (!m.ids.length) return <Card><p>No comparisons yet — run an analysis first.</p></Card>;
  return (<div><h2>Similarity matrix</h2><Card><p className="hint">Click a cell to open the side-by-side comparison. Colours follow the configured risk bands.</p>
    <div className="scroll"><table className="matrix"><thead><tr><th />{m.labels.map((l, i) => <th key={i}>{l}</th>)}</tr></thead>
      <tbody>{m.cells.map((row, i) => <tr key={i}><th>{m.labels[i]}</th>{row.map((c, j) => i === j ? <td key={j} className="diag">—</td> :
        <td key={j} className={c ? `cell ${riskClass(c.risk)}` : "diag"} onClick={() => c && nav(`/compare/${c.comparison_id}`)} title={c ? `${c.risk} similarity risk` : "not compared"}>{c ? Math.round(c.overall) : "·"}</td>)}</tr>)}</tbody></table></div></Card><Note /></div>);
}
