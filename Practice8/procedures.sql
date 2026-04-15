CREATE OR REPLACE PROCEDURE upsert_contact(p_first_name VARCHAR, p_last_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_first_name) THEN
        UPDATE phonebook SET phone = p_phone WHERE first_name = p_first_name;
    ELSE
        INSERT INTO phonebook (first_name, last_name, phone) VALUES (p_first_name, p_last_name, p_phone);
    END IF; 
END;
$$;

CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names VARCHAR[],
    p_last_names VARCHAR[],
    p_phones VARCHAR[]
)
LANGUAGE plpgsql as $$ 
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 1..array_length(p_names, 1) 
    LOOP 
        IF p_phones[i] ~ '^\+?[0-9]+$' THEN
            CALL upsert_contact(p_names[i], p_last_names[i], p_phones[i]);
        ELSE
            RAISE NOTICE 'Invalid record skipped: Name=% %, Phone=%',
                            p_names[i], p_last_names[i], p_phones[i];
        END IF;
    END LOOP;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_contact(
    p_search_term VARCHAR
)
LANGUAGE plpgsql as $$ 
BEGIN 
    DELETE FROM phonebook
    WHERE first_name = p_search_term
        OR first_name = p_search_term
        OR first_name = p_search_term;

    IF NOT FOUND THEN
        RAISE NOTICE 'No contact found matchong: %', p_search_term;
    END IF;
END;
$$;