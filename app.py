from flask import Flask, render_template, redirect, url_for, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Currently tracked bus
tracked_bus_id = None

# Current position of tracked bus
current_index = 0


def get_connection():
    return sqlite3.connect("bus_tracker.db")


# --------------------------------------------------
# Get bus tracking information
# --------------------------------------------------
def get_bus_data(bus_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, bus_number, route
        FROM buses
        WHERE id = ?
    """, (bus_id,))

    bus = cursor.fetchone()

    if bus is None:
        conn.close()
        return None

    cursor.execute("""
        SELECT stop_name, arrival_time
        FROM stops
        WHERE bus_id = ?
        ORDER BY stop_order
    """, (bus_id,))

    stops = cursor.fetchall()

    conn.close()

    if not stops:
        return None

    position = min(current_index, len(stops) - 1)

    current_stop = stops[position][0]

    if position >= len(stops) - 1:

        next_stop = "Trip Completed"
        eta = "0 minutes"
        status = "Arrived"

    else:

        next_stop = stops[position + 1][0]

        current_time = datetime.strptime(
            stops[position][1],
            "%H:%M"
        )

        next_time = datetime.strptime(
            stops[position + 1][1],
            "%H:%M"
        )

        difference = next_time - current_time

        eta_minutes = int(
            difference.total_seconds() / 60
        )

        eta = f"{eta_minutes} minutes"
        status = "On Schedule"

    return {
        "id": bus[0],
        "number": bus[1],
        "route": bus[2],
        "current_stop": current_stop,
        "next_stop": next_stop,
        "eta": eta,
        "status": status
    }


# --------------------------------------------------
# Get all stops
# --------------------------------------------------
def get_all_stops():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT stop_name
        FROM stops
        ORDER BY stop_name
    """)

    stops = [row[0] for row in cursor.fetchall()]

    conn.close()

    return stops


# --------------------------------------------------
# Search buses between two stops
# --------------------------------------------------
def search_buses(from_stop, to_stop):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            buses.id,
            buses.bus_number,
            buses.route,
            s1.stop_name,
            s1.arrival_time,
            s1.stop_order,
            s2.stop_name,
            s2.arrival_time,
            s2.stop_order

        FROM buses

        JOIN stops s1
            ON buses.id = s1.bus_id

        JOIN stops s2
            ON buses.id = s2.bus_id

        WHERE
            s1.stop_name = ?
            AND s2.stop_name = ?
            AND s1.stop_order < s2.stop_order

        ORDER BY s1.arrival_time
    """, (from_stop, to_stop))

    results = cursor.fetchall()

    conn.close()

    buses = []

    for row in results:

        bus_id = row[0]

        departure_time = row[4]
        arrival_time = row[7]

        start_time = datetime.strptime(
            departure_time,
            "%H:%M"
        )

        end_time = datetime.strptime(
            arrival_time,
            "%H:%M"
        )

        journey_time = end_time - start_time

        journey_minutes = int(
            journey_time.total_seconds() / 60
        )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT stop_name
            FROM stops
            WHERE
                bus_id = ?
                AND stop_order >= ?
                AND stop_order <= ?

            ORDER BY stop_order
        """, (
            bus_id,
            row[5],
            row[8]
        ))

        intermediate_stops = [
            stop[0]
            for stop in cursor.fetchall()
        ]

        conn.close()

        buses.append({
            "id": bus_id,
            "number": row[1],
            "route": row[2],
            "from_stop": from_stop,
            "to_stop": to_stop,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "journey_time": f"{journey_minutes} minutes",
            "stops": intermediate_stops
        })

    return buses


# --------------------------------------------------
# Home page
# --------------------------------------------------
@app.route("/")
def home():

    bus = None

    # If a bus is being tracked
    if tracked_bus_id is not None:

        bus = get_bus_data(tracked_bus_id)

    # Otherwise show first bus as demo
    else:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM buses
            ORDER BY id
            LIMIT 1
        """)

        first_bus = cursor.fetchone()

        conn.close()

        if first_bus:
            bus = get_bus_data(first_bus[0])

    stops = get_all_stops()

    search_results = []

    from_stop = request.args.get(
        "from_stop",
        ""
    )

    to_stop = request.args.get(
        "to_stop",
        ""
    )

    if from_stop and to_stop:

        search_results = search_buses(
            from_stop,
            to_stop
        )

    return render_template(
        "index.html",
        bus=bus,
        stops=stops,
        search_results=search_results,
        from_stop=from_stop,
        to_stop=to_stop
    )


# --------------------------------------------------
# Track selected bus
# --------------------------------------------------
@app.route("/track/<int:bus_id>")
def track_bus(bus_id):

    global tracked_bus_id
    global current_index

    tracked_bus_id = bus_id

    # Optional selected starting stop
    from_stop = request.args.get(
        "from_stop",
        ""
    )

    conn = get_connection()
    cursor = conn.cursor()

    if from_stop:

        cursor.execute("""
            SELECT stop_order
            FROM stops
            WHERE
                bus_id = ?
                AND stop_name = ?
        """, (
            bus_id,
            from_stop
        ))

        result = cursor.fetchone()

        if result:
            current_index = result[0] - 1
        else:
            current_index = 0

    else:
        current_index = 0

    conn.close()

    return redirect(url_for("home"))


# --------------------------------------------------
# Move bus to next stop
# --------------------------------------------------
@app.route("/next")
def next_stop():

    global current_index

    if tracked_bus_id is None:
        return redirect(url_for("home"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM stops
        WHERE bus_id = ?
    """, (tracked_bus_id,))

    total_stops = cursor.fetchone()[0]

    conn.close()

    if current_index < total_stops - 1:
        current_index += 1

    return redirect(url_for("home"))


# --------------------------------------------------
# Reset bus
# --------------------------------------------------
@app.route("/reset")
def reset():

    global current_index

    current_index = 0

    return redirect(url_for("home"))


# --------------------------------------------------
# Run application
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)