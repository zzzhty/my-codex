import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import AuditDashboard from "./pages/Audit/AuditDashboard";
import FindingDetail from "./pages/Audit/FindingDetail";
import ReportDetail from "./pages/Audit/ReportDetail";

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/audit" replace />} />
        <Route path="/dashboard" element={<Navigate to="/audit" replace />} />
        <Route path="/audit" element={<AuditDashboard />} />
        <Route path="/audit/reports/:reportId" element={<ReportDetail />} />
        <Route path="/audit/repos/:repoName/findings/:findingId" element={<FindingDetail />} />
      </Route>
    </Routes>
  );
}

export default App;
