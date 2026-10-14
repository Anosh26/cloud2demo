import os
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cloud2demo-secret-key-12345")

# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "app_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_connection(retries=15, delay=2):
    """Attempt connection to the PostgreSQL database with retry logic."""
    attempt = 0
    while attempt < retries:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                port=DB_PORT
            )
            return conn
        except OperationalError:
            attempt += 1
            print(f"[DB] Waiting for database at {DB_HOST}:{DB_PORT}... (attempt {attempt}/{retries})")
            time.sleep(delay)
    
    # Final try to connect or raise exception
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def init_db():
    """Ensure database table exists at startup."""
    print(f"[INIT] Checking PostgreSQL connection ({DB_HOST}:{DB_PORT}/{DB_NAME})...")
    try:
        conn = get_connection(retries=15, delay=2)
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("[INIT] Table 'logs' ready in database.")
        conn.close()
    except Exception as e:
        print(f"[INIT WARNING] Database not immediately reachable: {e}")

@app.route("/", methods=["GET"])
def index():
    """Render the web dashboard with all existing database records."""
    records = []
    db_status = "Connected"
    error_msg = None
    try:
        conn = get_connection(retries=3, delay=1)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id, message, created_at FROM logs ORDER BY id DESC;")
            records = cursor.fetchall()
        conn.close()
    except Exception as e:
        db_status = "Disconnected"
        error_msg = str(e)

    return render_template(
        "index.html",
        records=records,
        db_status=db_status,
        db_host=DB_HOST,
        db_name=DB_NAME,
        db_port=DB_PORT,
        error_msg=error_msg
    )

@app.route("/records", methods=["POST"])
def add_record():
    """Insert a new record entered by the user into the database."""
    message = request.form.get("message", "").strip()

    # Support JSON payload if submitted via fetch
    if not message and request.is_json:
        payload = request.get_json()
        message = payload.get("message", "").strip()

    if not message:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({"success": False, "error": "Message cannot be empty."}), 400
        flash("Message cannot be empty.", "error")
        return redirect(url_for("index"))

    try:
        conn = get_connection(retries=3, delay=1)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "INSERT INTO logs (message) VALUES (%s) RETURNING id, message, created_at;",
                (message,)
            )
            new_record = cursor.fetchone()
            conn.commit()
        conn.close()

        print(f"[WRITE] Inserted ID {new_record['id']}: '{message}'")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({
                "success": True,
                "record": {
                    "id": new_record["id"],
                    "message": new_record["message"],
                    "created_at": new_record["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                }
            })

        flash("Record inserted successfully!", "success")
        return redirect(url_for("index"))
    except Exception as e:
        print(f"[ERROR] Insert failed: {e}")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({"success": False, "error": str(e)}), 500
        flash(f"Database error: {e}", "error")
        return redirect(url_for("index"))

@app.route("/records/<int:record_id>/delete", methods=["POST", "DELETE"])
def delete_record(record_id):
    """Delete a record from the database by ID."""
    try:
        conn = get_connection(retries=3, delay=1)
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM logs WHERE id = %s;", (record_id,))
            conn.commit()
        conn.close()

        print(f"[DELETE] Removed record ID: {record_id}")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True, "deleted_id": record_id})

        flash(f"Record #{record_id} deleted.", "success")
        return redirect(url_for("index"))
    except Exception as e:
        print(f"[ERROR] Delete failed: {e}")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "error": str(e)}), 500
        flash(f"Failed to delete record: {e}", "error")
        return redirect(url_for("index"))

@app.route("/api/records", methods=["GET"])
def api_get_records():
    """API endpoint to get all records as JSON."""
    try:
        conn = get_connection(retries=3, delay=1)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id, message, created_at FROM logs ORDER BY id DESC;")
            records = cursor.fetchall()
        conn.close()

        for r in records:
            if isinstance(r["created_at"], datetime):
                r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({"success": True, "records": records, "count": len(records)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", 5000))
    print(f"Server running at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)