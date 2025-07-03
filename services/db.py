import sqlite3

conn = sqlite3.connect("employees.db", check_same_thread=False)
cursor = conn.cursor()

def initialize_db():
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
        emp_id TEXT PRIMARY KEY,
        name TEXT,
        lname TEXT,
        age INTEGER,
        salary INTEGER,
        position TEXT,
        email TEXT
    )''')
    conn.commit()

def get_all_employees():
    cursor.execute("SELECT * FROM employees")
    rows = cursor.fetchall()
    return [dict(zip(["emp_id", "name", "lname", "age", "salary", "position", "email"], row)) for row in rows]

def add_employee(data):
    try:
        print("🔍 Received data:", data)
        cursor.execute("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?)", (
            data["emp_id"],
            data["name"],
            data["lname"],
            int(data["age"]),
            int(data["salary"]),
            data["position"],
            data["email"]
        ))
        conn.commit()
        return {"success": True, "message": "Employee added successfully"}
    except Exception as e:
        print("❌ Error inserting employee:", e)
        return {"success": False, "error": str(e)}

def update_employee(emp_id, data):
    updates = ", ".join([f"{key} = ?" for key in data])
    values = list(data.values()) + [emp_id]
    cursor.execute(f"UPDATE employees SET {updates} WHERE emp_id = ?", values)
    conn.commit()
    return {"success": True}

def delete_employee(emp_id):
    cursor.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))
    conn.commit()
    return {"success": True}

def get_stats():
    cursor.execute("SELECT position, COUNT(*) FROM employees GROUP BY position")
    rows = cursor.fetchall()
    return [{"position": row[0], "count": row[1]} for row in rows]
