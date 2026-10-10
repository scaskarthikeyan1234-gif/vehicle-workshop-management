// API Base URL - Make sure this matches your backend
const API_BASE = 'http://127.0.0.1:5500/api';

// State management
let currentCustomers = [];
let currentVehicles = [];
let currentServices = [];
let currentAppointments = [];
let currentInvoices = [];

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Frontend loaded, connecting to backend at:', API_BASE);
    
    // Test backend connection
    testBackendConnection();
    
    // Load dashboard data
    loadDashboardData();
    
    // Setup navigation
    setupNavigation();
    
    // Setup modal close buttons
    setupModals();
});

// Test backend connection
async function testBackendConnection() {
    try {
        const response = await fetch('http://127.0.0.1:5000/');
        const data = await response.json();
        console.log('✅ Backend connected successfully!', data);
        
        // Show success message in console
        document.querySelector('.user-info span').textContent = 'Connected';
    } catch (error) {
        console.error('❌ Cannot connect to backend. Make sure app.py is running!', error);
        alert('ERROR: Backend server not running! Please start app.py first.\n\n1. Open Terminal\n2. cd backend\n3. python app.py');
    }
}

// Navigation setup
function setupNavigation() {
    document.querySelectorAll('.sidebar nav ul li').forEach(item => {
        item.addEventListener('click', function() {
            document.querySelectorAll('.sidebar nav ul li').forEach(li => li.classList.remove('active'));
            this.classList.add('active');
            
            const pageId = this.dataset.page;
            document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
            document.getElementById('page-title').textContent = this.querySelector('span').textContent;
            
            // Load page data
            loadPageData(pageId);
        });
    });
}

// Modal setup
function setupModals() {
    // Close modals when clicking on X
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.onclick = function() {
            this.closest('.modal').style.display = 'none';
        };
    });

    // Close modals when clicking outside
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    };
}

// Load data based on current page
function loadPageData(page) {
    switch(page) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'customers':
            loadCustomers();
            break;
        case 'vehicles':
            loadVehicles();
            break;
        case 'services':
            loadServices();
            break;
        case 'appointments':
            loadAppointments();
            break;
        case 'invoices':
            loadInvoices();
            break;
    }
}

// ==================== DASHBOARD FUNCTIONS ====================
async function loadDashboardData() {
    try {
        console.log('Loading dashboard data...');
        const response = await fetch(`${API_BASE}/dashboard/stats`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const stats = await response.json();
        console.log('Dashboard stats:', stats);
        
        document.getElementById('today-appointments').textContent = stats.today_appointments || 0;
        document.getElementById('pending-invoices').textContent = stats.pending_invoices || 0;
        document.getElementById('total-due').textContent = `$${(stats.total_due || 0).toFixed(2)}`;
        document.getElementById('total-customers').textContent = stats.total_customers || 0;
        document.getElementById('total-vehicles').textContent = stats.total_vehicles || 0;
        
        // Load recent appointments
        loadRecentAppointments();
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Failed to load dashboard data. Check if backend is running.');
    }
}

async function loadRecentAppointments() {
    try {
        const response = await fetch(`${API_BASE}/appointments`);
        const appointments = await response.json();
        
        const tbody = document.querySelector('#recent-appointments tbody');
        if (tbody) {
            tbody.innerHTML = '';
            
            appointments.slice(0, 5).forEach(app => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${app.customer_name || 'N/A'}</td>
                    <td>${app.make || ''} ${app.model || ''} (${app.registration_number || 'N/A'})</td>
                    <td>${app.service_date || 'N/A'}</td>
                    <td>${app.time_slot || 'N/A'}</td>
                    <td><span class="status-${(app.status || 'scheduled').toLowerCase()}">${app.status || 'Scheduled'}</span></td>
                `;
            });
        }
    } catch (error) {
        console.error('Error loading appointments:', error);
    }
}

// ==================== CUSTOMER FUNCTIONS ====================
async function loadCustomers() {
    try {
        const response = await fetch(`${API_BASE}/customers`);
        currentCustomers = await response.json();
        
        const tbody = document.querySelector('#customers-table tbody');
        if (tbody) {
            tbody.innerHTML = '';
            
            currentCustomers.forEach(customer => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${customer.name || ''}</td>
                    <td>${customer.phone || ''}</td>
                    <td>${customer.email || '-'}</td>
                    <td>${customer.address || '-'}</td>
                    <td>
                        <button class="btn-edit" onclick="editCustomer(${customer.id})">Edit</button>
                        <button class="btn-delete" onclick="deleteCustomer(${customer.id})">Delete</button>
                    </td>
                `;
            });
        }
        
        updateCustomerDropdown();
    } catch (error) {
        console.error('Error loading customers:', error);
    }
}

