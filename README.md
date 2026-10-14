# Cloud PostgreSQL Live Web Dashboard

A containerized web application built with **Flask**, **PostgreSQL**, and **Docker**. This allows you to enter data directly in a modern web interface and see it immediately reflected and stored in your PostgreSQL database in real-time.

---

## 📁 Repository Structure

```
cloud2demo/
├── docker-compose.yml       # Single-host deployment (DB + Web on one machine)
├── docker-compose.db.yml    # VM 1 deployment (PostgreSQL Database only)
├── docker-compose.app.yml   # VM 2 deployment (Flask Web App only)
├── .env.example             # Template for setting DB_HOST to VM 1's IP
└── app/
    ├── Dockerfile           # Python 3.12 container configuration
    ├── requirements.txt     # Python dependencies (Flask, psycopg2-binary)
    ├── main.py              # Flask backend server with PostgreSQL CRUD logic
    └── templates/
        └── index.html       # Modern dark-mode web dashboard
```

---

## 🌐 2-VM Distributed Deployment

To run the database on **VM 1** and the web application on **VM 2**:

```
+---------------------------+             +---------------------------+
|          VM 2             |             |          VM 1             |
|   (Application Server)    |   port 5432 |    (Database Server)      |
|                           |  -------->  |                           |
|  Flask App (Port 5000)    |             |  PostgreSQL (Port 5432)   |
|  http://<VM2_IP>:5000     |             |  Database: app_db         |
+---------------------------+             +---------------------------+
```

### Step 1: Set up VM 1 (Database)

1. Clone this repository on **VM 1**:
   ```bash
   git clone https://github.com/Anosh26/cloud2demo.git
   cd cloud2demo
   ```
2. Start the PostgreSQL container:
   ```bash
   docker compose -f docker-compose.db.yml up -d
   ```
3. Find VM 1's IP address:
   ```bash
   # On Linux
   ip addr show
   # or
   hostname -I
   ```
   *Note down this IP address (e.g. `192.168.1.100` or private cloud IP).*

4. **Firewall / Security Group check**:
   Ensure incoming traffic on port `5432` is allowed on VM 1 (from VM 2's IP address or subnet):
   ```bash
   # If using UFW (Ubuntu/Debian)
   sudo ufw allow 5432/tcp
   ```

---

### Step 2: Set up VM 2 (Web Application)

1. Clone this repository on **VM 2**:
   ```bash
   git clone https://github.com/Anosh26/cloud2demo.git
   cd cloud2demo
   ```
2. Create your `.env` configuration pointing to VM 1:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and replace `DB_HOST` with VM 1's actual IP address:
   ```env
   DB_HOST=192.168.1.100
   DB_NAME=app_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_PORT=5432
   ```

3. Build and run the web app container:
   ```bash
   docker compose -f docker-compose.app.yml up -d --build
   ```

---

### Step 3: Access the Web Dashboard

Open your web browser and navigate to:
```
http://<VM2_IP>:5000
```
- Enter any text in the form and click **"Save to Database"**.
- The web app on **VM 2** commits the data to PostgreSQL running on **VM 1** and immediately renders the new record on your screen!

---

## 🔍 Verification & Troubleshooting

- **Check if VM 2 can reach VM 1 on port 5432**:
  ```bash
  # From VM 2:
  nc -zv <VM1_IP> 5432
  # or
  telnet <VM1_IP> 5432
  ```
- **View Web App Logs on VM 2**:
  ```bash
  docker logs -f flask_web
  ```
- **View Database Logs on VM 1**:
  ```bash
  docker logs -f postgres_db
  ```
- **Inspect PostgreSQL directly on VM 1**:
  ```bash
  docker exec -it postgres_db psql -U postgres -d app_db -c "SELECT * FROM logs;"
  ```
