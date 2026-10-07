from datetime import datetime
import sqlite3
from flask import Flask, jsonify, request, send_file  # <-- Added send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_NAME = "crumb_and_cloud.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subtotal REAL NOT NULL,
            tax REAL NOT NULL,
            grand_total REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

  cursor.execute("SELECT COUNT(*) FROM products")
  if cursor.fetchone()[0] == 0:
    sample_products = [
        ("Chocolate Truffle Cake", "Cakes", 450.0, 15),
        ("Birthday Celebration Cake", "Cakes", 650.0, 10),
        ("Berry Glaze Pastry", "Pastries", 150.0, 25),
    ]
    cursor.executemany(
        """
            INSERT INTO products (name, category, price, stock) 
            VALUES (?, ?, ?, ?)
        """,
        sample_products,
    )
    conn.commit()

  conn.close()


# --- ADD THIS ROUTE SO IT LOADS YOUR DASHBOARD ---
@app.route("/")
def home():
  return send_file("index.html")


@app.route("/api/products", methods=["GET"])
def get_products():
  conn = sqlite3.connect(DB_NAME)
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM products")
  rows = cursor.fetchall()
  products = [dict(row) for row in rows]
  conn.close()
  return jsonify(products)


@app.route("/api/orders", methods=["POST"])
def save_order():
  data = request.json
  subtotal = data.get("subtotal")
  tax = data.get("tax")
  grand_total = data.get("grandTotal")
  created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT INTO orders (subtotal, tax, grand_total, created_at) 
        VALUES (?, ?, ?, ?)
    """,
      (subtotal, tax, grand_total, created_at),
  )
  conn.commit()
  conn.close()

  return jsonify(
      {"message": "Order successfully processed and stored in SQL database!"}
  )


if __name__ == "__main__":
  init_db()
  print("Python Flask Server running on http://localhost:3000")
  app.run(debug=True, port=3000)
