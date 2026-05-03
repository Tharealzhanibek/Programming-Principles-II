import csv
import json
import os
import sys
from datetime import date, datetime

import psycopg2

from connect import get_connection

# ── display helpers ────────────────────────────────────────────────────────────
SEP  = "─" * 74
SEP2 = "═" * 74
PAGE_SIZE = 5     # contacts shown per paginated page


def _header(title: str) -> None:
    print(f"\n{SEP2}\n  {title}\n{SEP2}")


def _print_row(i, first, last, email, birthday, grp, phones):
    """Print one contact record in a readable format."""
    bday = str(birthday) if birthday else "—"
    grp  = grp or "—"
    ph   = ", ".join(f"{p} ({t})" for p, t in phones) if phones else "—"
    print(f"  {i:>3}. {first} {last}")
    print(f"       Email: {email or '—'}   Birthday: {bday}   Group: {grp}")
    print(f"       Phones: {ph}")
    print(f"       {SEP}")


# ── database query helpers ─────────────────────────────────────────────────────

def _fetch_contact_phones(cur, contact_id: int) -> list[tuple]:
    """Return list of (phone, type) for a given contact_id."""
    cur.execute(
        "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
        (contact_id,)
    )
    return cur.fetchall()


def _get_or_create_group(cur, group_name: str) -> int:
    """Return group_id, inserting the group if it does not exist."""
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO groups (name) VALUES (%s) RETURNING id",
        (group_name,)
    )
    return cur.fetchone()[0]


# ══════════════════════════════════════════════════════════════════════════════
# 1. Add a contact
# ══════════════════════════════════════════════════════════════════════════════

