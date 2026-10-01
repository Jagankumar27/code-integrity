import { Link } from "react-router-dom";
const F = [["🧬", "Structural Analysis", "Compares AST / control-flow structure, so renamed variables and reformatting don't hide similar logic."],
  ["🧠", "Semantic Similarity", "TF-IDF vectors over normalised code capture shared vocabulary of operations, not just matching text."],
  ["🔍", "Explainable Reports", "Every score comes with evidence-based reasons, side-by-side highlights and a downloadable PDF."]];
export default function Landing() {
  return (<div>
    <section className="hero"><h1>AI-Powered <span>Code Integrity</span></h1>
      <p>Detect potential code similarity beyond simple text matching.</p>
      <div className="row center"><Link className="btn big" to="/login">Get Started</Link>
        <Link className="btn ghost big" to="/login?role=teacher">Teacher Login</Link><Link className="btn ghost big" to="/login?role=student">Student Login</Link></div></section>
    <div className="grid3">{F.map(([i, t, d]) => <div className="card feat" key={t}><div className="ico">{i}</div><h3>{t}</h3><p>{d}</p></div>)}</div>
    <p className="note center">Built to support human review — similarity is a signal, never proof of misconduct.</p></div>);
}
