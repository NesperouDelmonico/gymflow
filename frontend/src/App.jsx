// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import MembershipsPage from "./pages/MembershipsPage";
import UsersPage from "./pages/UsersPage";
import PlansPage from "./pages/PlansPage";
import MyMembershipPage from "./pages/MyMembershipPage";
import Layout from "./components/Layout";

function PrivateRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="loader" />;
  if (!user) return <Navigate to="/login" replace />;
  if (adminOnly && user.role_name !== "admin") return <Navigate to="/my-membership" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<PrivateRoute adminOnly><DashboardPage /></PrivateRoute>} />
            <Route path="memberships" element={<PrivateRoute adminOnly><MembershipsPage /></PrivateRoute>} />
            <Route path="users" element={<PrivateRoute adminOnly><UsersPage /></PrivateRoute>} />
            <Route path="plans" element={<PrivateRoute adminOnly><PlansPage /></PrivateRoute>} />
            <Route path="my-membership" element={<PrivateRoute><MyMembershipPage /></PrivateRoute>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
