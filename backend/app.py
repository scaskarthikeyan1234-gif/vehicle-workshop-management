from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create database folder if it doesn't exist
if not os.path.exists('database'):
    os.makedirs('database')

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('database/workshop.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database tables
def init_database():
    conn = get_db_connection()
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

# Initialize database on startup
init_database()

# ==================== ROOT ENDPOINT ====================
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': '🚗 Vehicle Workshop Management API',
        'version': '1.0',
        'status': 'running',
        'endpoints': {
            'customers': '/api/customers',
            'vehicles': '/api/vehicles',
            'services': '/api/services',
            'appointments': '/api/appointments',
            'invoices': '/api/invoices',
            'dashboard': '/api/dashboard/stats'
        },
        'documentation': 'Use the frontend application at http://127.0.0.1:5500'
    })

# ==================== CUSTOMER ROUTES ====================
@app.route('/api/customers', methods=['GET'])
def get_customers():
    try:
        conn = get_db_connection()
        customers = conn.execute('SELECT * FROM customers ORDER BY created_at DESC').fetchall()
        conn.close()
        return jsonify([dict(customer) for customer in customers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers', methods=['POST'])
def add_customer():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)',
            (data['name'], data['phone'], data.get('email', ''), data.get('address', ''))
        )
        conn.commit()
        customer_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': customer_id, 'message': 'Customer added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    try:
        data = request.json
        conn = get_db_connection()
        conn.execute(
            'UPDATE customers SET name=?, phone=?, email=?, address=? WHERE id=?',
            (data['name'], data['phone'], data.get('email', ''), data.get('address', ''), id)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Customer updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM customers WHERE id=?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Customer deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== VEHICLE ROUTES ====================
@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    try:
        conn = get_db_connection()
        vehicles = conn.execute('''
            SELECT v.*, c.name as customer_name 
            FROM vehicles v 
            JOIN customers c ON v.customer_id = c.id
            ORDER BY v.id DESC
        ''').fetchall()
        conn.close()
        return jsonify([dict(vehicle) for vehicle in vehicles])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicles/customer/<int:customer_id>', methods=['GET'])
def get_vehicles_by_customer(customer_id):
    try:
        conn = get_db_connection()
        vehicles = conn.execute(
            'SELECT * FROM vehicles WHERE customer_id=? ORDER BY id DESC',
            (customer_id,)
        ).fetchall()
        conn.close()
        return jsonify([dict(vehicle) for vehicle in vehicles])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO vehicles (customer_id, registration_number, make, model, year) VALUES (?, ?, ?, ?, ?)',
            (data['customer_id'], data['registration_number'], data['make'], data['model'], data.get('year'))
        )
        conn.commit()
        vehicle_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': vehicle_id, 'message': 'Vehicle added successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Registration number already exists'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/vehicles/<int:id>', methods=['DELETE'])
def delete_vehicle(id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM vehicles WHERE id=?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Vehicle deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== SERVICE ROUTES ====================
@app.route('/api/services', methods=['GET'])
def get_services():
    try:
        conn = get_db_connection()
        services = conn.execute('SELECT * FROM services ORDER BY category, name').fetchall()
        conn.close()
        return jsonify([dict(service) for service in services])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/services', methods=['POST'])
def add_service():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO services (name, description, price, category) VALUES (?, ?, ?, ?)',
            (data['name'], data.get('description', ''), data['price'], data.get('category', 'General'))
        )
        conn.commit()
        service_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': service_id, 'message': 'Service added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/services/<int:id>', methods=['PUT'])
def update_service(id):
    try:
        data = request.json
        conn = get_db_connection()
        conn.execute(
            'UPDATE services SET name=?, description=?, price=?, category=? WHERE id=?',
            (data['name'], data.get('description', ''), data['price'], data.get('category', 'General'), id)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Service updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/services/<int:id>', methods=['DELETE'])
def delete_service(id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM services WHERE id=?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Service deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== APPOINTMENT ROUTES ====================
@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    try:
        conn = get_db_connection()
        appointments = conn.execute('''
            SELECT a.*, v.registration_number, v.make, v.model, c.name as customer_name 
            FROM appointments a 
            JOIN vehicles v ON a.vehicle_id = v.id
            JOIN customers c ON v.customer_id = c.id
            ORDER BY a.service_date DESC, a.time_slot
        ''').fetchall()
        conn.close()
        return jsonify([dict(appointment) for appointment in appointments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointments', methods=['POST'])
def add_appointment():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO appointments (vehicle_id, service_date, time_slot, status, notes) VALUES (?, ?, ?, ?, ?)',
            (data['vehicle_id'], data['service_date'], data['time_slot'], data.get('status', 'Scheduled'), data.get('notes', ''))
        )
        conn.commit()
        appointment_id = cursor.lastrowid
        
        # Create invoice for appointment
        cursor.execute(
            'INSERT INTO invoices (appointment_id, total_amount) VALUES (?, ?)',
            (appointment_id, 0)
        )
        conn.commit()
        conn.close()
        return jsonify({'id': appointment_id, 'message': 'Appointment scheduled successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/appointments/<int:id>/status', methods=['PUT'])
def update_appointment_status(id):
    try:
        data = request.json
        conn = get_db_connection()
        conn.execute(
            'UPDATE appointments SET status=? WHERE id=?',
            (data['status'], id)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Appointment status updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== INVOICE ROUTES ====================
@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    try:
        conn = get_db_connection()
        invoices = conn.execute('''
            SELECT i.*, a.service_date, v.registration_number, c.name as customer_name 
            FROM invoices i 
            JOIN appointments a ON i.appointment_id = a.id
            JOIN vehicles v ON a.vehicle_id = v.id
            JOIN customers c ON v.customer_id = c.id
            ORDER BY i.created_at DESC
        ''').fetchall()
        conn.close()
        return jsonify([dict(invoice) for invoice in invoices])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/invoices/<int:id>/payment', methods=['PUT'])
def update_invoice_payment(id):
    try:
        data = request.json
        conn = get_db_connection()
        
        # Update paid amount and payment status
        if data.get('paid_amount') == data.get('total_amount'):
            status = 'Paid'
        elif data.get('paid_amount') > 0:
            status = 'Partial'
        else:
            status = 'Pending'
        
        conn.execute(
            'UPDATE invoices SET paid_amount=?, payment_status=? WHERE id=?',
            (data['paid_amount'], status, id)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Payment updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== DASHBOARD STATS ====================
@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        conn = get_db_connection()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Today's appointments
        today_appointments = conn.execute(
            'SELECT COUNT(*) as count FROM appointments WHERE service_date=?',
            (today,)
        ).fetchone()['count']
        
        # Pending invoices count
        pending_invoices = conn.execute(
            'SELECT COUNT(*) as count FROM invoices WHERE payment_status != "Paid"'
        ).fetchone()['count']
        
        # Total due amount
        total_due = conn.execute(
            'SELECT SUM(total_amount - paid_amount) as total FROM invoices WHERE payment_status != "Paid"'
        ).fetchone()['total']
        if total_due is None:
            total_due = 0
        
        # Total customers
        total_customers = conn.execute('SELECT COUNT(*) as count FROM customers').fetchone()['count']
        
        # Total vehicles
        total_vehicles = conn.execute('SELECT COUNT(*) as count FROM vehicles').fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'today_appointments': today_appointments,
            'pending_invoices': pending_invoices,
            'total_due': total_due,
            'total_customers': total_customers,
            'total_vehicles': total_vehicles
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'message': 'Check / for available endpoints'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

# ==================== RUN APPLICATION ====================
if __name__ == '__main__':
    app.run(debug=True, port=5500)