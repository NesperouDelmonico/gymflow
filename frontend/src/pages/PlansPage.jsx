// src/pages/PlansPage.jsx
import { useEffect, useState } from "react";
import { plansApi } from "../services/api";

const PLAN_ICONS = { basic: "◆", premium: "◈", deluxe: "⬡" };
const PLAN_COLOR = { basic: "var(--basic)", premium: "var(--premium)", deluxe: "var(--deluxe)" };

export default function PlansPage() {
  const [plans, setPlans] = useState([]);

  useEffect(() => { plansApi.list().then(r => setPlans(r.data)); }, []);

  return (
    <div>
      <div className="page-title">PLANES</div>
      <div className="page-subtitle">Catálogo de membresías disponibles</div>

      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(280px,1fr))", gap:20 }}>
        {plans.map(p => (
          <div key={p.id} className="card" style={{ borderTop:`3px solid ${PLAN_COLOR[p.name]}`, position:"relative", overflow:"hidden" }}>
            <div style={{ position:"absolute", top:16, right:16, fontSize:48, opacity:.06, fontFamily:"var(--font-head)" }}>
              {PLAN_ICONS[p.name]}
            </div>
            <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:16 }}>
              <span style={{ fontSize:28, color:PLAN_COLOR[p.name] }}>{PLAN_ICONS[p.name]}</span>
              <span className={`badge badge-${p.name}`}>{p.name.toUpperCase()}</span>
            </div>
            <div style={{ fontFamily:"var(--font-head)", fontSize:32, letterSpacing:1, marginBottom:4 }}>{p.display_name}</div>
            <div style={{ color:"var(--muted)", fontSize:13, marginBottom:20 }}>{p.description}</div>
            <div style={{ fontFamily:"var(--font-head)", fontSize:38, color:PLAN_COLOR[p.name], marginBottom:20 }}>
              ${p.price_monthly.toLocaleString("es-CO")}
              <span style={{ fontSize:16, color:"var(--muted)", fontFamily:"var(--font-body)" }}>/mes</span>
            </div>
            <ul style={{ listStyle:"none", display:"flex", flexDirection:"column", gap:8 }}>
              {p.features.map((f, i) => (
                <li key={i} style={{ fontSize:13, display:"flex", alignItems:"flex-start", gap:8 }}>
                  <span style={{ color:PLAN_COLOR[p.name], marginTop:2 }}>✓</span>
                  <span>{f}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
