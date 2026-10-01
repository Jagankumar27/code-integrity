import { Link, useNavigate } from "react-router-dom";
import { getUser, logout } from "../services/api";

export const riskClass = (r) => ({ Low: "low", Moderate: "mod", High: "high", "Very High": "vhigh" }[r] || "low");
export const RiskBadge = ({ risk }) => <span className={`badge ${riskClass(risk)}`}>{risk} similarity risk</span>;
export const ScoreBar = ({ label, value }) => (
  <div className="score"><div className="score-h"><span>{label}</span><b>{value}%</b></div>
    <div className="bar"><div style={{ width: `${Math.min(100, value)}%` }} className={`fill ${value >= 80 ? "vhigh" : value >= 60 ? "high" : value >= 30 ? "mod" : "low"}`} /></div></div>
);
export const Card = ({ title, children, className = "" }) => <section className={`card ${className}`}>{title && <h3>{title}</h3>}{children}</section>;
export const Stat = ({ label, value }) => <div className="card stat"><span>{label}</span><b>{value}</b></div>;
export const Note = () => <p className="note">Similarity indicates <b>potential</b> code similarity and requires human review. It does not by itself establish plagiarism or misconduct.</p>;

export function Layout({ children }) {
  const user = getUser(), nav = useNavigate();
  return (<div>
    <header className="nav"><Link to="/" className="logo">◈ CodeIntegrity</Link>
      <nav>{user && <>
        <Link to="/dashboard">Dashboard</Link><Link to="/upload">Upload</Link>
        {user.role === "teacher" && <Link to="/matrix">Matrix</Link>}<Link to="/history">History</Link>
        <span className="who">{user.name} · {user.role}</span>
        <button className="btn ghost" onClick={() => { logout(); nav("/"); }}>Logout</button></>}
        {!user && <Link className="btn" to="/login">Login</Link>}</nav></header>
    <main className="wrap">{children}</main></div>);
}
