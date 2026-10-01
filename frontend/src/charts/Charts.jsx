import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, CartesianGrid } from "recharts";
const COLORS = ["#6366f1", "#06b6d4", "#f59e0b", "#ec4899"];
export const Distribution = ({ data }) => (<ResponsiveContainer width="100%" height={220}><BarChart data={data}><CartesianGrid strokeDasharray="3 3" vertical={false} />
  <XAxis dataKey="range" fontSize={11} /><YAxis allowDecimals={false} fontSize={11} /><Tooltip /><Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer>);
export const Languages = ({ data }) => (<ResponsiveContainer width="100%" height={220}><PieChart><Pie data={data} dataKey="value" nameKey="name" innerRadius={45} outerRadius={80} label>
  {data.map((_, i) => <Cell key={i} fill={COLORS[i % 4]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer>);
export const TopPairs = ({ data, onClick }) => (<ResponsiveContainer width="100%" height={220}><BarChart data={data} layout="vertical" margin={{ left: 30 }}>
  <XAxis type="number" domain={[0, 100]} fontSize={11} /><YAxis type="category" dataKey="label" width={130} fontSize={11} /><Tooltip />
  <Bar dataKey="overall" fill="#ef4444" radius={[0, 4, 4, 0]} onClick={(d) => onClick && onClick(d.id)} cursor="pointer" /></BarChart></ResponsiveContainer>);
export function Network({ nodes, edges, onClick }) {
  const R = 110, C = 140, pos = Object.fromEntries(nodes.map((n, i) => [n, [C + R * Math.cos((2 * Math.PI * i) / nodes.length), C + R * Math.sin((2 * Math.PI * i) / nodes.length)]]));
  return (<svg viewBox="0 0 280 280" width="100%" height="260">
    {edges.map((e, i) => pos[e.a] && pos[e.b] && <line key={i} x1={pos[e.a][0]} y1={pos[e.a][1]} x2={pos[e.b][0]} y2={pos[e.b][1]} stroke={e.overall >= 80 ? "#ef4444" : e.overall >= 60 ? "#f97316" : "#f59e0b"}
      strokeWidth={1 + e.overall / 25} opacity=".8" style={{ cursor: "pointer" }} onClick={() => onClick(e.id)}><title>{`${e.a} ↔ ${e.b}: ${e.overall}%`}</title></line>)}
    {nodes.map((n) => <g key={n}><circle cx={pos[n][0]} cy={pos[n][1]} r="14" fill="#6366f1" /><text x={pos[n][0]} y={pos[n][1] + 26} fontSize="10" textAnchor="middle" fill="#334155">{n.slice(0, 10)}</text></g>)}</svg>);
}