function updateCustomerDropdown() {
    const select = document.getElementById('vehicleCustomerId');
    if (select) {
        select.innerHTML = '<option value="">Select Customer</option>';
        currentCustomers.forEach(customer => {
            select.innerHTML += `<option value="${customer.id}">${customer.name} (${customer.phone})</option>`;
        });
    }
}

// Show Add Customer Modal
function showAddCustomerModal() {
    const modal = document.getElementById('customerModal');
    if (modal) {
        modal.style.display = 'block';
        
        const form = document.getElementById('customerForm');
        form.onsubmit = function(e) {
            e.preventDefault();
            addCustomer();
        };
    }
}

async function addCustomer() {
    const customer = {
        name: document.getElementById('customerName').value,
        phone: document.getElementById('customerPhone').value,
        email: document.getElementById('customerEmail').value,
        address: document.getElementById('customerAddress').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/customers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(customer)
        });
        
        if (response.ok) {
            closeModal('customerModal');
            await loadCustomers();
            clearCustomerForm();
            alert('Customer added successfully!');
        } else {
            const error = await response.json();
            alert('Error: ' + (error.error || 'Failed to add customer'));
        }
    } catch (error) {
        console.error('Error adding customer:', error);
        alert('Failed to connect to server. Make sure backend is running.');
    }
}

async function deleteCustomer(id) {
    if (confirm('Are you sure you want to delete this customer?')) {
        try {
            const response = await fetch(`${API_BASE}/customers/${id}`, { 
                method: 'DELETE' 
            });
            if (response.ok) {
                await loadCustomers();
                alert('Customer deleted successfully!');
            }
        } catch (error) {
            console.error('Error deleting customer:', error);
            alert('Failed to delete customer');
        }
    }
}

// ==================== VEHICLE FUNCTIONS ====================
async function loadVehicles() {
    try {
        const response = await fetch(`${API_BASE}/vehicles`);
        currentVehicles = await response.json();
        
        const tbody = document.querySelector('#vehicles-table tbody');
        if (tbody) {
            tbody.innerHTML = '';
            
            currentVehicles.forEach(vehicle => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${vehicle.registration_number || ''}</td>
                    <td>${vehicle.make || ''}</td>
                    <td>${vehicle.model || ''}</td>
                    <td>${vehicle.year || '-'}</td>
                    <td>${vehicle.customer_name || ''}</td>
                    <td>
                        <button class="btn-delete" onclick="deleteVehicle(${vehicle.id})">Delete</button>
                    </td>
                `;
            });
        }
        
        updateVehicleDropdown();
    } catch (error) {
        console.error('Error loading vehicles:', error);
    }
}

function updateVehicleDropdown() {
    const select = document.getElementById('appointmentVehicleId');
    if (select) {
        select.innerHTML = '<option value="">Select Vehicle</option>';
        currentVehicles.forEach(vehicle => {
            select.innerHTML += `<option value="${vehicle.id}">${vehicle.registration_number} - ${vehicle.make} ${vehicle.model}</option>`;
        });
    }
}

function showAddVehicleModal() {
    // First load customers for dropdown
    loadCustomers().then(() => {
        const modal = document.getElementById('vehicleModal');
        if (modal) {
            modal.style.display = 'block';
            
            const form = document.getElementById('vehicleForm');
            form.onsubmit = function(e) {
                e.preventDefault();
                addVehicle();
            };
        }
    });
}

async function addVehicle() {
    const vehicle = {
        customer_id: document.getElementById('vehicleCustomerId').value,
        registration_number: document.getElementById('vehicleRegNo').value,
        make: document.getElementById('vehicleMake').value,
        model: document.getElementById('vehicleModel').value,
        year: document.getElementById('vehicleYear').value
    };
    
    if (!vehicle.customer_id) {
        alert('Please select a customer');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/vehicles`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(vehicle)
        });
        
        if (response.ok) {
            closeModal('vehicleModal');
            await loadVehicles();
            clearVehicleForm();
            alert('Vehicle added successfully!');
        } else {
            const data = await response.json();
            alert(data.error || 'Error adding vehicle');
        }
    } catch (error) {
        console.error('Error adding vehicle:', error);
        alert('Failed to connect to server.');
    }
}

async function deleteVehicle(id) {
    if (confirm('Are you sure you want to delete this vehicle?')) {
        try {
            const response = await fetch(`${API_BASE}/vehicles/${id}`, { 
                method: 'DELETE' 
            });
            if (response.ok) {
                await loadVehicles();
                alert('Vehicle deleted successfully!');
            }
        } catch (error) {
            console.error('Error deleting vehicle:', error);
            alert('Failed to delete vehicle');
        }
    }
}

