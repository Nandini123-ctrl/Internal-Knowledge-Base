from flask import Flask, render_template, request, jsonify
import sqlite3
import datetime

app = Flask(__name__)
DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY,
            customer_name TEXT,
            phone_number TEXT,
            payment_mode TEXT,
            subtotal REAL,
            tax_total REAL,
            discount REAL,
            grand_total REAL,
            created_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT,
            item_name TEXT,
            rate REAL,
            qty INTEGER,
            tax_rate REAL,
            total REAL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/save-invoice', methods=['POST'])
def save_invoice():
    data = request.json
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO invoices (invoice_id, customer_name, phone_number, payment_mode, subtotal, tax_total, discount, grand_total, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['invNo'], data['custName'], data['phoneNum'], data['payMode'],
            data['subTotal'], data['gstAmount'], data['discount'], data['grandTotal'],
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        for item in data['cart']:
            cursor.execute('''
                INSERT INTO invoice_items (invoice_id, item_name, rate, qty, tax_rate, total)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (data['invNo'], item['name'], item['rate'], item['qty'], item['taxRate'], item['total']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Saved to database!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)