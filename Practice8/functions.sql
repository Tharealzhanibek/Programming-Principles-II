CREATE OR REPLACE FUNCTION get_contacts_by_pattern(t text)
RETURNS TABLE(first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT p.first_name, p.last_name, p.phone FROM phonebook p
        WHERE p.first_name ILIKE '%' || t || '%'
        OR p.last_name ILIKE '%' || t || '%'
        OR p.phone ILIKE '%' || t || '%'; 
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offest INT)
RETURNS TABLE(first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT pb.first_name, pb.last_name, pb.phone
    FROM phonebook pb
    ORDER BY pb.last_name, pb.first_name
    LIMIT p_limit OFFSET p_offest;
END;
$$ LANGUAGE plpgsql
