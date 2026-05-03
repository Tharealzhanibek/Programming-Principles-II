-- procedures.sql
-- Contains:
--   • Updated versions of Practice 7/8 procedures to work with the new schema
--   • Three new TSIS 1 procedures: add_phone, move_to_group
--   • Updated bulk-insert procedure that accepts email/birthday/group

-- ═══════════════════════════════════════════════════════════════════════════════
-- Practice 7/8 procedures  (updated for new contacts/phones schema)
-- ═══════════════════════════════════════════════════════════════════════════════

-- upsert_contact
-- If a contact with the given first_name already exists, update its primary phone.
-- Otherwise insert a new contact + phone row.
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_first_name VARCHAR,
    p_last_name  VARCHAR,
    p_phone      VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE first_name = p_first_name AND last_name = p_last_name;

    IF FOUND THEN
        -- update or insert the first phone for this contact
        IF EXISTS (SELECT 1 FROM phones WHERE contact_id = v_contact_id LIMIT 1) THEN
            UPDATE phones
            SET phone = p_phone
            WHERE contact_id = v_contact_id
              AND id = (SELECT MIN(id) FROM phones WHERE contact_id = v_contact_id);
        ELSE
            INSERT INTO phones (contact_id, phone, type)
            VALUES (v_contact_id, p_phone, 'mobile');
        END IF;
    ELSE
        INSERT INTO contacts (first_name, last_name)
        VALUES (p_first_name, p_last_name)
        RETURNING id INTO v_contact_id;

        INSERT INTO phones (contact_id, phone, type)
        VALUES (v_contact_id, p_phone, 'mobile');
    END IF;
END;
$$;


-- insert_many_contacts
-- Bulk-insert contacts from parallel arrays; skips rows with invalid phones.
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names      VARCHAR[],
    p_last_names VARCHAR[],
    p_phones     VARCHAR[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 1..array_length(p_names, 1) LOOP
        IF p_phones[i] ~ '^\+?[0-9]+$' THEN
            CALL upsert_contact(p_names[i], p_last_names[i], p_phones[i]);
        ELSE
            RAISE NOTICE 'Invalid record skipped: % % — phone: %',
                p_names[i], p_last_names[i], p_phones[i];
        END IF;
    END LOOP;
END;
$$;


-- delete_contact
-- Deletes a contact matching the given first_name, last_name, or phone.
CREATE OR REPLACE PROCEDURE delete_contact(p_search_term VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_deleted INTEGER := 0;
BEGIN
    WITH deleted AS (
        DELETE FROM contacts
        WHERE first_name  = p_search_term
           OR last_name   = p_search_term
           OR id IN (
               SELECT contact_id FROM phones WHERE phone = p_search_term
           )
        RETURNING id
    )
    SELECT COUNT(*) INTO v_deleted FROM deleted;

    IF v_deleted = 0 THEN
        RAISE NOTICE 'No contact found matching: %', p_search_term;
    ELSE
        RAISE NOTICE 'Deleted % contact(s).', v_deleted;
    END IF;
END;
$$;


-- ═══════════════════════════════════════════════════════════════════════════════
-- TSIS 1 — new procedures
-- ═══════════════════════════════════════════════════════════════════════════════

-- add_phone
-- Adds a new phone number (with optional type) to an existing contact.
-- Raises a notice if the contact is not found.
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,   -- matched against first_name
    p_phone        VARCHAR,
    p_type         VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- look up the contact by first_name (or full "first last" match)
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE first_name = p_contact_name
       OR (first_name || ' ' || last_name) = p_contact_name
    LIMIT 1;

    IF NOT FOUND THEN
        RAISE NOTICE 'Contact "%" not found — phone not added.', p_contact_name;
        RETURN;
    END IF;

    -- validate phone type
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE NOTICE 'Invalid phone type "%" — must be home / work / mobile.', p_type;
        RETURN;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to contact id %.', p_phone, p_type, v_contact_id;
END;
$$;


-- move_to_group
-- Assigns a contact to a group; creates the group if it does not exist.
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,   -- matched against first_name or "first last"
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- ensure group exists (create if missing)
    INSERT INTO groups (name) VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    -- find the contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE first_name = p_contact_name
       OR (first_name || ' ' || last_name) = p_contact_name
    LIMIT 1;

    IF NOT FOUND THEN
        RAISE NOTICE 'Contact "%" not found.', p_contact_name;
        RETURN;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;

    RAISE NOTICE 'Contact id % moved to group "%".', v_contact_id, p_group_name;
END;
$$;
