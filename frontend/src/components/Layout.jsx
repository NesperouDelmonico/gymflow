// src/components/Layout.jsx
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Layout.css";

const ADMIN_NAV = [
  { to: "/dashboard",    icon: "⬡", label: "Dashboard" },
  { to: "/memberships",  icon: "◈", label: "Membresías" },
  { to: "/users",        icon: "◉", label: "Usuarios" },
  { to: "/plans",        icon: "◆", label: "Planes" },
];
const USER_NAV = [
  { to: "/my-membership", icon: "◈", label: "Mi Membresía" },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const nav = user?.role_name === "admin" ? ADMIN_NAV : USER_NAV;

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span className="logo-mark">GF</span>
          <span className="logo-text">GymFlow</span>
        </div>

        <nav className="sidebar-nav">
          {nav.map(({ to, icon, label }) => (
            <NavLink key={to} to={to} className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}>
              <span className="nav-icon">{icon}</span>
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-user">
          <div className="user-avatar">{user?.full_name?.[0]?.toUpperCase()}</div>
          <div className="user-info">
            <div className="user-name">{user?.full_name}</div>
            <div className="user-role">{user?.role_name === "admin" ? "Administrador" : "Miembro"}</div>
          </div>
          <button className="logout-btn" onClick={() => { logout(); navigate("/login"); }} title="Cerrar sesión">
            ⟶
          </button>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
