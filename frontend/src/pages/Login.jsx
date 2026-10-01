import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../services/api";
import { Card } from "../components/Ui";
export default function Login() {
  const [q] = useSearchParams(), nav = useNavigate();
  const [role, setRole] = useState(q.get("role") === "student" ? "student" : "teacher");
  const [u, setU] = useState(role === "teacher" ? "teacher" : "alice"), [p, setP] = useState(role === "teacher" ? "teacher123" : "student123");
  const [err, setErr] = useState(""), [busy, setBusy] = useState(false);
  const pick = (r) => { setRole(r); setU(r === "teacher" ? "teacher" : "alice"); setP(r === "teacher" ? "teacher123" : "student123"); };
  const submit = async (e) => {
    e.preventDefault(); setBusy(true); setErr("");
    try { const r = await api.login(u, p); localStorage.setItem("token", r.token); localStorage.setItem("user", JSON.stringify(r.user)); nav("/dashboard"); }
    catch (x) { setErr(x.message); } finally { setBusy(false); }
  };
  return (<div className="narrow"><Card title="Sign in">
    <div className="tabs">{["teacher", "student"].map((r) => <button key={r} className={role === r ? "on" : ""} onClick={() => pick(r)} type="button">{r}</button>)}</div>
    <form onSubmit={submit}><label>Username<input value={u} onChange={(e) => setU(e.target.value)} /></label>
      <label>Password<input type="password" value={p} onChange={(e) => setP(e.target.value)} /></label>
      {err && <p className="err">{err}</p>}<button className="btn" disabled={busy}>{busy ? "Signing in…" : "Login"}</button></form>
    <p className="hint">Demo — teacher / teacher123 · students: alice, bob, carol, dave, eve / student123</p></Card></div>);
}
