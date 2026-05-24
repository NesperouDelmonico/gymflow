// src/pages/MembershipsPage.jsx
import { useEffect, useState } from "react";
import { membershipsApi, plansApi, usersApi } from "../services/api";

const STATUS_OPTS = ["active","paused","cancelled","expired"];

function MembershipModal({ onClose, onSave, plans, users, editing }) {
  const [form, setForm] = useState(
    editing
      ? { plan_id: editing.plan_id, status: editing.status, end_date: editing.end_date, auto_renew: editing.auto_renew, notes: editing.notes || "" }
      : { user_id: "", plan_id: "", start_date: new Date().toISOString().slice(0,10), end_date: "", auto_renew: true, notes: "" }
  );
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");

  const submit = async () => {
    setErr(""); setSaving(true);
    try {
      if (editing) await onSave(editing.id, form);
      else await onSave(form);
      onClose();
    } catch(e) {
      setErr(e.response?.data?.detail || "Error al guardar.");
    } finally { setSaving(false); }
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <h2>{editing ? "EDITAR MEMBRESÍA" : "NUEVA MEMBRESÍA"}</h2>
        {err && <div className="alert alert-error">{err}</div>}

        <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
          {!editing && (
            <div className="form-group">
              <label>Usuario</label>
              <select className="input" value={form.user_id} onChange={e => setForm({...form, user_id: e.target.value})}>
                <option value="">Selecciona usuario...</option>
                {users.map(u => <option key={u.id} value={u.id}>{u.full_name} — {u.email}</option>)}
              </select>
            </div>
          )}
          <div className="form-group">
            <label>Plan</label>
            <select className="input" value={form.plan_id} onChange={e => setForm({...form, plan_id: e.target.value})}>
              <option value="">Selecciona plan...</option>
              {plans.map(p => <option key={p.id} value={p.id}>{p.display_name} — ${p.price_monthly.toLocaleString()}/mes</option>)}
            </select>
          </div>
          {editing && (
            <div className="form-group">
              <label>Estado</label>
              <select className="input" value={form.status} onChange={e => setForm({...form, status: e.target.value})}>
                {STATUS_OPTS.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          )}
          {!editing && (
            <div className="form-group">
              <label>Fecha de inicio</label>
              <input className="input" type="date" value={form.start_date} onChange={e => setForm({...form, start_date: e.target.value})} />
            </div>
          )}
          <div className="form-group">
            <label>Fecha de fin</label>
            <input className="input" type="date" value={form.end_date} onChange={e => setForm({...form, end_date: e.target.value})} />
          </div>
          <div className="form-group" style={{ flexDirection:"row", alignItems:"center", gap:10 }}>
            <input type="checkbox" id="renew" checked={form.auto_renew} onChange={e => setForm({...form, auto_renew: e.target.checked})} />
            <label htmlFor="renew" style={{ color:"var(--text)" }}>Renovación automática</label>
          </div>
          <div className="form-group">
            <label>Notas (opcional)</label>
            <input className="input" value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} placeholder="Observaciones..." />
          </div>

          <div style={{ display:"flex", gap:10, marginTop:8 }}>
            <button className="btn btn-primary" onClick={submit} disabled={saving} style={{ flex:1, justifyContent:"center" }}>
              {saving ? "Guardando..." : "Guardar"}
            </button>
            <button className="btn btn-ghost" onClick={onClose}>Cancelar</button>
          </div>
        </div>
      </div>
    </div>
  );
}

const PLAN_COLORS = { basic:"basic", premium:"premium", deluxe:"deluxe" };

export default function MembershipsPage() {
  const [memberships, setMemberships] = useState([]);
  const [plans, setPlans]   = useState([]);
  const [users, setUsers]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal]   = useState(false);
  const [editing, setEditing] = useState(null);
  const [search, setSearch] = useState("");

  const load = async () => {
    setLoading(true);
    const [m, p, u] = await Promise.all([
      membershipsApi.list(), plansApi.list(), usersApi.list(),
    ]);
    setMemberships(m.data); setPlans(p.data); setUsers(u.data);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (data) => { await membershipsApi.create(data); load(); };
  const handleUpdate = async (id, data) => { await membershipsApi.update(id, data); load(); };
  const handleDelete = async (id) => {
    if (!confirm("¿Eliminar esta membresía?")) return;
    await membershipsApi.delete(id); load();
  };

  const filtered = memberships.filter(m =>
    m.user_name?.toLowerCase().includes(search.toLowerCase()) ||
    m.user_email?.toLowerCase().includes(search.toLowerCase()) ||
    m.plan_name?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="page-title">MEMBRESÍAS</div>
      <div className="page-subtitle">Gestiona las membresías de todos los miembros</div>

      <div style={{ display:"flex", gap:12, marginBottom:24 }}>
        <input
          className="input"
          style={{ maxWidth:320 }}
          placeholder="Buscar por nombre, email o plan..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <button className="btn btn-primary" onClick={() => { setEditing(null); setModal(true); }}>
          + Nueva membresía
        </button>
      </div>

      <div className="card" style={{ padding:0 }}>
        {loading ? (
          <div style={{ padding:40, textAlign:"center", color:"var(--muted)" }}>Cargando...</div>
        ) : filtered.length === 0 ? (
          <div className="empty"><div className="empty-icon">◈</div><div>No hay membresías</div></div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Miembro</th>
                  <th>Plan</th>
                  <th>Estado</th>
                  <th>Vence</th>
                  <th>Precio</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(m => (
                  <tr key={m.id}>
                    <td>
                      <div style={{ fontWeight:600 }}>{m.user_name}</div>
                      <div style={{ fontSize:12, color:"var(--muted)" }}>{m.user_email}</div>
                    </td>
                    <td>
                      <span className={`badge badge-${PLAN_COLORS[m.plan_name] || "basic"}`}>
                        {m.plan_display_name}
                      </span>
                    </td>
                    <td><span className={`badge badge-${m.status}`}>{m.status}</span></td>
                    <td style={{ color: new Date(m.end_date) < new Date() ? "var(--danger)" : "inherit" }}>
                      {new Date(m.end_date).toLocaleDateString("es-CO")}
                    </td>
                    <td style={{ fontWeight:600 }}>
                      ${m.price_monthly?.toLocaleString()}<span style={{ fontSize:11, color:"var(--muted)" }}>/mes</span>
                    </td>
                    <td>
                      <div style={{ display:"flex", gap:8 }}>
                        <button className="btn btn-ghost btn-sm" onClick={() => { setEditing(m); setModal(true); }}>Editar</button>
                        <button className="btn btn-danger btn-sm" onClick={() => handleDelete(m.id)}>Eliminar</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {modal && (
        <MembershipModal
          onClose={() => setModal(false)}
          onSave={editing ? handleUpdate : handleCreate}
          plans={plans} users={users}
          editing={editing}
        />
      )}
    </div>
  );
}
