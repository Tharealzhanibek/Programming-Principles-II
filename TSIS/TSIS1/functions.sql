CREATE OR REPLACE FUNCTION get_contacts_by_pattern(t TEXT)
RETURNS TABLE(first_name VARCHAR, last_name VARCHAR, phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (c.id)
        c.first_name,
        c.last_name,
        p.phone
    FROM contacts c
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE c.first_name ILIKE '%' || t || '%'
       OR c.last_name  ILIKE '%' || t || '%'
       OR p.phone      ILIKE '%' || t || '%'
    ORDER BY c.id, p.id;
END;
$$;


-- get_contacts_paginated
-- Returns a page of contacts ordered by last_name, first_name.
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(
    first_name VARCHAR,
    last_name  VARCHAR,
    phone      VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.first_name,
        c.last_name,
        COALESCE(
            (SELECT ph.phone FROM phones ph
             WHERE ph.contact_id = c.id
             ORDER BY ph.id LIMIT 1),
            '—'
        )
    FROM contacts c
    ORDER BY c.last_name, c.first_name
    LIMIT p_limit OFFSET p_offset;
END;
$$;


-- ═══════════════════════════════════════════════════════════════════════════════
-- TSIS 1 — new function
-- ═══════════════════════════════════════════════════════════════════════════════

-- search_contacts
-- Full cross-field search: matches p_query against first_name, last_name,
-- email, AND every phone number in the phones table.
-- Returns one row per matching (contact, phone) combination.
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    contact_id INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    grp        VARCHAR,
    phone      VARCHAR,
    phone_type VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (c.id, ph.id)
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        c.birthday,
        g.name        AS grp,
        ph.phone,
        ph.type       AS phone_type
    FROM contacts c
    LEFT JOIN phones ph ON ph.contact_id = c.id
    LEFT JOIN groups  g ON g.id = c.group_id
    WHERE c.first_name ILIKE '%' || p_query || '%'
       OR c.last_name  ILIKE '%' || p_query || '%'
       OR c.email      ILIKE '%' || p_query || '%'
       OR ph.phone     ILIKE '%' || p_query || '%'
    ORDER BY c.id, ph.id;
END;
$$;
