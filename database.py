
import sqlite3


def create_database():
    conn = sqlite3.connect("bus_tracker.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_number TEXT,
            route TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_id INTEGER,
            stop_name TEXT,
            arrival_time TEXT,
            stop_order INTEGER
        )
    """)

    # Clear old sample data
    cursor.execute("DELETE FROM stops")
    cursor.execute("DELETE FROM buses")

    cursor.execute("DELETE FROM sqlite_sequence WHERE name='buses'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='stops'")

    # Bus 101
    cursor.execute("""
        INSERT INTO buses (bus_number, route)
        VALUES (?, ?)
    """, (
        "101",
        "Tadepalligudem → Tanuku → Undi → Bhimavaram"
    ))
    bus_101_id = cursor.lastrowid

    stops_101 = [
        ("Tadepalligudem", "08:00", 1),
        ("Tanuku", "08:20", 2),
        ("Undi", "08:35", 3),
        ("Bhimavaram", "09:00", 4)
    ]

    cursor.executemany("""
        INSERT INTO stops
        (bus_id, stop_name, arrival_time, stop_order)
        VALUES (?, ?, ?, ?)
    """, [(bus_101_id, *stop) for stop in stops_101])

    # Bus 102
    cursor.execute("""
        INSERT INTO buses (bus_number, route)
        VALUES (?, ?)
    """, (
        "102",
        "Tadepalligudem → Nidadavole → Tanuku → Bhimavaram"
    ))
    bus_102_id = cursor.lastrowid

    stops_102 = [
        ("Tadepalligudem", "08:30", 1),
        ("Nidadavole", "08:50", 2),
        ("Tanuku", "09:05", 3),
        ("Bhimavaram", "09:30", 4)
    ]

    cursor.executemany("""
        INSERT INTO stops
        (bus_id, stop_name, arrival_time, stop_order)
        VALUES (?, ?, ?, ?)
    """, [(bus_102_id, *stop) for stop in stops_102])

    # Bus 103
    cursor.execute("""
        INSERT INTO buses (bus_number, route)
        VALUES (?, ?)
    """, (
        "103",
        "Tanuku → Undi → Bhimavaram → College"
    ))
    bus_103_id = cursor.lastrowid

    stops_103 = [
        ("Tanuku", "09:00", 1),
        ("Undi", "09:20", 2),
        ("Bhimavaram", "09:40", 3),
        ("College", "10:00", 4)
    ]

    cursor.executemany("""
        INSERT INTO stops
        (bus_id, stop_name, arrival_time, stop_order)
        VALUES (?, ?, ?, ?)
    """, [(bus_103_id, *stop) for stop in stops_103])

    conn.commit()
    conn.close()

    print("Database created successfully!")
    print("3 sample buses and their stops have been added.")


if __name__ == "__main__":
    create_database()
