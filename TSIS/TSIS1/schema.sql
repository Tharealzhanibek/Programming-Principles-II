-- schema.sql
-- Extended PhoneBook schema for TSIS 1.
-- Run once on a fresh database (or re-run safely: IF NOT EXISTS guards).
--
-- Tables created:
--   groups   – contact categories (Family / Work / Friend / Other)
--   contacts – main contact record (replaces the old phonebook table)
--   phones   – 1-to-many phone numbers per contact
--
-- The old phonebook table is preserved via a compatibility VIEW so that
-- the Practice 7/8 stored procedures (upsert_contact, delete_contact, …)
-- keep working without modification.

-- ── 1. groups ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Seed the four default categories (safe to re-run)
INSERT INTO groups (name)
VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

-- ── 2. contacts ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS contacts (
    id         SERIAL       PRIMARY KEY,
    first_name VARCHAR(50)  NOT NULL,
    last_name  VARCHAR(50)  NOT NULL,
    email      VARCHAR(100),
    birthday   DATE,
    group_id   INTEGER      REFERENCES groups(id) ON DELETE SET NULL,
    created_at TIMESTAMP    DEFAULT NOW()
);

-- Unique index: (first_name, last_name) pair must be unique
CREATE UNIQUE INDEX IF NOT EXISTS idx_contacts_fullname
    ON contacts (first_name, last_name);

-- ── 3. phones ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL      PRIMARY KEY,
    contact_id INTEGER     NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) DEFAULT 'mobile'
                           CHECK (type IN ('home', 'work', 'mobile'))
);

CREATE INDEX IF NOT EXISTS idx_phones_contact_id ON phones (contact_id);

-- ── 4. phonebook (backward-compatibility view for Practice 7/8 procedures) ────
-- Exposes one row per contact with its first registered phone number so that
-- old procedures (upsert_contact, get_contacts_by_pattern, …) still compile.
CREATE OR REPLACE VIEW phonebook AS
    SELECT
        c.id,
        c.first_name,
        c.last_name,
        COALESCE(
            (SELECT p.phone FROM phones p
             WHERE p.contact_id = c.id
             ORDER BY p.id LIMIT 1),
            ''
        ) AS phone
    FROM contacts c;
