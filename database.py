import sqlite3

DB_NAME = "tickets.db"

# ---------- INIT FUNCTION ----------
def initialize_all_tables():
    create_table()
    create_staff_table()
    create_staff_logs_table()

# ---------- TICKETS ----------
def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            issue TEXT,
            priority TEXT,
            category TEXT,
            status TEXT DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_ticket(name, email, issue, priority, category, status="Open"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tickets (name, email, issue, priority, category, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, email, issue, priority, category, status))
    conn.commit()
    conn.close()

def fetch_all_tickets():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_ticket_status(ticket_id, new_status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tickets SET status = ? WHERE id = ?
    ''', (new_status, ticket_id))
    conn.commit()
    conn.close()

# ---------- STAFF ACCOUNTS ----------
def create_staff_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'staff'
        )
    ''')
    conn.commit()
    conn.close()

def insert_staff(username, password, role="staff"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO staff (username, password, role)
        VALUES (?, ?, ?)
    ''', (username, password, role))
    conn.commit()
    conn.close()

def validate_staff(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM staff WHERE username = ? AND password = ?
    ''', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# ---------- STAFF ACTIVITY LOGGING ----------
def create_staff_logs_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_username TEXT,
            action TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_staff_action(username, action):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO staff_logs (staff_username, action)
        VALUES (?, ?)
    ''', (username, action))
    conn.commit()
    conn.close()

def fetch_staff_logs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM staff_logs ORDER BY timestamp DESC')
    logs = cursor.fetchall()
    conn.close()
    return logs

# ---------- IF RUN DIRECTLY ----------
if __name__ == "__main__":
    initialize_all_tables()
    print("✅ All tables created and ready.")
