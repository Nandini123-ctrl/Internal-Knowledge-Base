import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = 'scheduler.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS shifts (id INTEGER PRIMARY KEY AUTOINCREMENT, employee_name TEXT NOT NULL, shift_date TEXT NOT NULL, shift_time TEXT NOT NULL)')
        cursor.execute('CREATE TABLE IF NOT EXISTS leaves (id INTEGER PRIMARY KEY AUTOINCREMENT, employee_name TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, status TEXT DEFAULT "Pending")')
        cursor.execute("SELECT COUNT(*) FROM shifts")
        if cursor.fetchone()[0] == 0:
            sample_shifts = [
                ("Alice Smith", "2026-07-03", "Morning (09:00 - 17:00)"),
                ("Bob Jones", "2026-07-03", "Evening (17:00 - 01:00)")
            ]
            cursor.executemany("INSERT INTO shifts (employee_name, shift_date, shift_time) VALUES (?, ?, ?)", sample_shifts)
        db.commit()

@app.route('/')
def index():
    db = get_db()
    shifts = db.execute("SELECT * FROM shifts ORDER BY shift_date ASC").fetchall()
    leaves = db.execute("SELECT * FROM leaves ORDER BY start_date ASC").fetchall()
    return render_template('index.html', shifts=shifts, leaves=leaves)

@app.route('/add_shift', methods=['POST'])
def add_shift():
    name = request.form['employee_name']
    date = request.form['shift_date']
    time = request.form['shift_time']
    if name and date and time:
        db = get_db()
        db.execute("INSERT INTO shifts (employee_name, shift_date, shift_time) VALUES (?, ?, ?)", (name, date, time))
        db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