// ==================== SERVICE FUNCTIONS ====================
async function loadServices() {
    try {
        const response = await fetch(`${API_BASE}/services`);
        currentServices = await response.json();
        
        const tbody = document.querySelector('#services-table tbody');
        if (tbody) {
            tbody.innerHTML = '';
            
            currentServices.forEach(service => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${service.name || ''}</td>
                    <td>${service.description || '-'}</td>
                    <td>$${(service.price || 0).toFixed(2)}</td>
                    <td>${service.category || ''}</td>
                    <td>
                        <button class="btn-edit" onclick="editService(${service.id})">Edit</button>
                        <button class="btn-delete" onclick="deleteService(${service.id})">Delete</button>
                    </td>
                `;
            });
        }
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

function showAddServiceModal() {
    const modal = document.getElementById('serviceModal');
    if (modal) {
        modal.style.display = 'block';
        
        const form = document.getElementById('serviceForm');
        form.onsubmit = function(e) {
            e.preventDefault();
            addService();
        };
    }
}

async function addService() {
    const service = {
        name: document.getElementById('serviceName').value,
        description: document.getElementById('serviceDescription').value,
        price: parseFloat(document.getElementById('servicePrice').value),
        category: document.getElementById('serviceCategory').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/services`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(service)
        });
        
        if (response.ok) {
            closeModal('serviceModal');
            await loadServices();
            clearServiceForm();
            alert('Service added successfully!');
        }
    } catch (error) {
        console.error('Error adding service:', error);
        alert('Failed to add service');
    }
}

async function deleteService(id) {
    if (confirm('Are you sure you want to delete this service?')) {
        try {
            const response = await fetch(`${API_BASE}/services/${id}`, { 
                method: 'DELETE' 
            });
            if (response.ok) {
                await loadServices();
                alert('Service deleted successfully!');
            }
        } catch (error) {
            console.error('Error deleting service:', error);
            alert('Failed to delete service');
        }
    }
}

// ==================== APPOINTMENT FUNCTIONS ====================
async function loadAppointments() {
    try {
        const response = await fetch(`${API_BASE}/appointments`);
        currentAppointments = await response.json();
        
        const tbody = document.querySelector('#appointments-table tbody');
        if (tbody) {
            tbody.innerHTML = '';
            
            currentAppointments.forEach(app => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${app.customer_name || ''}</td>
                    <td>${app.make || ''} ${app.model || ''}</td>
                    <td>${app.service_date || ''}</td>
                    <td>${app.time_slot || ''}</td>
                    <td><span class="status-${(app.status || 'scheduled').toLowerCase()}">${app.status || 'Scheduled'}</span></td>
                    <td>
                        <button class="btn-edit" onclick="updateAppointmentStatus(${app.id}, 'In Progress')">Start</button>
                        <button class="btn-pay" onclick="updateAppointmentStatus(${app.id}, 'Completed')">Complete</button>
                    </td>
                `;
            });
        }
    } catch (error) {
        console.error('Error loading appointments:', error);
    }
}

function showAddAppointmentModal() {
    // First load vehicles for dropdown
    loadVehicles().then(() => {
        const modal = document.getElementById('appointmentModal');
        if (modal) {
            modal.style.display = 'block';
            
            const form = document.getElementById('appointmentForm');
            form.onsubmit = function(e) {
                e.preventDefault();
                addAppointment();
            };
            
            // Set min date to today
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('appointmentDate').min = today;
        }
    });
}

async function addAppointment() {
    const appointment = {
        vehicle_id: document.getElementById('appointmentVehicleId').value,
        service_date: document.getElementById('appointmentDate').value,
        time_slot: document.getElementById('appointmentTime').value,
        notes: document.getElementById('appointmentNotes').value
    };
    
    if (!appointment.vehicle_id) {
        alert('Please select a vehicle');
        return;
    }
    
    if (!appointment.service_date) {
        alert('Please select a date');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/appointments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(appointment)
        });
        
        if (response.ok) {
            closeModal('appointmentModal');
            await loadAppointments();
            clearAppointmentForm();
            alert('Appointment scheduled successfully!');
        } else {
            const error = await response.json();
            alert('Error: ' + (error.error || 'Failed to schedule appointment'));
        }
    } catch (error) {
        console.error('Error adding appointment:', error);
        alert('Failed to connect to server');
    }
}

async function updateAppointmentStatus(id, status) {
    try {
        const response = await fetch(`${API_BASE}/appointments/${id}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        
        if (response.ok) {
            await loadAppointments();
            await loadDashboardData(); // Update dashboard stats
            alert(`Appointment marked as ${status}`);
        }
    } catch (error) {
        console.error('Error updating appointment:', error);
        alert('Failed to update appointment');
    }
}

// ==================== INVOICE FUNCTIONS ====================
async function loadInvoices() {
    try {
        const response = await fetch(`${API_BASE}/invoices`);
        currentInvoices = await response.json();
        
        const tbody = document.querySelector('#invoices-table tbody');
        if (tbody) {
            tbody.innerHTML = '';
            
            currentInvoices.forEach(invoice => {
                const row = tbody.insertRow();
                const dueAmount = (invoice.total_amount || 0) - (invoice.paid_amount || 0);
                row.innerHTML = `
                    <td>#${invoice.id}</td>
                    <td>${invoice.customer_name || ''}</td>
                    <td>${invoice.registration_number || ''}</td>
                    <td>${invoice.service_date || ''}</td>
                    <td>$${(invoice.total_amount || 0).toFixed(2)}</td>
                    <td>$${(invoice.paid_amount || 0).toFixed(2)}</td>
                    <td><span class="status-${(invoice.payment_status || 'pending').toLowerCase()}">${invoice.payment_status || 'Pending'}</span></td>
                    <td>
                        ${dueAmount > 0 ? `<button class="btn-pay" onclick="processPayment(${invoice.id})">Pay $${dueAmount.toFixed(2)}</button>` : 'Paid'}
                    </td>
                `;
            });
        }
    } catch (error) {
        console.error('Error loading invoices:', error);
    }
}

async function processPayment(invoiceId) {
    const invoice = currentInvoices.find(i => i.id === invoiceId);
    const dueAmount = (invoice.total_amount || 0) - (invoice.paid_amount || 0);
    
    const amount = prompt(`Enter payment amount (Max: $${dueAmount.toFixed(2)}):`, dueAmount.toFixed(2));
    if (amount && !isNaN(amount) && parseFloat(amount) > 0) {
        const paymentAmount = parseFloat(amount);
        if (paymentAmount > dueAmount) {
            alert(`Payment cannot exceed $${dueAmount.toFixed(2)}`);
            return;
        }
        
        const newPaidAmount = (invoice.paid_amount || 0) + paymentAmount;
        
        try {
            const response = await fetch(`${API_BASE}/invoices/${invoiceId}/payment`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    paid_amount: newPaidAmount,
                    total_amount: invoice.total_amount || 0
                })
            });
            
            if (response.ok) {
                await loadInvoices();
                await loadDashboardData(); // Update dashboard stats
                alert('Payment processed successfully!');
            }
        } catch (error) {
            console.error('Error processing payment:', error);
            alert('Failed to process payment');
        }
    }
}

