# GymFlow — Sistema de Gestión de Membresías

🔗 **[Acceder a la aplicación](https://gymflow-three-alpha.vercel.app/login)**

---

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | React 18 + Vite + React Router |
| Backend | Python 3.11 + FastAPI (async) |
| Base de datos | PostgreSQL (Supabase) |
| ORM | SQLAlchemy 2.0 async |
| Auth | JWT (python-jose) + bcrypt |
| Deploy Frontend | Vercel |
| Deploy Backend | Render |

---

## Arquitectura

### Backend — Arquitectura Hexagonal

```
backend/
├── main.py
└── src/
    ├── domain/                  # Núcleo — sin dependencias externas
    │   ├── entities/
    │   │   ├── __init__.py      # Re-exporta todas las entidades
    │   │   ├── membership.py    # Membership + MembershipStatus
    │   │   ├── plan.py          # MembershipPlan + PlanType
    │   │   └── user.py          # User
    │   └── repositories/        # Interfaces (puertos de salida)
    ├── application/             # Casos de uso + DTOs
    │   ├── use_cases/
    │   └── dtos/
    └── infrastructure/          # Adaptadores
        ├── database/
        │   ├── models.py        # SQLAlchemy ORM
        │   └── repositories/   # Implementaciones concretas
        └── api/
            ├── routes/          # Endpoints FastAPI
            └── dependencies.py  # Inyección de dependencias
```

**Patrones aplicados:**
- **Hexagonal (Ports & Adapters):** El dominio no conoce FastAPI ni SQLAlchemy
- **Repository Pattern:** Abstracción de la persistencia
- **Dependency Injection:** FastAPI `Depends()` resuelve las dependencias
- **Command/DTO Pattern:** DTOs tipados con Pydantic v2

**Principios SOLID:**
- **S** – Cada entidad en su propio archivo; cada use case hace una sola cosa
- **O** – Nuevos repositorios extienden la interfaz sin modificar el dominio
- **L** – Los repositorios concretos sustituyen a las interfaces sin romper nada
- **I** – Interfaces separadas por entidad (`IMembershipRepository`, `IPlanRepository`…)
- **D** – Los use cases dependen de abstracciones, nunca de SQLAlchemy directamente

---

## Dominio

Las entidades están separadas por responsabilidad en archivos individuales:

### `domain/entities/membership.py`
Contiene `Membership` y `MembershipStatus`. Incluye las reglas de negocio: cancelar, pausar y reactivar una membresía.

### `domain/entities/plan.py`
Contiene `MembershipPlan` y `PlanType` (basic, premium, deluxe).

### `domain/entities/user.py`
Contiene `User` con sus atributos de perfil y rol.

### `domain/entities/__init__.py`
Re-exporta todas las clases para mantener compatibilidad con imports existentes en el resto del proyecto.

---

## Despliegue

| Servicio | URL |
|---|---|
| Frontend (Vercel) | https://gymflow-three-alpha.vercel.app |
| Backend (Render) | https://gymflow-05q8.onrender.com |
| API Docs | https://gymflow-05q8.onrender.com/docs |

> **Nota:** El plan gratuito de Render suspende el servicio tras 15 minutos de inactividad. La primera petición puede tardar ~30 segundos en responder mientras el servidor se reactiva.

---

## Setup local

### 1. Base de datos (Supabase)

1. Crea un proyecto en [supabase.com](https://supabase.com)
2. En SQL Editor, ejecuta `database_schema.sql`
3. Copia la cadena de conexión del proyecto

### 2. Backend

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux / Mac
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edita .env con tu DATABASE_URL de Supabase y un SECRET_KEY seguro

uvicorn main:app --reload --port 8000
```

API disponible en `http://localhost:8000`
Docs interactivos: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install

# Crea .env.local con:
# VITE_API_URL=http://localhost:8000

npm run dev
```

App disponible en `http://localhost:5173`

---

## Flujo de uso

### Administrador
1. Crear usuarios desde `POST /auth/register`
2. Asignar membresías en la pantalla "Membresías"
3. Ver estadísticas en Dashboard
4. Actualizar o cancelar membresías con un clic

### Usuario / Miembro
- Ve su plan activo, fechas y precio en "Mi Membresía"

---

## Endpoints principales

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/auth/register` | Público | Registrar usuario |
| POST | `/auth/login` | Público | Login (JWT) |
| GET | `/auth/me` | Auth | Perfil propio |
| GET | `/plans/` | Auth | Listar planes |
| GET | `/memberships/` | Admin | Listar todas |
| POST | `/memberships/` | Admin | Crear membresía |
| PUT | `/memberships/{id}` | Admin | Actualizar |
| DELETE | `/memberships/{id}` | Admin | Eliminar |
| GET | `/memberships/my` | Auth | Mis membresías |
| GET | `/users/` | Admin | Listar usuarios |

---

## Modelo de datos

```
roles ──< users ──< memberships >── membership_plans
                         │
                  membership_history
```

Los triggers de PostgreSQL manejan:
- `updated_at` automático en todas las tablas
- Auditoría automática de cambios en membresías
