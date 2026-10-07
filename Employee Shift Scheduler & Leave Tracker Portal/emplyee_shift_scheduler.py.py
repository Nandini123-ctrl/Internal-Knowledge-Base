import sqlite3
import os
import webbrowser

# --- 1. Database Setup & Sample Data Insertion ---
def setup_database():
    conn = sqlite3.connect("scheduler.db")
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            shift_date TEXT NOT NULL,
            shift_type TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            leave_date TEXT NOT NULL,
            reason TEXT NOT NULL
        )
    """)
    
    # Clear old empty tables to prevent duplicates on rerun
    cursor.execute("DELETE FROM shifts")
    cursor.execute("DELETE FROM leaves")
    
    # Insert Sample Shifts Data
    sample_shifts = [
        ("Alice Smith", "2026-07-22", "Morning (08:00 - 16:00)"),
        ("Bob Jones", "2026-07-22", "Evening (16:00 - 00:00)"),
        ("Charlie Brown", "2026-07-23", "Night (00:00 - 08:00)"),
        ("Diana Prince", "2026-07-23", "Morning (08:00 - 16:00)"),
        ("Evan Wright", "2026-07-24", "Evening (16:00 - 00:00)")
    ]
    cursor.executemany("INSERT INTO shifts (employee_name, shift_date, shift_type) VALUES (?, ?, ?)", sample_shifts)

    # Insert Sample Leaves Data
    sample_leaves = [
        ("Fiona Gallagher", "2026-07-22", "Sick Leave"),
        ("George Clark", "2026-07-24", "Casual Leave"),
        ("Hannah Abbott", "2026-07-25", "Medical Emergency")
    ]
    cursor.executemany("INSERT INTO leaves (employee_name, leave_date, reason) VALUES (?, ?, ?)", sample_leaves)

    conn.commit()
    conn.close()

# --- 2. Generate HTML Report with Styled Tables ---
def generate_html_report():
    conn = sqlite3.connect("scheduler.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT employee_name, shift_date, shift_type FROM shifts")
    shifts = cursor.fetchall()
    
    cursor.execute("SELECT employee_name, leave_date, reason FROM leaves")
    leaves = cursor.fetchall()
    
    conn.close()

    html_code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Employee Shift Scheduler & Leave Tracker</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 40px; 
            background-color: #f4f6f9; 
        }
        h1 { color: #2c3e50; margin-bottom: 30px; }
        h2 { color: #34495e; margin-top: 30px; }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 15px; 
            background-color: #ffffff; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
            border-radius: 6px;
            overflow: hidden;
        }
        th, td { 
            border: 1px solid #e1e8ed; 
            padding: 12px 15px; 
            text-align: left; 
        }
        th { 
            background-color: #007bff; 
            color: #ffffff; 
            font-weight: 600; 
            text-transform: uppercase;
            font-size: 14px;
        }
        tr:nth-child(even) { background-color: #f8f9fa; }
        tr:hover { background-color: #f1f3f5; }
    </style>
</head>
<body>
    <h1>📅 Employee Shift Scheduler & Leave Tracker</h1>
    
    <h2>Shift Schedule</h2>
    <table>
        <thead>
            <tr>
                <th>Employee Name</th>
                <th>Shift Date</th>
                <th>Shift Details</th>
            </tr>
        </thead>
        <tbody>
"""
    
    if shifts:
        for name, date, shift in shifts:
            html_code += f"        <tr><td>{name}</td><td>{date}</td><td>{shift}</td></tr>\n"
    else:
        html_code += "        <tr><td colspan='3'>No shifts scheduled yet.</td></tr>\n"

    html_code += """        </tbody>
    </table>

    <h2>Leave Requests</h2>
    <table>
        <thead>
            <tr>
                <th>Employee Name</th>
                <th>Leave Date</th>
                <th>Reason</th>
            </tr>
        </thead>
        <tbody>
"""

    if leaves:
        for name, date, reason in leaves:
            html_code += f"        <tr><td>{name}</td><td>{date}</td><td>{reason}</td></tr>\n"
    else:
        html_code += "        <tr><td colspan='3'>No leave records found.</td></tr>\n"

    html_code += """        </tbody>
    </table>
</body>
</html>
"""

    output_filename = "index.html"

    # Save to file with UTF-8 encoding
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_code)

    print(f"✅ Report generated successfully: {os.path.abspath(output_filename)}")
    
    # Open automatically in default browser
    webbrowser.open("file://" + os.path.abspath(output_filename))

# --- Main Execution ---
if __name__ == "__main__":
    setup_database()
    generate_html_report()