// ==================== UTILITY FUNCTIONS ====================
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

function clearCustomerForm() {
    document.getElementById('customerName').value = '';
    document.getElementById('customerPhone').value = '';
    document.getElementById('customerEmail').value = '';
    document.getElementById('customerAddress').value = '';
}

function clearVehicleForm() {
    document.getElementById('vehicleCustomerId').value = '';
    document.getElementById('vehicleRegNo').value = '';
    document.getElementById('vehicleMake').value = '';
    document.getElementById('vehicleModel').value = '';
    document.getElementById('vehicleYear').value = '';
}

function clearServiceForm() {
    document.getElementById('serviceName').value = '';
    document.getElementById('serviceDescription').value = '';
    document.getElementById('servicePrice').value = '';
    document.getElementById('serviceCategory').value = 'Maintenance';
}

function clearAppointmentForm() {
    document.getElementById('appointmentVehicleId').value = '';
    document.getElementById('appointmentDate').value = '';
    document.getElementById('appointmentTime').value = '09:00';
    document.getElementById('appointmentNotes').value = '';
}

function showError(message) {
    console.error(message);
    alert('Error: ' + message);
}

// Edit functions (placeholder - can be implemented later)
function editCustomer(id) {
    const customer = currentCustomers.find(c => c.id === id);
    if (customer) {
        alert(`Edit customer: ${customer.name}\nThis feature will be implemented soon!`);
    }
}

function editService(id) {
    const service = currentServices.find(s => s.id === id);
    if (service) {
        alert(`Edit service: ${service.name}\nThis feature will be implemented soon!`);
    }
}

// Make functions available globally for HTML onclick events
window.showAddCustomerModal = showAddCustomerModal;
window.showAddVehicleModal = showAddVehicleModal;
window.showAddServiceModal = showAddServiceModal;
window.showAddAppointmentModal = showAddAppointmentModal;
window.deleteCustomer = deleteCustomer;
window.deleteVehicle = deleteVehicle;
window.deleteService = deleteService;
window.editCustomer = editCustomer;
window.editService = editService;
window.updateAppointmentStatus = updateAppointmentStatus;
window.processPayment = processPayment;