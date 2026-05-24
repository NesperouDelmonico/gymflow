// src/pages/UsersPage.jsx
import { useEffect, useState } from "react";
import { usersApi } from "../services/api";

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => { usersApi.list().then(r => setUsers(r.data)); }, []);

  const filtered = users.filter(u =>
    u.full_name.toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="page-title">USUARIOS</div>
      <div className="page-subtitle">Todos los miembros registrados en el sistema</div>

      <input
        className="input"
        style={{ maxWidth:320, marginBottom:20 }}
        placeholder="Buscar por nombre o email..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />

      <div className="card" style={{ padding:0 }}>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Miembro</th>
                <th>Email</th>
                <th>Teléfono</th>
                <th>Rol</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(u => (
                <tr key={u.id}>
                  <td>
                    <div style={{ display:"flex", alignItems:"center", gap:10 }}>
                      <div style={{ width:32, height:32, background:"var(--bg3)", borderRadius:"50%", display:"grid", placeItems:"center", fontWeight:700, fontSize:13, flexShrink:0 }}>
                        {u.full_name[0]}
                      </div>
                      <span style={{ fontWeight:600 }}>{u.full_name}</span>
                    </div>
                  </td>
                  <td style={{ color:"var(--muted)" }}>{u.email}</td>
                  <td style={{ color:"var(--muted)" }}>{u.phone || "—"}</td>
                  <td>
                    <span className={`badge ${u.role_name === "admin" ? "badge-premium" : "badge-active"}`}>
                      {u.role_name}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${u.is_active ? "badge-active" : "badge-cancelled"}`}>
                      {u.is_active ? "activo" : "inactivo"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filtered.length === 0 && (
          <div className="empty"><div className="empty-icon">◉</div><div>Sin usuarios</div></div>
        )}
      </div>
    </div>
  );
}
