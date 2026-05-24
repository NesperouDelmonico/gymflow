// src/pages/MyMembershipPage.jsx
import { useEffect, useState } from "react";
import { membershipsApi } from "../services/api";
import { useAuth } from "../context/AuthContext";

const PLAN_COLOR = { basic: "var(--basic)", premium: "var(--premium)", deluxe: "var(--deluxe)" };
const PLAN_ICON  = { basic: "◆", premium: "◈", deluxe: "⬡" };

export default function MyMembershipPage() {
  const { user } = useAuth();
  const [memberships, setMemberships] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    membershipsApi.mine()
      .then(r => setMemberships(r.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loader" style={{ width:"100%", height:"60vh" }} />;

  const active = memberships.find(m => m.status === "active");

  return (
    <div>
      <div className="page-title">MI MEMBRESÍA</div>
      <div className="page-subtitle">Tu estado actual en GymFlow</div>

      {!active ? (
        <div className="card" style={{ textAlign:"center", padding:60 }}>
          <div style={{ fontSize:56, marginBottom:12 }}>◈</div>
          <div style={{ fontFamily:"var(--font-head)", fontSize:28, marginBottom:8 }}>SIN MEMBRESÍA ACTIVA</div>
          <div style={{ color:"var(--muted)" }}>Contacta al administrador para activar tu plan.</div>
        </div>
      ) : (
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:20, maxWidth:760 }}>
          <div className="card" style={{ borderTop:`4px solid ${PLAN_COLOR[active.plan_name]}`, gridColumn:"1/-1" }}>
            <div style={{ display:"flex", alignItems:"flex-start", justifyContent:"space-between", gap:16, flexWrap:"wrap" }}>
              <div>
                <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:8 }}>
                  <span style={{ fontSize:36, color:PLAN_COLOR[active.plan_name] }}>{PLAN_ICON[active.plan_name]}</span>
                  <span className={`badge badge-${active.plan_name}`} style={{ fontSize:13 }}>{active.plan_name?.toUpperCase()}</span>
                </div>
                <div style={{ fontFamily:"var(--font-head)", fontSize:42, letterSpacing:2, marginBottom:4 }}>
                  {active.plan_display_name}
                </div>
                <div style={{ color:"var(--muted)", fontSize:14 }}>Plan activo — renovación {active.auto_renew ? "automática" : "manual"}</div>
              </div>
              <div style={{ textAlign:"right" }}>
                <div style={{ fontFamily:"var(--font-head)", fontSize:48, color:PLAN_COLOR[active.plan_name] }}>
                  ${active.price_monthly?.toLocaleString("es-CO")}
                </div>
                <div style={{ color:"var(--muted)", fontSize:13 }}>por mes</div>
              </div>
            </div>
          </div>

          <div className="card">
            <div style={{ color:"var(--muted)", fontSize:12, textTransform:"uppercase", letterSpacing:1, marginBottom:6 }}>Inicio</div>
            <div style={{ fontFamily:"var(--font-head)", fontSize:28 }}>
              {new Date(active.start_date).toLocaleDateString("es-CO", { day:"2-digit", month:"long", year:"numeric" })}
            </div>
          </div>
          <div className="card">
            <div style={{ color:"var(--muted)", fontSize:12, textTransform:"uppercase", letterSpacing:1, marginBottom:6 }}>Vencimiento</div>
            <div style={{ fontFamily:"var(--font-head)", fontSize:28, color: new Date(active.end_date) < new Date() ? "var(--danger)" : "inherit" }}>
              {new Date(active.end_date).toLocaleDateString("es-CO", { day:"2-digit", month:"long", year:"numeric" })}
            </div>
          </div>

          {active.notes && (
            <div className="card" style={{ gridColumn:"1/-1" }}>
              <div style={{ color:"var(--muted)", fontSize:12, textTransform:"uppercase", letterSpacing:1, marginBottom:6 }}>Notas</div>
              <div style={{ fontSize:14 }}>{active.notes}</div>
            </div>
          )}
        </div>
      )}

      {memberships.length > 1 && (
        <div style={{ marginTop:32 }}>
          <div style={{ fontFamily:"var(--font-head)", fontSize:22, letterSpacing:1, marginBottom:16 }}>HISTORIAL</div>
          <div className="card" style={{ padding:0 }}>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr><th>Plan</th><th>Estado</th><th>Inicio</th><th>Fin</th></tr>
                </thead>
                <tbody>
                  {memberships.filter(m => m.id !== active?.id).map(m => (
                    <tr key={m.id}>
                      <td><span className={`badge badge-${m.plan_name}`}>{m.plan_display_name}</span></td>
                      <td><span className={`badge badge-${m.status}`}>{m.status}</span></td>
                      <td style={{ color:"var(--muted)" }}>{new Date(m.start_date).toLocaleDateString("es-CO")}</td>
                      <td style={{ color:"var(--muted)" }}>{new Date(m.end_date).toLocaleDateString("es-CO")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
