import psycopg2, csv
from connect import get_connection

def create_table():
    sql = """
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50),
            phone VARCHAR(20) NOT NULL UNIQUE
        );
    """

    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()

def insert_from_csv(filepath):
    conn = get_connection()
    if not conn:
        return
    
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cur = conn.cursor()
        for row in reader:
            cur.execute(
                """INSERT INTO phonebook (first_name, last_name, phone) VALUES  (%s, %s, %s) ON CONFLICT (phone) DO NOTHING""", 
                (row["first_name"], row["last_name"], row["phone"])
            )
    conn.commit()
    conn.close()

def insert_from_console():
    first_name = input("First name: ")
    last_name = input("Last name: ")
    phone = input("Phone: ")

    conn = get_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO phonebook (first_name, last_name, phone) VALUES (%s, %s, %s) ON CONFLICT (phone) DO NOTHING
    """, (first_name, last_name, phone))

    conn.commit()
    conn.close()

def search_contacts():
    name = input("Search by name: ")
    conn = get_connection()
    if not conn:
        return

    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM phonebook WHERE first_name = %s
    """, (name, ))
    rows = cur.fetchall()
    for row in rows:
        print(row)
    conn.close()

def update_contact():
    phone = input("Enter current phone number: ")
    print("What do you want to update?")
    print("1. First name")
    print("2. Last name")
    print("3. Phone")
    choice = input("Choose: ")

    conn = get_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    if choice == "1":
        new_val = input("New first name: ")
        cur.execute("""
            UPDATE phonebook SET first_name = %s WHERE phone = %s
        """, (new_val, phone))
    elif choice == "2":
        new_val = input("New last name: ")
        cur.execute("""
            UPDATE phonebook SET last_name = %s WHERE phone = %s
        """, (new_val, phone))
    elif choice == "3":
        new_val = input("New phone: ")
        cur.execute("""
            UPDATE phonebook SET phone = %s WHERE phone = %s
        """, (new_val, phone))

    conn.commit()
    conn.close()

def delete_contact():
    name = input("Enter the name of contact you want to delete: ")

    conn = get_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM phonebook WHERE first_name = %s
    """, (name, ))

    conn.commit()
    conn.close()

def main():
    create_table()
    while True:
        print("\n--- PhoneBook Menu ---")
        print("1. Import from CSV")
        print("2. Add contact manually")
        print("3. Search contacts")
        print("4. Update contact")
        print("5. Delete contact")
        print("0. Exit")

        choice = input("Choose: ")

        if choice == "1":
            insert_from_csv("contactns.csv")
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            search_contacts()
        elif choice == "4":
            update_contact()
        elif choice == "5":
            delete_contact()
        elif choice == "0":
            break

create_table()
main()