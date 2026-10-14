# Cloud PostgreSQL Live Web Dashboard

A containerized web application built with **Flask**, **PostgreSQL**, and **Docker Compose**. This allows you to enter data directly in a modern web interface and see it immediately reflected and stored in your PostgreSQL database in real-time.

---

## 🚀 Features

- **Interactive Web Interface**: Clean, modern dark-themed dashboard to insert messages, log payloads, or notes into PostgreSQL.
- **Instant Reflection**: Real-time updates without page reloads using asynchronous fetch.
- **Quick Test Presets**: Pre-configured buttons to test various cloud log messages with 1 click.
- **Database Management**: Live count of records, search/filter through saved records, and delete records directly from the database.
- **Automatic Schema Initialization**: Auto-creates the `logs` table upon database startup.
- **Container Ready**: Runs seamlessly with `docker compose up --build`.

---

## 📁 Project Structure

```
cloud2demo/
├── docker-compose.yml       # Coordinates PostgreSQL ('db') and Flask Web ('web')
└── app/
    ├── Dockerfile           # Python 3.12-slim container configuration
    ├── requirements.txt     # Python dependencies (Flask, psycopg2-binary)
    ├── main.py              # Flask backend server with PostgreSQL CRUD logic
    └── templates/
        └── index.html       # Web UI dashboard
```

---

## 🛠️ How to Run

### Option 1: Run with Docker Compose (Recommended)

1. Make sure **Docker Desktop** is open and running on your system.
2. In your terminal, navigate to the `cloud2demo` folder:
   ```bash
   cd c:\Users\Anosh\Documents\Notes\cloud\cloud2demo
   ```
3. Start the database and web service:
   ```bash
   docker compose up --build
   ```
4. Open your browser and visit:
   ```
   http://localhost:5000
   ```

To stop the containers:
```bash
docker compose down
```

---

## 🗄️ Database Details

- **Database Name**: `app_db`
- **Table Name**: `logs`
- **Schema**:
  - `id` (SERIAL PRIMARY KEY)
  - `message` (TEXT NOT NULL)
  - `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
