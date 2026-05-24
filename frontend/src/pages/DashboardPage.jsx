// src/pages/DashboardPage.jsx
import { useEffect, useState } from "react";
import { membershipsApi, plansApi, usersApi } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState({ memberships: [], plans: [], users: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([membershipsApi.list(), plansApi.list(), usersApi.list()])
      .then(([m, p, u]) => {
        setData({ memberships: m.data, plans: p.data, users: u.data });
        setLoading(false);
      });
  }, []);

  const active    = data.memberships.filter(m => m.status === "active").length;
  const paused    = data.memberships.filter(m => m.status === "paused").length;
  const cancelled = data.memberships.filter(m => m.status === "cancelled").length;
  const revenue   = data.memberships
    .filter(m => m.status === "active")
    .reduce((s, m) => s + (m.price_monthly || 0), 0);

  const planCount = {};
  data.memberships.forEach(m => {
    if (m.plan_name) planCount[m.plan_name] = (planCount[m.plan_name] || 0) + 1;
  });

  if (loading) return <div className="loader" style={{ width:"100%", height:"60vh" }} />;

  return (
    <div>
      <div className="page-title">DASHBOARD</div>
      <div className="page-subtitle">Hola, {user?.full_name?.split(" ")[0]} — resumen del día</div>

      <div className="stats-grid">
        <div className="stat-card" style={{ borderTop:"3px solid var(--success)" }}>
          <div className="stat-value" style={{ color:"var(--success)" }}>{active}</div>
          <div className="stat-label">Membresías activas</div>
        </div>
        <div className="stat-card" style={{ borderTop:"3px solid var(--deluxe)" }}>
          <div className="stat-value" style={{ color:"var(--deluxe)" }}>{paused}</div>
          <div className="stat-label">Pausadas</div>
        </div>
        <div className="stat-card" style={{ borderTop:"3px solid var(--danger)" }}>
          <div className="stat-value" style={{ color:"var(--danger)" }}>{cancelled}</div>
          <div className="stat-label">Canceladas</div>
        </div>
        <div className="stat-card" style={{ borderTop:"3px solid var(--accent)" }}>
          <div className="stat-value" style={{ color:"var(--accent)", fontSize:32 }}>
            ${revenue.toLocaleString("es-CO")}
          </div>
          <div className="stat-label">Ingreso mensual activo</div>
        </div>
        <div className="stat-card" style={{ borderTop:"3px solid var(--basic)" }}>
          <div className="stat-value" style={{ color:"var(--basic)" }}>{data.users.length}</div>
          <div className="stat-label">Usuarios registrados</div>
        </div>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:20 }}>
        {/* Distribución de planes */}
        <div className="card">
          <h3 style={{ fontFamily:"var(--font-head)", fontSize:22, letterSpacing:1, marginBottom:20 }}>
            DISTRIBUCIÓN DE PLANES
          </h3>
          {data.plans.map(p => {
            const count = planCount[p.name] || 0;
            const total = data.memberships.length || 1;
            const pct   = Math.round((count / total) * 100);
            const color = p.name === "basic" ? "var(--basic)" : p.name === "premium" ? "var(--premium)" : "var(--deluxe)";
            return (
              <div key={p.id} style={{ marginBottom:16 }}>
                <div style={{ display:"flex", justifyContent:"space-between", marginBottom:6, fontSize:13 }}>
                  <span style={{ color }}>{p.display_name}</span>
                  <span style={{ color:"var(--muted)" }}>{count} miembros ({pct}%)</span>
                </div>
                <div style={{ height:8, background:"var(--bg3)", borderRadius:4, overflow:"hidden" }}>
                  <div style={{ height:"100%", width:`${pct}%`, background:color, borderRadius:4, transition:"width .5s" }} />
                </div>
              </div>
            );
          })}
        </div>

        {/* Membresías recientes */}
        <div className="card">
          <h3 style={{ fontFamily:"var(--font-head)", fontSize:22, letterSpacing:1, marginBottom:20 }}>
            ÚLTIMAS MEMBRESÍAS
          </h3>
          {data.memberships.slice(0, 6).map(m => (
            <div key={m.id} style={{ display:"flex", alignItems:"center", gap:12, marginBottom:14 }}>
              <div style={{ width:36, height:36, background:"var(--bg3)", borderRadius:"50%", display:"grid", placeItems:"center", fontWeight:700, flexShrink:0 }}>
                {m.user_name?.[0]}
              </div>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontSize:13, fontWeight:600, whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis" }}>{m.user_name}</div>
                <div style={{ fontSize:12, color:"var(--muted)" }}>{m.plan_display_name}</div>
              </div>
              <span className={`badge badge-${m.status}`}>{m.status}</span>
            </div>
          ))}
          {data.memberships.length === 0 && <div style={{ color:"var(--muted)", fontSize:14 }}>Sin membresías aún.</div>}
        </div>
      </div>
    </div>
  );
}
