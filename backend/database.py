import sqlite3
import os

def init_database():
    """Initialize the database with required tables"""
    
    # Create database directory if it doesn't exist
    db_path = 'database'
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    
    # Connect to database
    conn = sqlite3.connect('database/workshop.db')
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create vehicles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            registration_number TEXT UNIQUE NOT NULL,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    # Create services table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT
        )
    ''')
    
    # Create appointments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            service_date DATE NOT NULL,
            time_slot TEXT NOT NULL,
            status TEXT DEFAULT 'Scheduled',
            notes TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
        )
    ''')
    
    # Create invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            paid_amount REAL DEFAULT 0,
            payment_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (appointment_id) REFERENCES appointments (id)
        )
    ''')
    
    # Insert sample services if table is empty
    cursor.execute("SELECT COUNT(*) FROM services")
    if cursor.fetchone()[0] == 0:
        sample_services = [
            ('Oil Change', 'Engine oil change with filter replacement', 50.00, 'Maintenance'),
            ('Tire Rotation', 'Rotate all four tires and check pressure', 30.00, 'Maintenance'),
            ('Brake Pad Replacement', 'Replace front/rear brake pads', 150.00, 'Repair'),
            ('Engine Diagnostic', 'Complete engine diagnostic check', 80.00, 'Diagnostic'),
            ('AC Service', 'Air conditioning system service', 100.00, 'Maintenance'),
            ('Battery Replacement', 'Replace old battery with new one', 120.00, 'Repair'),
            ('Wheel Alignment', 'Complete wheel alignment service', 60.00, 'Maintenance'),
            ('Car Wash', 'Exterior and interior car wash', 25.00, 'Cleaning')
        ]
        cursor.executemany("INSERT INTO services (name, description, price, category) VALUES (?, ?, ?, ?)", sample_services)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()