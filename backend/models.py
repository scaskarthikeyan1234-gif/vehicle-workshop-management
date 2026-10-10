from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Customer Model
class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    vehicles = db.relationship('Vehicle', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<Customer {self.name}>'


# Vehicle Model
class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    registration_number = db.Column(db.String(50), unique=True, nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.owner.name if self.owner else None,
            'registration_number': self.registration_number,
            'make': self.make,
            'model': self.model,
            'year': self.year
        }
    
    def __repr__(self):
        return f'<Vehicle {self.registration_number}>'


# Service Model
class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    
    # Relationships
    invoice_items = db.relationship('InvoiceItem', backref='service', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category
        }
    
    def __repr__(self):
        return f'<Service {self.name}>'


# Appointment Model
class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), default='Scheduled')  # Scheduled, In Progress, Completed, Cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    invoice = db.relationship('Invoice', backref='appointment', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'registration_number': self.vehicle.registration_number if self.vehicle else None,
            'make': self.vehicle.make if self.vehicle else None,
            'model': self.vehicle.model if self.vehicle else None,
            'customer_name': self.vehicle.owner.name if self.vehicle and self.vehicle.owner else None,
            'service_date': self.service_date.strftime('%Y-%m-%d') if self.service_date else None,
            'time_slot': self.time_slot,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.service_date}>'


# Invoice Model
class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False, unique=True)
    total_amount = db.Column(db.Float, nullable=False, default=0)
    paid_amount = db.Column(db.Float, default=0)
    payment_status = db.Column(db.String(50), default='Pending')  # Pending, Partial, Paid
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'customer_name': self.appointment.vehicle.owner.name if self.appointment and self.appointment.vehicle and self.appointment.vehicle.owner else None,
            'registration_number': self.appointment.vehicle.registration_number if self.appointment and self.appointment.vehicle else None,
            'service_date': self.appointment.service_date.strftime('%Y-%m-%d') if self.appointment and self.appointment.service_date else None,
            'total_amount': self.total_amount,
            'paid_amount': self.paid_amount,
            'payment_status': self.payment_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': [item.to_dict() for item in self.items]
        }
    
    def update_status(self):
        """Update payment status based on paid amount"""
        if self.paid_amount >= self.total_amount:
            self.payment_status = 'Paid'
        elif self.paid_amount > 0:
            self.payment_status = 'Partial'
        else:
            self.payment_status = 'Pending'
    
    def __repr__(self):
        return f'<Invoice {self.id} - {self.payment_status}>'


# Invoice Item Model (for services in invoice)
class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)  # Price at time of service
    description = db.Column(db.String(200))
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'service_id': self.service_id,
            'service_name': self.service.name if self.service else None,
            'quantity': self.quantity,
            'price': self.price,
            'description': self.description,
            'subtotal': self.quantity * self.price
        }
    
    def __repr__(self):
        return f'<InvoiceItem {self.id} - {self.service_id}>'


# Initialize database function
def init_db(app):
    """Initialize database with tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
        
        # Add sample services if table is empty
        if Service.query.count() == 0:
            sample_services = [
                Service(name='Oil Change', description='Engine oil change with filter replacement', price=50.00, category='Maintenance'),
                Service(name='Tire Rotation', description='Rotate all four tires and check pressure', price=30.00, category='Maintenance'),
                Service(name='Brake Pad Replacement', description='Replace front/rear brake pads', price=150.00, category='Repair'),
                Service(name='Engine Diagnostic', description='Complete engine diagnostic check', price=80.00, category='Diagnostic'),
                Service(name='AC Service', description='Air conditioning system service', price=100.00, category='Maintenance'),
                Service(name='Battery Replacement', description='Replace old battery with new one', price=120.00, category='Repair'),
                Service(name='Wheel Alignment', description='Complete wheel alignment service', price=60.00, category='Maintenance'),
                Service(name='Car Wash', description='Exterior and interior car wash', price=25.00, category='Cleaning'),
                Service(name='Spark Plug Replacement', description='Replace spark plugs', price=90.00, category='Maintenance'),
                Service(name='Coolant Flush', description='Engine coolant system flush', price=70.00, category='Maintenance'),
                Service(name='Transmission Service', description='Transmission fluid change', price=120.00, category='Maintenance'),
                Service(name='AC Recharge', description='Air conditioning refrigerant recharge', price=80.00, category='Repair'),
                Service(name='Headlight Restoration', description='Restore cloudy headlights', price=40.00, category='Cleaning'),
                Service(name='Wheel Balancing', description='Balance all wheels', price=35.00, category='Maintenance'),
                Service(name='Timing Belt Replacement', description='Replace timing belt', price=250.00, category='Repair')
            ]
            db.session.bulk_save_objects(sample_services)
            db.session.commit()
            print("Sample services added successfully!")