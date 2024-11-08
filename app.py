from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    with sqlite3.connect("items.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            quantity INTEGER NOT NULL
        )
        """)
    conn.close()

init_db()

# Get all items
@app.route("/items", methods=["GET"])
def get_items():
    with sqlite3.connect("items.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, quantity FROM items")
        items = [{"name": row[0], "quantity": row[1]} for row in cursor.fetchall()]
    return jsonify(items)

# Add a new item or update an existing one
@app.route("/items", methods=["POST"])
def add_item():
    data = request.get_json()
    name = data.get("name").upper()
    quantity = data.get("quantity", 0)

    with sqlite3.connect("items.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO items (name, quantity) VALUES (?, ?)", (name, quantity))
        except sqlite3.IntegrityError:
            cursor.execute("UPDATE items SET quantity = quantity + ? WHERE name = ?", (quantity, name))
        conn.commit()
    
    return jsonify({"message": "Item added/updated successfully"}), 201

# Update item quantity
@app.route("/items/<name>", methods=["PUT"])
def update_quantity(name):
    data = request.get_json()
    delta = data.get("delta", 0)

    with sqlite3.connect("items.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE items SET quantity = quantity + ? WHERE name = ?", (delta, name.upper()))
        conn.commit()
    
    return jsonify({"message": "Quantity updated successfully"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