def add_contact(conn) -> None:
    """Prompt the user for full contact details and insert into the DB."""
    _header("Add Contact")
    first    = input("  First name : ").strip()
    last     = input("  Last name  : ").strip()
    email    = input("  Email      : ").strip() or None
    bday_raw = input("  Birthday (YYYY-MM-DD, blank to skip): ").strip()
    birthday = bday_raw if bday_raw else None

    # group selection
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM groups ORDER BY name")
        groups = cur.fetchall()

    print("  Groups:")
    for gid, gname in groups:
        print(f"    {gid}. {gname}")
    gid_raw   = input("  Enter group id (blank for none): ").strip()
    group_id  = int(gid_raw) if gid_raw.isdigit() else None

    # phone
    phone     = input("  Phone number : ").strip()
    phone_type = input("  Phone type [mobile/home/work] (default mobile): ").strip() or "mobile"
    if phone_type not in ("mobile", "home", "work"):
        phone_type = "mobile"

    try:
        with conn.cursor() as cur:
            # insert contact
            cur.execute(
                """
                INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (first_name, last_name) DO NOTHING
                RETURNING id
                """,
                (first, last, email, birthday, group_id)
            )
            row = cur.fetchone()
            if row is None:
                print(f"  ⚠ Contact '{first} {last}' already exists — use upsert or update.")
                conn.rollback()
                return
            contact_id = row[0]

            # insert phone
            if phone:
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                    (contact_id, phone, phone_type)
                )
        conn.commit()
        print(f"  ✓ Contact '{first} {last}' added (id={contact_id}).")
    except psycopg2.Error as exc:
        conn.rollback()
        print(f"  ✗ Database error: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. Add an extra phone to an existing contact  (calls add_phone procedure)
# ══════════════════════════════════════════════════════════════════════════════

def add_extra_phone(conn) -> None:
    """Add a new phone number to an existing contact via the add_phone procedure."""
    _header("Add Phone to Contact")
    name  = input("  Contact first name (or 'First Last'): ").strip()
    phone = input("  New phone number: ").strip()
    ptype = input("  Type [mobile/home/work] (default mobile): ").strip() or "mobile"

    try:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        print("  ✓ Done (see server notices above).")
    except psycopg2.Error as exc:
        conn.rollback()
        print(f"  ✗ {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# 3. Paginated listing  (uses get_contacts_paginated DB function)
# ══════════════════════════════════════════════════════════════════════════════

def list_contacts_paged(conn) -> None:
    """Navigate all contacts page-by-page using the existing DB function."""
    _header("All Contacts (paginated)")
    page = 0

    while True:
        offset = page * PAGE_SIZE
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM get_contacts_paginated(%s, %s)",
                (PAGE_SIZE, offset)
            )
            rows = cur.fetchall()

        if not rows and page == 0:
            print("  No contacts found.")
            return

        if not rows:
            print("  (end of list)")
            page = max(0, page - 1)
            continue

        print(f"\n  Page {page + 1}  (offset {offset})")
        print(f"  {SEP}")
        for i, (first, last, phone) in enumerate(rows, start=offset + 1):
            print(f"  {i:>3}. {first} {last:<20}  📞 {phone}")
        print(f"  {SEP}")

        cmd = input("  [n]ext  [p]rev  [q]uit: ").strip().lower()
        if cmd == "n":
            page += 1
        elif cmd == "p":
            page = max(0, page - 1)
        elif cmd == "q":
            break


# ══════════════════════════════════════════════════════════════════════════════
# 4. Full search  (calls search_contacts DB function)
# ══════════════════════════════════════════════════════════════════════════════

def search_contacts(conn) -> None:
    """Search across first name, last name, email, and all phone numbers."""
    _header("Search Contacts")
    query = input("  Search (name / email / phone fragment): ").strip()
    if not query:
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()
    except psycopg2.Error as exc:
        print(f"  ✗ {exc}")
        return

    if not rows:
        print("  No results.")
        return

    print(f"\n  {len(rows)} result(s):\n  {SEP}")
    # group rows by contact_id for display
    seen: dict = {}
    for cid, first, last, email, bday, grp, phone, ptype in rows:
        if cid not in seen:
            seen[cid] = {"first": first, "last": last, "email": email,
                         "bday": bday, "grp": grp, "phones": []}
        if phone:
            seen[cid]["phones"].append((phone, ptype))

    for i, (cid, d) in enumerate(seen.items(), 1):
        _print_row(i, d["first"], d["last"], d["email"],
                   d["bday"], d["grp"], d["phones"])


# ══════════════════════════════════════════════════════════════════════════════
# 5. Search by email  (partial match)
# ══════════════════════════════════════════════════════════════════════════════

def search_by_email(conn) -> None:
    """Filter contacts whose email matches a fragment (e.g. 'gmail')."""
    _header("Search by Email")
    fragment = input("  Email fragment: ").strip()
    if not fragment:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.id, c.first_name, c.last_name, c.email,
                       c.birthday, g.name AS grp
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                WHERE c.email ILIKE %s
                ORDER BY c.last_name, c.first_name
                """,
                (f"%{fragment}%",)
            )
            rows = cur.fetchall()
    except psycopg2.Error as exc:
        print(f"  ✗ {exc}")
        return

    if not rows:
        print("  No contacts match that email fragment.")
        return

    print(f"\n  {len(rows)} result(s):\n  {SEP}")
    for i, (cid, first, last, email, bday, grp) in enumerate(rows, 1):
        with conn.cursor() as cur:
            phones = _fetch_contact_phones(cur, cid)
        _print_row(i, first, last, email, bday, grp, phones)


# ══════════════════════════════════════════════════════════════════════════════
# 6. Filter by group + optional sort
# ══════════════════════════════════════════════════════════════════════════════

def filter_by_group(conn) -> None:
    """Show contacts belonging to a selected group with a chosen sort order."""
    _header("Filter by Group")

    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM groups ORDER BY name")
        groups = cur.fetchall()

    if not groups:
        print("  No groups found.")
        return

    print("  Available groups:")
    for gid, gname in groups:
        print(f"    {gid}. {gname}")
    gid_raw = input("  Enter group id: ").strip()
    if not gid_raw.isdigit():
        print("  Invalid input.")
        return
    group_id = int(gid_raw)

    print("  Sort by:  1) Name  2) Birthday  3) Date added")
    sort_choice = input("  Choice [1]: ").strip() or "1"
    sort_map = {"1": "c.last_name, c.first_name",
                "2": "c.birthday NULLS LAST",
                "3": "c.created_at"}
    order_by = sort_map.get(sort_choice, "c.last_name, c.first_name")

    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT c.id, c.first_name, c.last_name, c.email,
                       c.birthday, g.name AS grp
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                WHERE c.group_id = %s
                ORDER BY {order_by}
                """,
                (group_id,)
            )
            rows = cur.fetchall()
    except psycopg2.Error as exc:
        print(f"  ✗ {exc}")
        return

    if not rows:
        print("  No contacts in this group.")
        return

    print(f"\n  {len(rows)} contact(s):\n  {SEP}")
    for i, (cid, first, last, email, bday, grp) in enumerate(rows, 1):
        with conn.cursor() as cur2:
            phones = _fetch_contact_phones(cur2, cid)
        _print_row(i, first, last, email, bday, grp, phones)


