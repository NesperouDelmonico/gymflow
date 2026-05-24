-- ============================================================
-- GymFlow - Modelo Relacional para Supabase / PostgreSQL
-- ============================================================

-- Extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- TABLA: roles
-- ============================================================
CREATE TABLE roles (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(50) NOT NULL UNIQUE,  -- 'admin' | 'user'
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO roles (name, description) VALUES
    ('admin', 'Administrador del gimnasio'),
    ('user',  'Usuario / miembro del gimnasio');

-- ============================================================
-- TABLA: users
-- ============================================================
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_id       UUID NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    full_name     VARCHAR(150) NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    phone         VARCHAR(20),
    password_hash TEXT NOT NULL,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email   ON users(email);
CREATE INDEX idx_users_role_id ON users(role_id);

-- ============================================================
-- TABLA: membership_plans
-- ============================================================
CREATE TABLE membership_plans (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name          VARCHAR(50)    NOT NULL UNIQUE,  -- 'basic' | 'premium' | 'deluxe'
    display_name  VARCHAR(100)   NOT NULL,
    description   TEXT,
    price_monthly NUMERIC(10,2)  NOT NULL,
    features      JSONB          NOT NULL DEFAULT '[]',  -- lista de beneficios
    is_active     BOOLEAN        NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

INSERT INTO membership_plans (name, display_name, description, price_monthly, features) VALUES
(
    'basic', 'Plan Básico',
    'Acceso esencial al gimnasio para comenzar tu camino fitness.',
    29900,
    '["Acceso a zona cardiovascular","Acceso a pesas libres","Casillero personal","Horario estándar (6am - 10pm)"]'
),
(
    'premium', 'Plan Premium',
    'Más herramientas y flexibilidad para llevar tu entrenamiento al siguiente nivel.',
    59900,
    '["Todo lo del plan Básico","Clases grupales ilimitadas","Acceso a zona de spa","Asesor nutricional mensual","Horario extendido (5am - 11pm)"]'
),
(
    'deluxe', 'Plan Deluxe',
    'La experiencia fitness más completa, sin límites.',
    99900,
    '["Todo lo del plan Premium","Entrenador personal 2x/semana","Acceso 24/7","Invitado gratis 1x/mes","Evaluación física trimestral","Acceso a todas las sedes"]'
);

-- ============================================================
-- TABLA: memberships  (asignación de plan a usuario)
-- ============================================================
CREATE TABLE memberships (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id       UUID NOT NULL REFERENCES membership_plans(id) ON DELETE RESTRICT,
    status        VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','paused','cancelled','expired')),
    start_date    DATE        NOT NULL DEFAULT CURRENT_DATE,
    end_date      DATE        NOT NULL,
    auto_renew    BOOLEAN     NOT NULL DEFAULT TRUE,
    notes         TEXT,
    created_by    UUID REFERENCES users(id) ON DELETE SET NULL,  -- admin que creó
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_memberships_user_id  ON memberships(user_id);
CREATE INDEX idx_memberships_plan_id  ON memberships(plan_id);
CREATE INDEX idx_memberships_status   ON memberships(status);
CREATE INDEX idx_memberships_end_date ON memberships(end_date);

-- ============================================================
-- TABLA: membership_history  (auditoría de cambios)
-- ============================================================
CREATE TABLE membership_history (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    membership_id  UUID NOT NULL REFERENCES memberships(id) ON DELETE CASCADE,
    changed_by     UUID REFERENCES users(id) ON DELETE SET NULL,
    previous_plan  UUID REFERENCES membership_plans(id),
    new_plan       UUID REFERENCES membership_plans(id),
    previous_status VARCHAR(20),
    new_status      VARCHAR(20),
    reason          TEXT,
    changed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_membership_history_membership_id ON membership_history(membership_id);

-- ============================================================
-- TRIGGER: updated_at automático
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_plans_updated_at
    BEFORE UPDATE ON membership_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_memberships_updated_at
    BEFORE UPDATE ON memberships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- TRIGGER: auditoría automática en memberships
-- ============================================================
CREATE OR REPLACE FUNCTION log_membership_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (OLD.plan_id IS DISTINCT FROM NEW.plan_id) OR
       (OLD.status IS DISTINCT FROM NEW.status) THEN
        INSERT INTO membership_history (
            membership_id, changed_by, previous_plan, new_plan,
            previous_status, new_status
        ) VALUES (
            NEW.id, NEW.created_by, OLD.plan_id, NEW.plan_id,
            OLD.status, NEW.status
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_memberships_audit
    AFTER UPDATE ON memberships
    FOR EACH ROW EXECUTE FUNCTION log_membership_changes();

-- ============================================================
-- VISTA: memberships con info completa (útil para el backend)
-- ============================================================
CREATE VIEW v_memberships_full AS
SELECT
    m.id,
    m.status,
    m.start_date,
    m.end_date,
    m.auto_renew,
    m.notes,
    m.created_at,
    m.updated_at,
    u.id          AS user_id,
    u.full_name   AS user_name,
    u.email       AS user_email,
    u.phone       AS user_phone,
    p.id          AS plan_id,
    p.name        AS plan_name,
    p.display_name AS plan_display_name,
    p.price_monthly,
    p.features
FROM memberships m
JOIN users       u ON u.id = m.user_id
JOIN membership_plans p ON p.id = m.plan_id;
