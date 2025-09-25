from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras

app = Flask(__name__)

# Simple DB connection function
def get_conn():
    return psycopg2.connect(
        host="localhost",
        dbname="sample_db",
        user="postgres",
        password="root"   # <-- change this
    )

# ------------------- CREATE -------------------
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            "INSERT INTO users (name,email,age) VALUES (%s,%s,%s) RETURNING *",
            (data["name"], data["email"], data.get("age"))
        )
        conn.commit()
        return jsonify(cur.fetchone()), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

# ------------------- READ ALL -------------------
@app.route("/users", methods=["GET"])
def get_users():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users ORDER BY id")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(users)

# ------------------- READ ONE -------------------
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

# ------------------- UPDATE -------------------
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "UPDATE users SET name=%s, email=%s, age=%s WHERE id=%s RETURNING *",
        (data["name"], data["email"], data.get("age"), user_id)
    )
    conn.commit()
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

# ------------------- DELETE -------------------
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s RETURNING id", (user_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not deleted:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": f"User {user_id} deleted"})

if __name__ == "__main__":
    app.run(debug=True)