# ══════════════════════════════════════════════════════════════════════════════
# 7. Move contact to group  (calls move_to_group procedure)
# ══════════════════════════════════════════════════════════════════════════════

def move_to_group(conn) -> None:
    """Move a contact to a group (creates the group if it doesn't exist)."""
    _header("Move Contact to Group")
    name  = input("  Contact first name (or 'First Last'): ").strip()
    group = input("  Target group name: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
        print("  ✓ Done.")
    except psycopg2.Error as exc:
        conn.rollback()
        print(f"  ✗ {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# 8. Delete contact  (calls existing delete_contact procedure)
# ══════════════════════════════════════════════════════════════════════════════

def delete_contact(conn) -> None:
    """Delete a contact by first name, last name, or phone number."""
    _header("Delete Contact")
    term = input("  First name / last name / phone: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute("CALL delete_contact(%s)", (term,))
        conn.commit()
        print("  ✓ Done.")
    except psycopg2.Error as exc:
        conn.rollback()
        print(f"  ✗ {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# 9. Export to JSON
# ══════════════════════════════════════════════════════════════════════════════

def export_to_json(conn) -> None:
    """Export every contact (with all phones and group) to a JSON file."""
    _header("Export to JSON")
    filename = input("  Output filename [contacts.json]: ").strip() or "contacts.json"

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.id, c.first_name, c.last_name, c.email,
                       c.birthday, g.name AS grp, c.created_at
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                ORDER BY c.last_name, c.first_name
                """
            )
            contacts = cur.fetchall()

            records = []
            for cid, first, last, email, bday, grp, created in contacts:
                cur.execute(
                    "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
                    (cid,)
                )
                phones = [{"phone": p, "type": t} for p, t in cur.fetchall()]
                records.append({
                    "first_name": first,
                    "last_name":  last,
                    "email":      email,
                    "birthday":   str(bday) if bday else None,
                    "group":      grp,
                    "phones":     phones,
                    "created_at": str(created),
                })

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        print(f"  ✓ Exported {len(records)} contact(s) to '{filename}'.")
    except (psycopg2.Error, OSError) as exc:
        print(f"  ✗ {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# 10. Import from JSON  (skip or overwrite on duplicate)
# ══════════════════════════════════════════════════════════════════════════════

def import_from_json(conn) -> None:
    """
    Read contacts from a JSON file and insert into the DB.
    On duplicate (same first+last name) ask: skip or overwrite.
    """
    _header("Import from JSON")
    filename = input("  JSON filename [contacts.json]: ").strip() or "contacts.json"

    if not os.path.exists(filename):
        print(f"  ✗ File '{filename}' not found.")
        return

    try:
        with open(filename, encoding="utf-8") as f:
            records = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"  ✗ Cannot read file: {exc}")
        return

    inserted = skipped = overwritten = 0

    for rec in records:
        first = rec.get("first_name", "").strip()
        last  = rec.get("last_name",  "").strip()
        if not first or not last:
            print(f"  ⚠ Skipping record with missing name: {rec}")
            skipped += 1
            continue

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM contacts WHERE first_name = %s AND last_name = %s",
                    (first, last)
                )
                existing = cur.fetchone()

                if existing:
                    ans = input(
                        f"  Duplicate: '{first} {last}' — [s]kip / [o]verwrite? "
                    ).strip().lower()
                    if ans != "o":
                        skipped += 1
                        continue

                    cid = existing[0]
                    # update contact fields
                    group_id = _get_or_create_group(cur, rec["group"]) \
                               if rec.get("group") else None
                    cur.execute(
                        """
                        UPDATE contacts
                        SET email = %s, birthday = %s, group_id = %s
                        WHERE id = %s
                        """,
                        (rec.get("email"), rec.get("birthday"), group_id, cid)
                    )
                    # replace phones
                    cur.execute("DELETE FROM phones WHERE contact_id = %s", (cid,))
                    for ph in rec.get("phones", []):
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (cid, ph["phone"], ph.get("type", "mobile"))
                        )
                    overwritten += 1

                else:
                    group_id = _get_or_create_group(cur, rec["group"]) \
                               if rec.get("group") else None
                    cur.execute(
                        """
                        INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (first, last, rec.get("email"), rec.get("birthday"), group_id)
                    )
                    cid = cur.fetchone()[0]
                    for ph in rec.get("phones", []):
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (cid, ph["phone"], ph.get("type", "mobile"))
                        )
                    inserted += 1

            conn.commit()
        except psycopg2.Error as exc:
            conn.rollback()
            print(f"  ✗ Error on '{first} {last}': {exc}")
            skipped += 1

    print(f"\n  ✓ Import complete — inserted: {inserted}, "
          f"overwritten: {overwritten}, skipped: {skipped}.")


# ══════════════════════════════════════════════════════════════════════════════
# 11. Import from extended CSV
# ══════════════════════════════════════════════════════════════════════════════

def import_from_csv(conn) -> None:
    """
    Import contacts from an extended CSV that supports:
      first_name, last_name, phone, phone_type, email, birthday, group
    On duplicate, calls upsert_contact() so the phone is updated in place.
    """
    _header("Import from CSV")
    filename = input("  CSV filename [contacts.csv]: ").strip() or "contacts.csv"

    if not os.path.exists(filename):
        print(f"  ✗ File '{filename}' not found.")
        return

    inserted = skipped = 0

    try:
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                first = row.get("first_name", "").strip()
                last  = row.get("last_name",  "").strip()
                phone = row.get("phone",       "").strip()
                ptype = row.get("phone_type",  "mobile").strip() or "mobile"
                email = row.get("email",       "").strip() or None
                bday  = row.get("birthday",    "").strip() or None
                group = row.get("group",       "").strip() or None

                if not first or not last:
                    print(f"  ⚠ Skipping row with missing name: {row}")
                    skipped += 1
                    continue

                try:
                    with conn.cursor() as cur:
                        # upsert the contact (existing procedure)
                        cur.execute(
                            "CALL upsert_contact(%s, %s, %s)",
                            (first, last, phone)
                        )
                        # update extended fields if provided
                        group_id = _get_or_create_group(cur, group) if group else None
                        cur.execute(
                            """
                            UPDATE contacts
                            SET email    = COALESCE(%s, email),
                                birthday = COALESCE(%s::DATE, birthday),
                                group_id = COALESCE(%s, group_id)
                            WHERE first_name = %s AND last_name = %s
                            """,
                            (email, bday, group_id, first, last)
                        )
                        # ensure correct phone type
                        if ptype in ("home", "work", "mobile"):
                            cur.execute(
                                """
                                UPDATE phones SET type = %s
                                WHERE contact_id = (
                                    SELECT id FROM contacts
                                    WHERE first_name = %s AND last_name = %s
                                )
                                AND phone = %s
                                """,
                                (ptype, first, last, phone)
                            )
                    conn.commit()
                    inserted += 1
                except psycopg2.Error as exc:
                    conn.rollback()
                    print(f"  ✗ Error on '{first} {last}': {exc}")
                    skipped += 1
    except OSError as exc:
        print(f"  ✗ Cannot read file: {exc}")
        return

    print(f"\n  ✓ CSV import complete — processed: {inserted}, skipped: {skipped}.")


# ══════════════════════════════════════════════════════════════════════════════
# Main menu
# ══════════════════════════════════════════════════════════════════════════════

MENU = """
  1.  Add contact
  2.  Add extra phone to contact
  3.  List all contacts  (paginated)
  4.  Search contacts  (name / email / phone)
  5.  Search by email
  6.  Filter by group  (+ sort)
  7.  Move contact to group
  8.  Delete contact
  9.  Export to JSON
  10. Import from JSON
  11. Import from CSV
  0.  Exit
"""

ACTIONS = {
    "1":  add_contact,
    "2":  add_extra_phone,
    "3":  list_contacts_paged,
    "4":  search_contacts,
    "5":  search_by_email,
    "6":  filter_by_group,
    "7":  move_to_group,
    "8":  delete_contact,
    "9":  export_to_json,
    "10": import_from_json,
    "11": import_from_csv,
}


def main() -> None:
    print(SEP2)
    print("  PhoneBook — Extended Edition  (TSIS 1)")
    print(SEP2)

    conn = get_connection()
    if conn is None:
        print("  Cannot connect to the database. Check config.py and try again.")
        sys.exit(1)

    # enable server-side NOTICE messages to be printed in the console
    conn.autocommit = False

    try:
        while True:
            print(MENU)
            choice = input("  Your choice: ").strip()

            if choice == "0":
                print("  Goodbye.")
                break

            action = ACTIONS.get(choice)
            if action is None:
                print("  Invalid choice — please try again.")
                continue

            try:
                action(conn)
            except KeyboardInterrupt:
                print("\n  (cancelled)")
                conn.rollback()

    finally:
        conn.close()


if __name__ == "__main__":
    main()
