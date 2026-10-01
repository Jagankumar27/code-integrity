import { Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./components/Ui";
import { getUser } from "./services/api";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Matrix from "./pages/Matrix";
import Comparison, { Report } from "./pages/Comparison";
import History from "./pages/History";

const Guard = ({ children, teacher }) => {
  const u = getUser();
  if (!u) return <Navigate to="/login" />;
  if (teacher && u.role !== "teacher") return <Navigate to="/dashboard" />;
  return children;
};
export default function App() {
  return (<Layout><Routes>
    <Route path="/" element={<Landing />} /><Route path="/login" element={<Login />} />
    <Route path="/dashboard" element={<Guard><Dashboard /></Guard>} />
    <Route path="/upload" element={<Guard><Upload /></Guard>} />
    <Route path="/matrix" element={<Guard teacher><Matrix /></Guard>} />
    <Route path="/history" element={<Guard><History /></Guard>} />
    <Route path="/compare/:id" element={<Guard><Comparison /></Guard>} />
    <Route path="/report/:id" element={<Guard><Report /></Guard>} />
    <Route path="*" element={<Navigate to="/" />} />
  </Routes></Layout>);
}
