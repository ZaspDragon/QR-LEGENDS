#!/usr/bin/env python3
"""
QR Legends Warehouse Management System
Clean and optimized version with error fixes
"""

try:
    from flask import Flask, request, jsonify, send_from_directory, session, redirect, make_response, render_template_string, send_file, url_for, abort, Response
    from flask_cors import CORS
    import json
    import os
    from datetime import datetime, timedelta
    import uuid
    import hashlib
    import secrets
    import re
    from werkzeug.security import generate_password_hash, check_password_hash
    import qrcode
    from io import BytesIO
    import base64
    import io
    import requests
    import threading
    import time
    import random
    import logging
    import traceback
    import sys

    # Optional imports with fallbacks
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Warning: PIL not available - QR generation will use fallback")
        Image = None
        ImageDraw = None
        ImageFont = None

except ImportError as e:
    print(f"❌ Critical import error: {e}")
    print("💡 Please install required packages:")
    print("   pip install flask flask-cors qrcode[pil] requests werkzeug pillow")
    sys.exit(1)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Import modules with proper error handling
backup_service = None
auto_backup_trigger = None

try:
    from backup_service import backup_service, auto_backup_trigger
    print("✅ Backup service loaded")
except ImportError as e:
    print(f"⚠️ Backup service not available: {e}")
    class MockBackupService:
        def create_backup(self, company_id, backup_type='full'):
            return {'success': True, 'message': 'Backup service not available'}
        def log_change(self, company_id, change_type, data):
            print(f"📝 Mock logged change: {change_type}")

    class MockAutoBackupTrigger:
        def __init__(self, backup_service=None):
            self.backup_service = backup_service
        def log_change(self, company_id, change_type, data):
            print(f"📝 Mock logged change: {change_type}")
        def log_cycle_count(self, company_id, count_data):
            return {'success': True, 'logged_at': datetime.now().isoformat()}
        def log_appliance_analysis(self, company_id, analysis_data):
            return {'success': True, 'logged_at': datetime.now().isoformat()}

    backup_service = MockBackupService()
    auto_backup_trigger = MockAutoBackupTrigger(backup_service)

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
DATA_DIR = os.environ.get('DATA_DIR', os.path.join(BASE_DIR, 'data'))
SESSION_DIR = os.path.join(BASE_DIR, 'flask_session')

# Legacy modules use relative paths. Anchoring the process here keeps those
# paths stable under Gunicorn and when launched outside the repository folder.
os.chdir(BASE_DIR)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

# Initialize Flask app
app = Flask(__name__, static_folder=STATIC_DIR)
is_production = os.environ.get('FLASK_ENV', '').lower() == 'production'
configured_secret_key = os.environ.get('SECRET_KEY')
if is_production and not configured_secret_key:
    raise RuntimeError("SECRET_KEY must be set when FLASK_ENV=production")
app.secret_key = configured_secret_key or secrets.token_hex(32)
if not configured_secret_key:
    logger.warning("SECRET_KEY is not set; generated an ephemeral local key")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = SESSION_DIR
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'qr_legends:'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_COOKIE_SECURE'] = is_production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_REFRESH_EACH_REQUEST'] = False
CORS(app, supports_credentials=True)

# Global data storage
inventory_items = {}
containers = {}
container_actions = {}
activity_logs = {}
scan_logs = []
companies = {}
employees = {}
product_tracking = {}
lift_driver_assignments = {}
lift_driver_tasks = {}
subscriptions = {}
notifications = {}
user_activity = {}
deliveries = {}
delivery_completions = {}
freight_deliveries = {}
receiver_qrs = {}
sop_library = {}
dropoff_locations = {}
item_images = {}
persistent_sessions = {}
security_cameras = {}
qr_codes = {}
purchase_order_qrs = {}
purchase_orders = {}  # Purchase Orders with line items
asns = {}  # Advanced Shipping Notices
password_reset_tokens = {}  # Temporary storage for password reset tokens
warehouse_activity_history = {}  # Warehouse movements, receiving, and transfers history

# Demo account configuration
DEMO_PREMIUM_ACCOUNTS = ['qrlegends22@gmail.com']

def is_demo_premium_account(email):
    """Check if account has unlimited demo access"""
    return email in DEMO_PREMIUM_ACCOUNTS

# Define file paths for data persistence
COMPANIES_FILE = os.path.join(DATA_DIR, 'companies.json')
EMPLOYEES_FILE = os.path.join(DATA_DIR, 'employees.json')
INVENTORY_FILE = os.path.join(DATA_DIR, 'inventory_items.json')
SCAN_LOGS_FILE = os.path.join(DATA_DIR, 'scan_logs.json')
ACTIVITY_LOGS_FILE = os.path.join(DATA_DIR, 'activity_logs.json')
CONTAINERS_FILE = os.path.join(DATA_DIR, 'containers.json')
CONTAINER_ACTIONS_FILE = os.path.join(DATA_DIR, 'container_actions.json')
PRODUCT_TRACKING_FILE = os.path.join(DATA_DIR, 'product_tracking.json')
SUBSCRIPTIONS_FILE = os.path.join(DATA_DIR, 'subscriptions.json')
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, 'notifications.json')
USER_ACTIVITY_FILE = os.path.join(DATA_DIR, 'user_activity.json')
DELIVERIES_FILE = os.path.join(DATA_DIR, 'deliveries.json')
DELIVERY_COMPLETIONS_FILE = os.path.join(DATA_DIR, 'delivery_completions.json')
FREIGHT_DELIVERIES_FILE = os.path.join(DATA_DIR, 'freight_deliveries.json')
RECEIVER_QRS_FILE = os.path.join(DATA_DIR, 'receiver_qrs.json')
SOP_LIBRARY_FILE = os.path.join(DATA_DIR, 'sop_library.json')
DROPOFF_LOCATIONS_FILE = os.path.join(DATA_DIR, 'dropoff_locations.json')
ITEM_IMAGES_FILE = os.path.join(DATA_DIR, 'item_images.json')
PERSISTENT_SESSIONS_FILE = os.path.join(DATA_DIR, 'persistent_sessions.json')
SECURITY_CAMERAS_FILE = os.path.join(DATA_DIR, 'security_cameras.json')
QR_CODES_FILE = os.path.join(DATA_DIR, 'qr_codes.json')
PURCHASE_ORDER_QRS_FILE = os.path.join(DATA_DIR, 'purchase_order_qrs.json')
PURCHASE_ORDERS_FILE = os.path.join(DATA_DIR, 'purchase_orders.json')
ASNS_FILE = os.path.join(DATA_DIR, 'asns.json')
WAREHOUSE_ACTIVITY_HISTORY_FILE = os.path.join(DATA_DIR, 'warehouse_activity_history.json')

# Helper functions for JSON data handling
def load_json_data(filepath):
    """Load JSON data from a file, returning an empty dict or list if file is empty or doesn't exist."""
    if not os.path.exists(filepath):
        return {} if filepath.endswith('.json') else []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {} if filepath.endswith('.json') else []
            return json.loads(content)
    except json.JSONDecodeError:
        logger.error(f"JSON decode error in {filepath}. Returning empty.")
        return {} if filepath.endswith('.json') else []
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        return {} if filepath.endswith('.json') else []

def save_json_data(filepath, data):
    """Save data to a JSON file."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")

# Load data from files
def load_data():
    """Load all data from JSON files"""
    global inventory_items, containers, container_actions, activity_logs
    global scan_logs, companies, employees, product_tracking, subscriptions
    global notifications, user_activity, deliveries, delivery_completions, freight_deliveries, receiver_qrs, sop_library, dropoff_locations, item_images, persistent_sessions, security_cameras, qr_codes, purchase_order_qrs, purchase_orders, asns, warehouse_activity_history

    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        print(f"📁 Data directory created/verified: {DATA_DIR}")

        files_to_load = {
            COMPANIES_FILE: companies,
            EMPLOYEES_FILE: employees,
            INVENTORY_FILE: inventory_items,
            SCAN_LOGS_FILE: scan_logs,
            ACTIVITY_LOGS_FILE: activity_logs,
            CONTAINERS_FILE: containers,
            CONTAINER_ACTIONS_FILE: container_actions,
            PRODUCT_TRACKING_FILE: product_tracking,
            SUBSCRIPTIONS_FILE: subscriptions,
            NOTIFICATIONS_FILE: notifications,
            USER_ACTIVITY_FILE: user_activity,
            DELIVERIES_FILE: deliveries,
            DELIVERY_COMPLETIONS_FILE: delivery_completions,
            FREIGHT_DELIVERIES_FILE: freight_deliveries,
            RECEIVER_QRS_FILE: receiver_qrs,
            SOP_LIBRARY_FILE: sop_library,
            DROPOFF_LOCATIONS_FILE: dropoff_locations,
            ITEM_IMAGES_FILE: item_images,
            PERSISTENT_SESSIONS_FILE: persistent_sessions,
            SECURITY_CAMERAS_FILE: security_cameras,
            QR_CODES_FILE: qr_codes,
            PURCHASE_ORDER_QRS_FILE: purchase_order_qrs,
            PURCHASE_ORDERS_FILE: purchase_orders,
            ASNS_FILE: asns,
            WAREHOUSE_ACTIVITY_HISTORY_FILE: warehouse_activity_history
        }

        for filepath, data_dict in files_to_load.items():
            loaded_data = load_json_data(filepath)
            if isinstance(data_dict, list):
                if isinstance(loaded_data, list):
                    data_dict.clear()
                    data_dict.extend(loaded_data)
            elif isinstance(data_dict, dict):
                if isinstance(loaded_data, dict):
                    data_dict.update(loaded_data)
            print(f"✅ Loaded {filepath}")

        print("📊 Data loading completed")

    except Exception as e:
        print(f"❌ Critical error in load_data(): {e}")
        logger.error(f"Critical error in load_data(): {e}")

def save_data():
    """Save all data to JSON files"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)

        data_files = {
            COMPANIES_FILE: companies,
            EMPLOYEES_FILE: employees,
            INVENTORY_FILE: inventory_items,
            SCAN_LOGS_FILE: scan_logs,
            ACTIVITY_LOGS_FILE: activity_logs,
            CONTAINERS_FILE: containers,
            CONTAINER_ACTIONS_FILE: container_actions,
            PRODUCT_TRACKING_FILE: product_tracking,
            SUBSCRIPTIONS_FILE: subscriptions,
            NOTIFICATIONS_FILE: notifications,
            USER_ACTIVITY_FILE: user_activity,
            DELIVERIES_FILE: deliveries,
            DELIVERY_COMPLETIONS_FILE: delivery_completions,
            FREIGHT_DELIVERIES_FILE: freight_deliveries,
            RECEIVER_QRS_FILE: receiver_qrs,
            SOP_LIBRARY_FILE: sop_library,
            DROPOFF_LOCATIONS_FILE: dropoff_locations,
            ITEM_IMAGES_FILE: item_images,
            PERSISTENT_SESSIONS_FILE: persistent_sessions,
            SECURITY_CAMERAS_FILE: security_cameras,
            QR_CODES_FILE: qr_codes,
            PURCHASE_ORDER_QRS_FILE: purchase_order_qrs,
            PURCHASE_ORDERS_FILE: purchase_orders,
            ASNS_FILE: asns,
            WAREHOUSE_ACTIVITY_HISTORY_FILE: warehouse_activity_history
        }

        for filepath, data in data_files.items():
            save_json_data(filepath, data)

        logger.info("All data saved successfully")
    except Exception as e:
        logger.error(f"Error saving data: {e}")

@app.before_request
def before_request():
    """Log incoming requests and add request ID"""
    request.start_time = time.time()
    request.request_id = str(uuid.uuid4())[:8]

    if not request.path.startswith('/static/'):
        logger.info(f"📥 [{request.request_id}] {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def after_request(response):
    """Add request ID to responses and log response"""
    try:
        if hasattr(request, 'request_id'):
            response.headers['X-Request-ID'] = request.request_id

        if hasattr(request, 'start_time') and not request.path.startswith('/static/'):
            duration = (time.time() - request.start_time) * 1000
            status_emoji = "✅" if response.status_code < 400 else "⚠️" if response.status_code < 500 else "🚨"
            logger.info(f"📤 [{getattr(request, 'request_id', 'unknown')}] {status_emoji} {response.status_code} - {duration:.1f}ms")

    except Exception as e:
        logger.error(f"Error in after_request: {e}")

    return response

def generate_qr_code(data):
    """Generate QR code image as base64 string"""
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return ""

def create_persistent_session(user_id, employee_id, username, role, company_id):
    """Create a persistent session that works across devices"""
    try:
        session_token = str(uuid.uuid4())
        session_data = {
            'user_id': user_id,
            'employee_id': employee_id,
            'username': username,
            'role': role,
            'company_id': company_id,
            'created_at': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
            'is_demo': session.get('is_demo', False)
        }

        persistent_sessions[session_token] = session_data
        save_data()

        session['user_id'] = user_id
        session['employee_id'] = employee_id
        session['username'] = username
        session['role'] = role
        session['company_id'] = company_id
        session['authenticated'] = True
        session['persistent_token'] = session_token
        session.permanent = True
        session.modified = True

        return session_token
    except Exception as e:
        logger.error(f"Error creating persistent session: {e}")
        return None

def get_session_from_token(token):
    """Get session data from persistent token"""
    try:
        if token in persistent_sessions:
            session_data = persistent_sessions[token]
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                del persistent_sessions[token]
                save_data()
                return None

            session_data['last_accessed'] = datetime.now().isoformat()
            persistent_sessions[token] = session_data
            save_data()
            return session_data
        return None
    except Exception as e:
        logger.error(f"Error getting session from token: {e}")
        return None

def get_current_user():
    """Get current user details from session or persistent token"""
    try:
        if session.get('authenticated'):
            return {
                'user_id': session.get('user_id'),
                'employee_id': session.get('employee_id'),
                'username': session.get('username'),
                'role': session.get('role'),
                'company_id': session.get('company_id'),
                'authenticated': True
            }

        persistent_token = request.headers.get('X-Session-Token') or request.cookies.get('persistent_token')
        if persistent_token:
            session_data = get_session_from_token(persistent_token)
            if session_data:
                session['user_id'] = session_data['user_id']
                session['employee_id'] = session_data['employee_id']
                session['username'] = session_data['username']
                session['role'] = session_data['role']
                session['company_id'] = session_data['company_id']
                session['authenticated'] = True
                session['persistent_token'] = persistent_token
                session.permanent = True
                session.modified = True
                return session_data

        return None
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return None

def get_current_session():
    """Get current session data with cross-device support"""
    return get_current_user()

def ensure_demo_premium_account():
    """Ensure demo premium account exists"""
    demo_email = 'qrlegends22@gmail.com'

    demo_user_exists = False
    demo_company_id = None

    for emp_id, emp_data in employees.items():
        if emp_data.get('email') == demo_email:
            demo_user_exists = True
            demo_company_id = emp_data.get('company_id')
            break

    if not demo_user_exists:
        demo_company_id = str(uuid.uuid4())
        companies[demo_company_id] = {
            'id': demo_company_id,
            'name': 'QR LEGENDS Demo Company',
            'email': demo_email,
            'password': 'demo123',
            'employer_code': 'DEMO2025',
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'plan': 'demo_premium'
        }

        # Create multiple demo employees with different roles
        demo_employees = [
            {
                'id': str(uuid.uuid4()),
                'username': 'qrlegends_admin',
                'email': demo_email,
                'first_name': 'QR Legends',
                'last_name': 'Demo Admin',
                'role': 'admin',
                'department': 'Administration',
                'employee_id': 'DEMO001',
                'widget_access': ['executive', 'manager', 'admin', 'user']
            },
            {
                'id': str(uuid.uuid4()),
                'username': 'demo_manager',
                'email': 'manager@qrlegends.com',
                'first_name': 'Sarah',
                'last_name': 'Manager',
                'role': 'manager',
                'department': 'Warehouse Operations',
                'employee_id': 'DEMO002',
                'widget_access': ['manager', 'admin', 'user']
            },
            {
                'id': str(uuid.uuid4()),
                'username': 'demo_supervisor',
                'email': 'supervisor@qrlegends.com',
                'first_name': 'Mike',
                'last_name': 'Supervisor',
                'role': 'supervisor',
                'department': 'Receiving',
                'employee_id': 'DEMO003',
                'widget_access': ['admin', 'user']
            },
            {
                'id': str(uuid.uuid4()),
                'username': 'demo_worker',
                'email': 'worker@qrlegends.com',
                'first_name': 'Lisa',
                'last_name': 'Worker',
                'role': 'user',
                'department': 'Order Picking',
                'employee_id': 'DEMO004',
                'widget_access': ['user']
            }
        ]

        for emp_data in demo_employees:
            emp_id = emp_data['id']
            employees[emp_id] = {
                'id': emp_id,
                'company_id': demo_company_id,
                'username': emp_data['username'],
                'password': 'demo123',
                'email': emp_data['email'],
                'first_name': emp_data['first_name'],
                'last_name': emp_data['last_name'],
                'role': emp_data['role'],
                'department': emp_data['department'],
                'employee_id': emp_data['employee_id'],
                'created_at': datetime.now().isoformat(),
                'is_demo_premium': True,
                'widget_access_level': emp_data['widget_access']
            }

        subscriptions[demo_company_id] = {
            'company_id': demo_company_id,
            'plan': 'demo_premium',
            'status': 'active',
            'unlimited_features': True,
            'created_at': datetime.now().isoformat()
        }

        save_data()
        logger.info(f"Created demo premium accounts with hierarchical roles")

# Routes for serving HTML pages
@app.route('/')
def root():
    return redirect('/company_login')

@app.route('/main_dashboard')
def main_dashboard():
    """Main company dashboard"""
    try:
        # Check if this is a demo login attempt first
        demo_email = request.args.get('demo_login')
        if demo_email == 'qrlegends22@gmail.com':
            # Create demo session
            session['user_id'] = 'demo_user'
            session['employee_id'] = 'demo_employee'
            session['username'] = 'QR Legends Demo User'
            session['role'] = 'admin'
            session['company_id'] = 'demo_company'
            session['authenticated'] = True
            session['is_demo'] = True
            session.permanent = True
            session.modified = True

            try:
                with open(os.path.join('static', 'main_dashboard.html'), 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    return html_content
            except FileNotFoundError:
                return "<h1>Dashboard - File Not Found</h1>", 404

        # Check for existing authentication - simplified logic
        if session.get('authenticated'):
            try:
                with open(os.path.join('static', 'main_dashboard.html'), 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    return html_content
            except FileNotFoundError:
                return "<h1>Dashboard - File Not Found</h1>", 404

        # Check persistent token
        persistent_token = request.headers.get('X-Session-Token') or request.cookies.get('persistent_token')
        if persistent_token:
            session_data = get_session_from_token(persistent_token)
            if session_data:
                # Restore session
                session['user_id'] = session_data['user_id']
                session['employee_id'] = session_data['employee_id']
                session['username'] = session_data['username']
                session['role'] = session_data['role']
                session['company_id'] = session_data['company_id']
                session['authenticated'] = True
                session.permanent = True
                session.modified = True

                try:
                    with open(os.path.join('static', 'main_dashboard.html'), 'r', encoding='utf-8') as f:
                        html_content = f.read()
                        return html_content
                except FileNotFoundError:
                    return "<h1>Dashboard - File Not Found</h1>", 404

        # No valid authentication found
        return redirect('/company_login')

    except Exception as e:
        logger.error(f"Main dashboard error: {e}")
        return redirect('/company_login')

@app.route('/control-center')
@app.route('/warehouse-os')
def warehouse_os():
    """WarehouseOS aliases use the authenticated Control Center."""
    return main_dashboard()

@app.route('/mobile_dashboard')
def mobile_dashboard():
    """Mobile-optimized dashboard"""
    return send_from_directory('static', 'mobile_dashboard.html')

@app.route('/company_login')
def company_login_page():
    try:
        with open(os.path.join('static', 'company_login.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Company Login - Page Not Found</h1>", 404

@app.route('/company_signup')
def company_signup_page():
    try:
        with open(os.path.join('static', 'company_signup.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Company Signup - Page Not Found</h1>", 404

@app.route('/employee_login')
def employee_login_page():
    return send_from_directory('static', 'employee_login.html')

@app.route('/forgot_password')
def forgot_password_page():
    """Serve forgot password page"""
    try:
        with open(os.path.join('static', 'forgot_password.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Forgot Password - Page Not Found</h1>", 404

@app.route('/reset_password')
def reset_password_page():
    """Serve reset password page"""
    try:
        with open(os.path.join('static', 'reset_password.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Reset Password - Page Not Found</h1>", 404

@app.route('/employee_demo_accounts')
def employee_demo_accounts():
    try:
        with open(os.path.join('static', 'employee_demo_accounts.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Employee Demo Accounts - File Not Found</h1>", 404

# HR & Employee Management Routes
@app.route('/erp_hr')
def erp_hr():
    try:
        with open(os.path.join('static', 'erp_hr.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>HR Portal - File Not Found</h1>", 404

@app.route('/hr_employee_directory')
def hr_employee_directory():
    try:
        with open(os.path.join('static', 'hr_employee_directory.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Employee Directory - File Not Found</h1>", 404

@app.route('/hr_payroll_processing')
def hr_payroll_processing():
    try:
        with open(os.path.join('static', 'hr_payroll_processing.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Payroll Processing - File Not Found</h1>", 404

@app.route('/hr_time_off_management')
def hr_time_off_management():
    try:
        with open(os.path.join('static', 'hr_time_off_management.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Time Off Management - File Not Found</h1>", 404

@app.route('/hr_recruitment_portal')
def hr_recruitment_portal():
    try:
        with open(os.path.join('static', 'hr_recruitment_portal.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Recruitment Portal - File Not Found</h1>", 404

@app.route('/hr_employee_onboarding')
def hr_employee_onboarding():
    try:
        with open(os.path.join('static', 'hr_employee_onboarding.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Employee Onboarding - File Not Found</h1>", 404

@app.route('/hr_onboarding')
def hr_onboarding():
    return redirect('/hr_employee_directory')

@app.route('/hr_performance_reviews')
def hr_performance_reviews():
    return redirect('/hr_employee_directory')

@app.route('/hr_benefits_management')
def hr_benefits_management():
    return redirect('/hr_payroll_processing')

@app.route('/hr_time_tracking')
def hr_time_tracking():
    return redirect('/hr_time_off_management')

@app.route('/hr_job_postings')
def hr_job_postings():
    return redirect('/hr_recruitment_portal')

@app.route('/hr_candidate_tracking')
def hr_candidate_tracking():
    return redirect('/hr_recruitment_portal')

@app.route('/hr_interview_management')
def hr_interview_management():
    return redirect('/hr_recruitment_portal')

@app.route('/hr_training_programs')
def hr_training_programs():
    return redirect('/company_training')

@app.route('/hr_certifications')
def hr_certifications():
    return redirect('/company_training')

@app.route('/hr_career_development')
def hr_career_development():
    return redirect('/company_training')

@app.route('/hr_compliance_tracking')
def hr_compliance_tracking():
    return redirect('/hr_employee_directory')

@app.route('/hr_policy_management')
def hr_policy_management():
    return redirect('/hr_employee_directory')

@app.route('/hr_analytics_dashboard')
def hr_analytics_dashboard():
    return redirect('/analytics_dashboard')

@app.route('/hr_workforce_planning')
def hr_workforce_planning():
    return redirect('/hr_employee_directory')

@app.route('/hr_reports_generator')
def hr_reports_generator():
    return redirect('/financial_reports')

@app.route('/employee_portal')
def employee_portal():
    return redirect('/employee_dashboard')

@app.route('/employee_documents')
def employee_documents():
    return redirect('/employee_dashboard')

@app.route('/employee_benefits_portal')
def employee_benefits_portal():
    return redirect('/employee_dashboard')

# Warehouse/Inventory Routes
@app.route('/cycle_counting')
def cycle_counting():
    return send_from_directory('static', 'cycle_counting.html')

@app.route('/inventory_adjustments')
def inventory_adjustments():
    return send_from_directory('static', 'inventory_adjustments.html')

@app.route('/custom_reports')
def custom_reports():
    return send_from_directory('static', 'custom_reports.html')

@app.route('/warehouse_chat')
def warehouse_chat():
    return send_from_directory('static', 'warehouse_chat.html')

@app.route('/qr_camera_scanner')
@app.route('/qr_scanner')
def qr_camera_scanner():
    return send_from_directory('static', 'qr_scanner_test.html')

# Order Picking Routes
@app.route('/order_picking')
def order_picking_page():
    """Order picking department page"""
    return send_from_directory('static', 'order_picking.html')

@app.route('/picking')
def picking_redirect():
    """Redirect /picking to /order_picking"""
    return redirect('/order_picking')

# Reports Routes
@app.route('/reports')
@app.route('/reports_hub')
def reports_page():
    """Reports and analytics hub"""
    return send_from_directory('static', 'reports_hub.html')

# Admin Routes
@app.route('/admin')
@app.route('/admin_hub')
def admin_page():
    """Admin control panel"""
    return send_from_directory('static', 'admin_hub.html')

# Logout Route
@app.route('/logout')
def logout():
    """Logout user and clear session"""
    try:
        # Clear Flask session
        session.clear()
        
        # Clear persistent session if exists
        persistent_token = request.cookies.get('persistent_token')
        if persistent_token and persistent_token in persistent_sessions:
            del persistent_sessions[persistent_token]
            save_data()
        
        logger.info(f"User logged out successfully")
        
        # Create response with cleared cookie
        response = redirect('/company_login')
        response.set_cookie('persistent_token', '', max_age=0)
        return response
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return redirect('/company_login')

# HR Recruitment API Routes
@app.route('/api/hr/recruitment/positions', methods=['GET'])
def get_recruitment_positions():
    """Get all open positions"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        # Mock recruitment positions data
        positions = {
            'warehouse-supervisor': {
                'id': 'warehouse-supervisor',
                'position': 'Warehouse Supervisor',
                'department': 'Warehouse Operations',
                'type': 'Full-time',
                'status': 'Active',
                'applications': 47,
                'in_review': 12,
                'interviews': 3,
                'posted_date': '2025-01-10',
                'salary_range': '$55,000 - $65,000'
            },
            'inventory-specialist': {
                'id': 'inventory-specialist',
                'position': 'Inventory Specialist',
                'department': 'Warehouse Operations',
                'type': 'Full-time',
                'status': 'Active',
                'applications': 23,
                'in_review': 8,
                'interviews': 2,
                'posted_date': '2025-01-08',
                'salary_range': '$40,000 - $48,000'
            }
        }

        return jsonify({
            'success': True,
            'positions': positions
        })

    except Exception as e:
        logger.error(f"Error fetching recruitment positions: {e}")
        return jsonify({'error': 'Failed to fetch positions'}), 500

@app.route('/api/hr/recruitment/candidates/<position_id>', methods=['GET'])
def get_candidates(position_id):
    """Get candidates for a specific position"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        # Mock candidate data
        candidates_data = {
            'warehouse-supervisor': [
                {
                    'id': 1,
                    'name': 'John Smith',
                    'email': 'john.smith@email.com',
                    'phone': '(555) 123-4567',
                    'experience': '8 years warehouse management',
                    'status': 'Interview Scheduled',
                    'rating': 4.5,
                    'applied_date': '2025-01-15',
                    'resume_url': '/mock/resume/john_smith.pdf'
                },
                {
                    'id': 2,
                    'name': 'Sarah Johnson',
                    'email': 'sarah.johnson@email.com',
                    'phone': '(555) 234-5678',
                    'experience': '5 years logistics supervision',
                    'status': 'Under Review',
                    'rating': 4.2,
                    'applied_date': '2025-01-14',
                    'resume_url': '/mock/resume/sarah_johnson.pdf'
                }
            ],
            'inventory-specialist': [
                {
                    'id': 3,
                    'name': 'Lisa Chen',
                    'email': 'lisa.chen@email.com',
                    'phone': '(555) 456-7890',
                    'experience': '3 years inventory management',
                    'status': 'Interview Scheduled',
                    'rating': 4.0,
                    'applied_date': '2025-01-12',
                    'resume_url': '/mock/resume/lisa_chen.pdf'
                }
            ]
        }

        candidates = candidates_data.get(position_id, [])

        return jsonify({
            'success': True,
            'candidates': candidates,
            'position_id': position_id
        })

    except Exception as e:
        logger.error(f"Error fetching candidates: {e}")
        return jsonify({'error': 'Failed to fetch candidates'}), 500

@app.route('/api/hr/recruitment/interviews', methods=['POST'])
def schedule_interview():
    """Schedule an interview"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = ['candidateId', 'interviewDate', 'interviewTime', 'interviewType', 'interviewer']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # In a real app, you would save this to database
        interview_record = {
            'id': str(uuid.uuid4()),
            'candidate_id': data['candidateId'],
            'interview_date': data['interviewDate'],
            'interview_time': data['interviewTime'],
            'interview_type': data['interviewType'],
            'interviewer': data['interviewer'],
            'status': 'Scheduled',
            'created_at': datetime.now().isoformat(),
            'created_by': session_data.get('user_id')
        }

        logger.info(f"Interview scheduled: Candidate {data['candidateId']} on {data['interviewDate']} at {data['interviewTime']}")

        return jsonify({
            'success': True,
            'message': 'Interview scheduled successfully',
            'interview_id': interview_record['id'],
            'interview_record': interview_record
        })

    except Exception as e:
        logger.error(f"Error scheduling interview: {e}")
        return jsonify({'error': 'Failed to schedule interview'}), 500

@app.route('/api/hr/recruitment/positions/<position_id>', methods=['PUT'])
def update_position(position_id):
    """Update position details"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # In a real app, you would update this in database
        logger.info(f"Position updated: {position_id} - {data}")

        return jsonify({
            'success': True,
            'message': 'Position updated successfully',
            'position_id': position_id
        })

    except Exception as e:
        logger.error(f"Error updating position: {e}")
        return jsonify({'error': 'Failed to update position'}), 500

# API Routes
@app.route('/api/auth/company/register', methods=['POST'])
def company_register_api():
    """Company registration endpoint"""
    try:
        data = request.get_json()
        company_name = data.get('company_name')
        email = data.get('email')
        password = data.get('password')
        employer_code = data.get('employer_code')

        if not company_name or not email or not password:
            return jsonify({'error': 'Company name, email and password required'}), 400

        # Check if company email already exists
        for company_id, company_data in companies.items():
            if company_data.get('email') == email:
                return jsonify({'error': 'Company with this email already exists'}), 400

        # Generate employer code if not provided
        if not employer_code:
            employer_code = f"QRL{str(uuid.uuid4())[:8].upper()}"

        # Create new company
        company_id = str(uuid.uuid4())
        companies[company_id] = {
            'id': company_id,
            'name': company_name,
            'email': email,
            'password': password,  # In production, this should be hashed
            'employer_code': employer_code,
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'plan': 'starter'
        }

        # Create default subscription
        subscriptions[company_id] = {
            'company_id': company_id,
            'plan': 'starter',
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }

        save_data()

        logger.info(f"New company registered: {company_name} ({email})")

        return jsonify({
            'success': True,
            'message': 'Company account created successfully',
            'company_id': company_id,
            'employer_code': employer_code
        })

    except Exception as e:
        logger.error(f"Company registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/company/login', methods=['POST'])
def company_login_api():
    """Company login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        terms_accepted = data.get('termsAccepted', False)

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Validate terms acceptance
        if not terms_accepted:
            return jsonify({'error': 'You must accept the Terms of Service and Privacy Policy to continue'}), 400

        # Handle demo login first
        if email == 'qrlegends22@gmail.com' and password == 'demo123':
            user_id = 'demo_user_id'
            employee_id = 'demo_employee_id'
            username = 'QR Legends Demo'
            role = 'admin'
            company_id = 'demo_company_id'

            # Set demo session flag
            session['is_demo'] = True
            session_token = create_persistent_session(user_id, employee_id, username, role, company_id)

            resp = jsonify({
                'success': True,
                'message': 'Demo login successful',
                'persistent_token': session_token,
                'redirect_url': '/main_dashboard',
                'user': {
                    'user_id': user_id,
                    'employee_id': employee_id,
                    'username': username,
                    'role': role,
                    'company_id': company_id,
                    'is_demo': True
                }
            })
            resp.set_cookie('persistent_token', session_token, max_age=30*24*3600, httponly=True, secure=False)
            return resp

        # Check regular company accounts
        for company_id, company_data in companies.items():
            if company_data.get('email') == email and company_data.get('password') == password:
                user_id = company_data.get('id', str(uuid.uuid4()))
                employee_id = user_id
                username = company_data.get('name', email)
                role = 'admin'

                session_token = create_persistent_session(user_id, employee_id, username, role, company_id)

                resp = jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'persistent_token': session_token,
                    'user': {
                        'user_id': user_id,
                        'employee_id': employee_id,
                        'username': username,
                        'role': role,
                        'company_id': company_id
                    }
                })
                resp.set_cookie('persistent_token', session_token, max_age=30*24*3600, httponly=True, secure=False)
                return resp

        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        logger.error(f"Company login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password_api():
    """Handle forgot password request - send reset link to email"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Check if email exists in companies
        user_exists = False
        company_id = None
        for comp_id, company_data in companies.items():
            if company_data.get('email', '').lower() == email:
                user_exists = True
                company_id = comp_id
                break

        # Always return success to prevent email enumeration
        # But only actually create token if user exists
        if user_exists:
            # Generate secure reset token
            reset_token = secrets.token_urlsafe(32)
            expiry_time = datetime.now() + timedelta(hours=1)

            # Store token with expiry
            password_reset_tokens[reset_token] = {
                'email': email,
                'company_id': company_id,
                'expires_at': expiry_time.isoformat(),
                'created_at': datetime.now().isoformat()
            }

            # Clean up expired tokens (simple cleanup)
            current_time = datetime.now()
            expired_tokens = [
                token for token, data in password_reset_tokens.items()
                if datetime.fromisoformat(data['expires_at']) < current_time
            ]
            for token in expired_tokens:
                del password_reset_tokens[token]

            # In a real app, send email here
            # For demo, we'll log the reset link
            reset_link = f"{request.host_url}reset_password?token={reset_token}"
            logger.info(f"Password reset link for {email}: {reset_link}")
            print(f"\n{'='*60}")
            print(f"🔑 PASSWORD RESET LINK")
            print(f"{'='*60}")
            print(f"Email: {email}")
            print(f"Reset Link: {reset_link}")
            print(f"Expires: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")

        # Always return success message (security best practice)
        return jsonify({
            'success': True,
            'message': 'If an account exists with that email, a password reset link has been sent.'
        })

    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        return jsonify({'error': 'Failed to process request'}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password_api():
    """Handle password reset with token"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')

        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400

        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400

        # Validate token
        if token not in password_reset_tokens:
            return jsonify({'error': 'Invalid or expired reset link'}), 400

        token_data = password_reset_tokens[token]
        expiry_time = datetime.fromisoformat(token_data['expires_at'])

        # Check if token has expired
        if datetime.now() > expiry_time:
            del password_reset_tokens[token]
            return jsonify({'error': 'Reset link has expired. Please request a new one.'}), 400

        # Get user details
        email = token_data['email']
        company_id = token_data['company_id']

        # Update password
        if company_id in companies:
            companies[company_id]['password'] = new_password
            save_data()

            # Delete used token
            del password_reset_tokens[token]

            logger.info(f"Password reset successful for {email}")

            return jsonify({
                'success': True,
                'message': 'Password reset successful'
            })
        else:
            return jsonify({'error': 'Account not found'}), 404

    except Exception as e:
        logger.error(f"Reset password error: {e}")
        return jsonify({'error': 'Failed to reset password'}), 500

@app.route('/api/auth/employee/login', methods=['POST'])
@app.route('/api/auth/employee-login', methods=['POST'])
def employee_login_api():
    """Employee login endpoint"""
    try:
        data = request.get_json()
        # Support both email and username
        email_or_username = data.get('email') or data.get('username')
        password = data.get('password')
        terms_accepted = data.get('termsAccepted', False)

        if not email_or_username or not password:
            return jsonify({'error': 'Username/email and password required'}), 400
        
        # Validate terms acceptance
        if not terms_accepted:
            return jsonify({'error': 'You must accept the Terms of Service and Privacy Policy to continue'}), 400

        employee_data = None
        for emp_id, emp in employees.items():
            if emp.get('email') == email_or_username or emp.get('username') == email_or_username:
                employee_data = emp
                break

        if employee_data and employee_data.get('password') == password:
            user_id = employee_data.get('id')
            employee_id = employee_data.get('employee_id')
            username = f"{employee_data.get('first_name', '')} {employee_data.get('last_name', '')}".strip() or email_or_username
            role = employee_data.get('role', 'user')
            company_id = employee_data.get('company_id')

            session_token = create_persistent_session(user_id, employee_id, username, role, company_id)

            # Determine redirect URL based on role
            role_redirect_map = {
                'admin': '/main_dashboard',
                'manager': '/main_dashboard',
                'picker': '/order_picking',
                'lift_driver': '/lift_drivers',
                'receiver': '/receiving',
                'shipper': '/shipping',
                'inventory': '/inventory',
                'quality': '/quality_check',
                'sales': '/salespad_dashboard',
                'accountant': '/accounts_payable'
            }
            redirect_url = role_redirect_map.get(role, '/main_dashboard')

            resp = jsonify({
                'success': True,
                'message': 'Login successful',
                'redirect_url': redirect_url,
                'persistent_token': session_token,
                'user': {
                    'user_id': user_id,
                    'employee_id': employee_id,
                    'username': username,
                    'role': role,
                    'company_id': company_id,
                    'first_name': employee_data.get('first_name', ''),
                    'last_name': employee_data.get('last_name', '')
                }
            })
            resp.set_cookie('persistent_token', session_token, max_age=30*24*3600, httponly=True, secure=False)
            
            # Also set session variables
            session['user_id'] = user_id
            session['employee_id'] = employee_id
            session['username'] = username
            session['role'] = role
            session['company_id'] = company_id
            session['authenticated'] = True
            session.permanent = True
            
            return resp
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        logger.error(f"Employee login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/demo_auto_login')
@app.route('/auto_demo')
@app.route('/quick_demo')
def demo_auto_login():
    """Instant demo login - bypasses all login screens and goes straight to dashboard"""
    try:
        # Set up demo session
        user_id = 'demo_user_id'
        employee_id = 'demo_employee_id'
        username = 'QR Legends Demo'
        role = 'admin'
        company_id = 'demo_company_id'
        
        # Create demo employee record if it doesn't exist
        if employee_id not in employees:
            from datetime import datetime
            employees[employee_id] = {
                'id': employee_id,
                'company_id': company_id,
                'employee_id': 'DEMO001',
                'username': username,
                'email': 'demo@qrlegends.com',
                'first_name': 'Demo',
                'last_name': 'User',
                'phone': '555-0100',
                'address': '123 Demo Street',
                'position': 'System Administrator',
                'department': 'Administration',
                'role': role,
                'employment_type': 'full_time',
                'hire_date': '2024-01-01',
                'salary': 85000,
                'manager_id': '',
                'vacation_days': 15,
                'sick_days': 10,
                'emergency_contact': 'N/A',
                'status': 'active',
                'created_at': datetime.now().isoformat()
            }
            save_data()
        
        # Create session
        session['is_demo'] = True
        session['user_id'] = user_id
        session['employee_id'] = employee_id
        session['username'] = username
        session['role'] = role
        session['company_id'] = company_id
        session['authenticated'] = True
        session.permanent = True
        session.modified = True
        
        # Create persistent session
        session_token = create_persistent_session(user_id, employee_id, username, role, company_id)
        
        logger.info("🚀 Auto demo login successful - redirecting to dashboard")
        
        # Redirect directly to main dashboard
        resp = redirect('/main_dashboard')
        resp.set_cookie('persistent_token', session_token, max_age=30*24*3600, httponly=True, secure=False)
        return resp
        
    except Exception as e:
        logger.error(f"Demo auto login error: {e}")
        return redirect('/company_login')

@app.route('/api/auth/verify-session', methods=['POST'])
def verify_session_api():
    """Verify if session is still valid"""
    try:
        session_data = get_current_session()
        if session_data and session_data.get('authenticated'):
            return jsonify({
                'success': True,
                'user': session_data
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Session expired'
            }), 401
    except Exception as e:
        logger.error(f"Session verification error: {e}")
        return jsonify({
            'success': False,
            'message': 'Session verification failed'
        }), 500

@app.route('/logout')
def logout_page():
    """Logout page redirect"""
    return logout_api()

@app.route('/api/auth/logout', methods=['POST'])
def logout_api():
    """Logout user and clear session"""
    try:
        # Clear persistent token if exists
        persistent_token = session.get('persistent_token')
        if persistent_token and persistent_token in persistent_sessions:
            del persistent_sessions[persistent_token]
            save_data()

        # Clear session
        session.clear()

        resp = make_response(redirect('/company_login'))
        resp.set_cookie('persistent_token', '', expires=0)
        return resp

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return redirect('/company_login')

@app.route('/api/auth/profile')
def get_auth_profile():
    """Get user profile information"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        user_id = session_data.get('user_id')
        employee_id = session_data.get('employee_id')

        # Get employee data for widget access levels
        employee_data = None
        for emp_id, emp in employees.items():
            if emp.get('id') == user_id or emp.get('employee_id') == employee_id:
                employee_data = emp
                break

        widget_access = ['user']  # Default access
        if employee_data:
            widget_access = employee_data.get('widget_access_level', ['user'])

        return jsonify({
            'user_type': 'employee',
            'role': session_data.get('role', 'user'),
            'company_id': session_data.get('company_id'),
            'user_id': user_id,
            'employee_id': employee_id,
            'username': session_data.get('username'),
            'widget_access_levels': widget_access,
            'department': employee_data.get('department') if employee_data else 'Unknown'
        })
    except Exception as e:
        logger.error(f"Error getting auth profile: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/hr/employees', methods=['POST'])
def add_employee_api():
    """Add new employee"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'employeeId', 'position', 'department', 'role', 'tempPassword']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Check if employee ID already exists
        for emp_id, emp_data in employees.items():
            if emp_data.get('employee_id') == data['employeeId']:
                return jsonify({'error': 'Employee ID already exists'}), 400

        # Check if email already exists
        for emp_id, emp_data in employees.items():
            if emp_data.get('email') == data['email']:
                return jsonify({'error': 'Email already exists'}), 400

        # Create new employee
        employee_id = str(uuid.uuid4())
        company_id = session_data.get('company_id')

        employee_record = {
            'id': employee_id,
            'company_id': company_id,
            'employee_id': data['employeeId'],
            'username': f"{data['firstName']}_{data['lastName']}".lower(),
            'password': data['tempPassword'],  # In production, this should be hashed
            'email': data['email'],
            'first_name': data['firstName'],
            'last_name': data['lastName'],
            'phone': data.get('phone', ''),
            'address': data.get('address', ''),
            'position': data['position'],
            'department': data['department'],
            'role': data['role'],
            'employment_type': data.get('employmentType', 'full_time'),
            'hire_date': data.get('hireDate', datetime.now().isoformat()),
            'salary': float(data.get('salary', 0)) if data.get('salary') else 0,
            'manager_id': data.get('manager', ''),
            'vacation_days': int(data.get('vacationDays', 15)),
            'sick_days': int(data.get('sickDays', 10)),
            'emergency_contact': data.get('emergencyContact', ''),
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'password_reset_required': True
        }

        employees[employee_id] = employee_record
        save_data()

        logger.info(f"New employee added: {data['firstName']} {data['lastName']} (ID: {data['employeeId']})")

        return jsonify({
            'success': True,
            'message': 'Employee added successfully',
            'employee_id': employee_id,
            'employee_record': {
                'name': f"{data['firstName']} {data['lastName']}",
                'email': data['email'],
                'employee_id': data['employeeId'],
                'department': data['department'],
                'position': data['position']
            }
        })

    except Exception as e:
        logger.error(f"Error adding employee: {e}")
        return jsonify({'error': 'Failed to add employee'}), 500

@app.route('/api/qr/list', methods=['GET'])
def list_qr_codes():
    """Get all QR codes for the current company"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        company_qrs = []

        # Filter QR codes by company
        for qr_id, qr_data in qr_codes.items():
            if qr_data.get('company_id') == company_id:
                company_qrs.append(qr_data)

        # Sort by creation date (newest first)
        company_qrs.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return jsonify({
            'success': True,
            'qr_codes': company_qrs,
            'total': len(company_qrs)
        })

    except Exception as e:
        logger.error(f"Error listing QR codes: {e}")
        return jsonify({'error': 'Failed to retrieve QR codes'}), 500

@app.route('/api/qr/generate', methods=['POST'])
def generate_qr_api():
    try:
        data = request.get_json()
        qr_data = data.get('qr_data', 'DEFAULT-QR-' + str(int(time.time())))
        qr_type = data.get('type', 'generic')

        # Generate QR code
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
        except Exception as qr_error:
            logger.error(f"QR code generation failed: {qr_error}")
            return jsonify({'success': False, 'error': 'QR code generation failed'}), 500

        # Create QR image
        qr_image = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Store QR code record
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'

        qr_record = {
            'id': str(uuid.uuid4()),
            'qr_data': qr_data,
            'type': qr_type,
            'company_id': company_id,
            'created_at': datetime.now().isoformat(),
            'created_by': session_data.get('user_id', 'system') if session_data else 'system'
        }

        qr_codes[qr_record['id']] = qr_record
        save_data()

        return jsonify({
            'success': True,
            'qr_data': qr_data,
            'qr_image': f'data:image/png;base64,{qr_base64}',
            'type': qr_type,
            'qr_id': qr_record['id']
        })

    except Exception as e:
        logger.error(f"QR Generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/qr/purchase-order', methods=['POST'])
def generate_purchase_order_qr():
    """Generate QR code for Purchase Orders"""
    try:
        data = request.get_json()
        po_number = data.get('po_number', f'PO-{int(time.time())}')
        supplier = data.get('supplier', 'Unknown Supplier')
        priority = data.get('priority', 'Normal')

        # Create PO QR data - Include PO number as ID for lookup
        qr_data = f"PO_RECEIVING:{po_number}"

        # Generate QR code
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
        except Exception as qr_error:
            logger.error(f"QR code generation failed: {qr_error}")
            return jsonify({'success': False, 'error': 'QR code generation failed'}), 500

        qr_image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Store PO QR record
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'

        po_qr_record = {
            'id': str(uuid.uuid4()),
            'po_number': po_number,
            'supplier': supplier,
            'priority': priority,
            'qr_data': qr_data,
            'company_id': company_id,
            'created_at': datetime.now().isoformat(),
            'created_by': session_data.get('user_id', 'system') if session_data else 'system'
        }

        purchase_order_qrs[po_qr_record['id']] = po_qr_record
        save_data()

        print(f"✅ PO QR generated: {po_number}")

        return jsonify({
            'success': True,
            'po_number': po_number,
            'qr_data': qr_data,
            'qr_image': f'data:image/png;base64,{qr_base64}',
            'po_id': po_qr_record['id']
        })

    except Exception as e:
        logger.error(f"PO QR generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/qr/special-purchase-order', methods=['POST'])
def generate_special_purchase_order_qr():
    """Generate QR code for Special Purchase Orders (SPO)"""
    try:
        data = request.get_json()
        spo_number = data.get('spo_number', f'SPO-{int(time.time())}')
        priority = data.get('priority', 'High')

        # Create SPO QR data
        qr_data = f"SPO:{spo_number}:PRIORITY:{priority}:URGENT"

        # Generate QR code
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
        except Exception as qr_error:
            logger.error(f"QR code generation failed: {qr_error}")
            return jsonify({'success': False, 'error': 'QR code generation failed'}), 500

        qr_image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Store SPO QR record
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'

        spo_qr_record = {
            'id': str(uuid.uuid4()),
            'spo_number': spo_number,
            'priority': priority,
            'qr_data': qr_data,
            'company_id': company_id,
            'created_at': datetime.now().isoformat(),
            'created_by': session_data.get('user_id', 'system') if session_data else 'system'
        }

        purchase_order_qrs[spo_qr_record['id']] = spo_qr_record
        save_data()

        print(f"✅ SPO QR generated: {spo_number}")

        return jsonify({
            'success': True,
            'spo_number': spo_number,
            'qr_data': qr_data,
            'qr_image': f'data:image/png;base64,{qr_base64}',
            'spo_id': spo_qr_record['id']
        })

    except Exception as e:
        logger.error(f"SPO QR generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate_qr', methods=['POST', 'GET'])
def generate_qr_endpoint():
    """General QR code generation endpoint"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
        else:
            # Handle GET requests with query parameters
            data = {
                'text': request.args.get('text', 'DEFAULT-QR'),
                'size': request.args.get('size', 200)
            }

        text = data.get('text', 'DEFAULT-QR')
        size = int(data.get('size', 200))

        # Generate QR code
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(text)
            qr.make(fit=True)
        except Exception as qr_error:
            logger.error(f"QR code generation failed: {qr_error}")
            return jsonify({'success': False, 'error': 'QR code generation failed'}), 500

        qr_image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        print(f"✅ QR code generated for: {text}")

        return jsonify({
            'success': True,
            'qr_image': f'data:image/png;base64,{qr_base64}',
            'text': text,
            'size': size
        })

    except Exception as e:
        logger.error(f"QR generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/inventory/items', methods=['GET'])
def get_inventory_items():
    """Get all inventory items for the current company"""
    try:
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'
        
        # Filter inventory items by company
        company_items = {}
        for item_id, item_data in inventory_items.items():
            if item_data.get('company_id') == company_id:
                company_items[item_id] = item_data
        
        # If no items exist, create some demo data
        if not company_items:
            demo_items = {
                'item_001': {
                    'id': 'item_001',
                    'sku': 'ABC123',
                    'name': 'Widget A',
                    'description': 'Premium quality widget',
                    'quantity': 150,
                    'location': 'A1-B2-C3',
                    'company_id': company_id,
                    'category': 'Widgets',
                    'unit_price': 25.99,
                    'reorder_point': 50,
                    'supplier': 'ABC Supplies Inc.',
                    'created_at': datetime.now().isoformat()
                },
                'item_002': {
                    'id': 'item_002',
                    'sku': 'DEF456',
                    'name': 'Widget B',
                    'description': 'Standard widget model',
                    'quantity': 75,
                    'location': 'A2-B1-C5',
                    'company_id': company_id,
                    'category': 'Widgets',
                    'unit_price': 18.50,
                    'reorder_point': 25,
                    'supplier': 'XYZ Manufacturing',
                    'created_at': datetime.now().isoformat()
                },
                'item_003': {
                    'id': 'item_003',
                    'sku': 'GHI789',
                    'name': 'Widget C',
                    'description': 'Compact widget design',
                    'quantity': 230,
                    'location': 'B1-A3-C2',
                    'company_id': company_id,
                    'category': 'Widgets',
                    'unit_price': 12.75,
                    'reorder_point': 100,
                    'supplier': 'TechCorp Ltd.',
                    'created_at': datetime.now().isoformat()
                }
            }
            
            # Add demo items to inventory
            inventory_items.update(demo_items)
            save_data()
            company_items = demo_items
            
        print(f"✅ Inventory items retrieved for company: {company_id} ({len(company_items)} items)")
        
        return jsonify({
            'success': True,
            'items': company_items,
            'count': len(company_items)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving inventory items: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==== LIFT DRIVER MANAGEMENT ENDPOINTS ====

@app.route('/api/lift-drivers/assignments', methods=['GET'])
def get_lift_driver_assignments():
    """Get all lift driver assignments"""
    try:
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'
        
        # Create demo assignments if none exist
        if 'lift_driver_assignments' not in globals():
            global lift_driver_assignments
            lift_driver_assignments = {}
        
        company_assignments = [a for a in lift_driver_assignments.values() if a.get('company_id') == company_id]
        
        # Create demo data if empty
        if not company_assignments:
            demo_assignments = [
                {'id': 'lda_001', 'driver_name': 'John Smith', 'assigned_aisles': ['A1', 'A2', 'A3'], 'status': 'active', 'company_id': company_id},
                {'id': 'lda_002', 'driver_name': 'Maria Garcia', 'assigned_aisles': ['B1', 'B2', 'B3'], 'status': 'active', 'company_id': company_id},
                {'id': 'lda_003', 'driver_name': 'David Chen', 'assigned_aisles': ['C1', 'C2', 'C3'], 'status': 'active', 'company_id': company_id}
            ]
            for assignment in demo_assignments:
                lift_driver_assignments[assignment['id']] = assignment
            company_assignments = demo_assignments
        
        return jsonify({'success': True, 'assignments': company_assignments})
    except Exception as e:
        logger.error(f"Error getting lift driver assignments: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lift-drivers/assignments', methods=['POST'])
def create_lift_driver_assignment():
    """Create or update lift driver assignment"""
    try:
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'
        
        data = request.get_json()
        assignment_id = data.get('id', f'lda_{str(uuid.uuid4())[:8]}')
        
        assignment = {
            'id': assignment_id,
            'driver_name': data.get('driver_name'),
            'assigned_aisles': data.get('assigned_aisles', []),
            'status': data.get('status', 'active'),
            'company_id': company_id,
            'updated_at': datetime.now().isoformat()
        }
        
        if 'lift_driver_assignments' not in globals():
            global lift_driver_assignments
            lift_driver_assignments = {}
        
        lift_driver_assignments[assignment_id] = assignment
        
        return jsonify({'success': True, 'assignment': assignment})
    except Exception as e:
        logger.error(f"Error creating lift driver assignment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lift-drivers/tasks', methods=['GET'])
def get_lift_driver_tasks():
    """Get all pending lift driver tasks"""
    try:
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'
        driver_id = request.args.get('driver_id')
        
        if 'lift_driver_tasks' not in globals():
            global lift_driver_tasks
            lift_driver_tasks = {}
        
        # Filter tasks
        company_tasks = [t for t in lift_driver_tasks.values() if t.get('company_id') == company_id]
        if driver_id:
            company_tasks = [t for t in company_tasks if t.get('assigned_driver_id') == driver_id]
        
        # Sort by priority
        company_tasks.sort(key=lambda x: (x.get('priority', 5), x.get('created_at', '')))
        
        return jsonify({'success': True, 'tasks': company_tasks})
    except Exception as e:
        logger.error(f"Error getting lift driver tasks: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lift-drivers/tasks', methods=['POST'])
def create_lift_driver_task():
    """Create a new lift driver task (replenishment or pull-down request)"""
    try:
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'
        user_id = session_data.get('user_id', 'system') if session_data else 'system'
        
        data = request.get_json()
        
        # Determine closest driver based on aisle
        location = data.get('location', '')
        aisle = location.split('-')[0] if location else 'A1'
        
        # Find closest driver
        if 'lift_driver_assignments' not in globals():
            global lift_driver_assignments
            lift_driver_assignments = {}
        
        closest_driver = None
        for assignment in lift_driver_assignments.values():
            if assignment.get('company_id') == company_id and assignment.get('status') == 'active':
                if aisle in assignment.get('assigned_aisles', []):
                    closest_driver = assignment
                    break
        
        # If no exact match, use first available driver
        if not closest_driver:
            for assignment in lift_driver_assignments.values():
                if assignment.get('company_id') == company_id and assignment.get('status') == 'active':
                    closest_driver = assignment
                    break
        
        task_id = f'task_{str(uuid.uuid4())[:12]}'
        task = {
            'id': task_id,
            'type': data.get('type', 'pull_down'),  # pull_down or replenishment
            'item_name': data.get('item_name'),
            'location': location,
            'requested_by': user_id,
            'assigned_driver_id': closest_driver.get('id') if closest_driver else None,
            'assigned_driver_name': closest_driver.get('driver_name') if closest_driver else 'Unassigned',
            'priority': data.get('priority', 1),  # 1 = highest
            'status': 'pending',
            'company_id': company_id,
            'created_at': datetime.now().isoformat(),
            'notes': data.get('notes', '')
        }
        
        if 'lift_driver_tasks' not in globals():
            global lift_driver_tasks
            lift_driver_tasks = {}
        
        lift_driver_tasks[task_id] = task
        
        print(f"✅ Lift driver task created: {task_id} assigned to {task.get('assigned_driver_name')}")
        
        return jsonify({'success': True, 'task': task})
    except Exception as e:
        logger.error(f"Error creating lift driver task: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lift-drivers/tasks/<task_id>/complete', methods=['POST'])
def complete_lift_driver_task(task_id):
    """Mark a lift driver task as complete"""
    try:
        if 'lift_driver_tasks' not in globals():
            global lift_driver_tasks
            lift_driver_tasks = {}
        
        if task_id in lift_driver_tasks:
            lift_driver_tasks[task_id]['status'] = 'completed'
            lift_driver_tasks[task_id]['completed_at'] = datetime.now().isoformat()
            return jsonify({'success': True, 'task': lift_driver_tasks[task_id]})
        else:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
    except Exception as e:
        logger.error(f"Error completing lift driver task: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==== END LIFT DRIVER MANAGEMENT ====

@app.route('/api/qr/transfer-purchase-order', methods=['POST'])
def generate_transfer_purchase_order_qr():
    """Generate QR code for Transfer Purchase Orders"""
    try:
        data = request.get_json()
        transfer_number = data.get('transfer_number', f'XFR-{int(time.time())}')
        transfer_type = data.get('transfer_type', 'Standard Transfer')

        # Create Transfer QR data
        qr_data = f"TRANSFER:{transfer_number}:TYPE:{transfer_type}"

        # Generate QR code
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
        except Exception as qr_error:
            logger.error(f"QR code generation failed: {qr_error}")
            return jsonify({'success': False, 'error': 'QR code generation failed'}), 500

        qr_image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Store Transfer QR record
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'

        transfer_qr_record = {
            'id': str(uuid.uuid4()),
            'transfer_number': transfer_number,
            'transfer_type': transfer_type,
            'qr_data': qr_data,
            'company_id': company_id,
            'created_at': datetime.now().isoformat(),
            'created_by': session_data.get('user_id', 'system') if session_data else 'system'
        }

        purchase_order_qrs[transfer_qr_record['id']] = transfer_qr_record
        save_data()

        print(f"✅ Transfer QR generated: {transfer_number}")

        return jsonify({
            'success': True,
            'transfer_number': transfer_number,
            'qr_data': qr_data,
            'qr_image': f'data:image/png;base64,{qr_base64}',
            'transfer_id': transfer_qr_record['id']
        })

    except Exception as e:
        logger.error(f"Transfer QR generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# User Information API
@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    """Get current user's role and department information for widget access control"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            # Return default/guest access if not authenticated
            return jsonify({
                'role': 'worker',
                'department': 'warehouse',
                'username': 'guest',
                'authenticated': False
            })
        
        # Get employee data for more complete information
        employee_id = session_data.get('employee_id')
        user_role = session_data.get('role', 'worker')
        
        # Try to get department from employee record
        user_department = 'warehouse'  # default
        if employee_id and employee_id in employees:
            employee = employees[employee_id]
            user_department = employee.get('department', 'warehouse')
        
        return jsonify({
            'success': True,
            'role': user_role,
            'department': user_department,
            'username': session_data.get('username', 'unknown'),
            'employee_id': employee_id,
            'authenticated': True
        })
        
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        return jsonify({
            'success': False,
            'role': 'worker',
            'department': 'warehouse',
            'error': str(e)
        }), 200  # Still return 200 with default values

WAREHOUSE_OS_ROLES = {
    'platform_owner': ['*'],
    'admin': ['*'],
    'manager': ['control_center', 'receiving', 'putaway', 'inventory', 'replenishment',
                'picking', 'shipping', 'labor', 'safety', 'reports', 'administration'],
    'supervisor': ['control_center', 'receiving', 'putaway', 'inventory', 'replenishment',
                   'picking', 'shipping', 'labor', 'safety', 'reports'],
    'inventory_control_lead': ['control_center', 'inventory', 'replenishment', 'reports'],
    'receiving_lead': ['control_center', 'receiving', 'putaway', 'labor', 'reports'],
    'lift_driver': ['putaway', 'replenishment', 'safety'],
    'cycle_counter': ['inventory', 'safety'],
    'picker': ['picking', 'safety'],
    'order_picker': ['picking', 'safety'],
    'receiver': ['receiving', 'safety'],
    'shipper': ['shipping', 'safety'],
    'shipping_clerk': ['shipping', 'reports'],
    'auditor': ['control_center', 'inventory', 'safety', 'reports'],
    'read_only_auditor': ['control_center', 'inventory', 'safety', 'reports'],
}


def _company_records(records, company_id, allow_demo_fallback=False):
    """Return records for a company while preserving useful demo snapshots."""
    values = list(records.values()) if isinstance(records, dict) else list(records or [])
    filtered = [item for item in values if item.get('company_id') == company_id]
    if filtered or not allow_demo_fallback:
        return filtered
    return values


def _safe_metric(value, default):
    try:
        return round(float(value), 1)
    except (TypeError, ValueError):
        return default


@app.route('/api/warehouse-os/control-center', methods=['GET'])
def warehouse_os_control_center():
    """Return an operational snapshot backed by existing QR Legends stores."""
    session_data = get_current_session()
    if not session_data or not session_data.get('authenticated'):
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    company_id = session_data.get('company_id')
    is_demo = bool(session_data.get('is_demo')) or company_id == 'demo_company'
    inventory = _company_records(inventory_items, company_id, is_demo)
    orders = _company_records(purchase_orders, company_id, is_demo)
    activities = _company_records(warehouse_activity_history, company_id, is_demo)
    active_containers = _company_records(containers, company_id, is_demo)
    tasks = _company_records(lift_driver_tasks, company_id, is_demo)

    metric_source = load_json_data(os.path.join(DATA_DIR, 'performance_metrics.json'))
    metric = metric_source.get(company_id, {}) if isinstance(metric_source, dict) else {}
    if not metric and isinstance(metric_source, dict) and metric_source:
        metric = next(iter(metric_source.values()))

    on_hand = sum(max(0, item.get('quantity', 0) or 0) for item in inventory)
    negative = [item for item in inventory if (item.get('quantity', 0) or 0) < 0]
    empty_faces = [
        item for item in inventory
        if (item.get('quantity', 0) or 0) == 0 and item.get('location')
    ]
    holds = [
        item for item in inventory
        if item.get('status') in ('quality_hold', 'blocked', 'damaged', 'quarantine')
    ]
    open_orders = [
        order for order in orders
        if order.get('status', 'open') not in ('received', 'complete', 'closed', 'cancelled')
    ]
    open_replenishments = [
        task for task in tasks
        if task.get('type') in ('replenishment', 'pull_down')
        and task.get('status', 'open') not in ('complete', 'completed', 'cancelled')
    ]
    active_trucks = [
        container for container in active_containers
        if container.get('status', 'active') not in ('complete', 'completed', 'closed')
    ]
    cycle_counts = [
        activity for activity in activities
        if activity.get('action_type') == 'cycle_count'
        and activity.get('status', 'open') not in ('complete', 'completed', 'approved')
    ]
    variances = [
        activity for activity in activities
        if activity.get('variance_amount') not in (None, 0, 0.0, '0')
    ]

    accuracy = _safe_metric(metric.get('accuracy_rate'), 99.2)
    fill_rate = _safe_metric(metric.get('order_fill_rate'), 98.7)
    dock_to_stock = _safe_metric(metric.get('cycle_time_minutes'), 42.0)
    damage_rate = _safe_metric(metric.get('damage_rate'), 0.3)
    receiving_accuracy = max(0, round(100 - damage_rate, 1))

    exceptions = []
    for item in holds[:3]:
        exceptions.append({
            'severity': item.get('severity', 'high'),
            'type': 'Inventory hold',
            'title': item.get('name') or item.get('item_number') or 'Held inventory',
            'detail': item.get('hold_reason') or item.get('status', '').replace('_', ' ').title(),
            'location': item.get('location', 'Unassigned'),
            'href': '/inventory'
        })
    for item in negative[:2]:
        exceptions.append({
            'severity': 'critical',
            'type': 'Negative inventory',
            'title': item.get('name') or item.get('item_number') or 'Inventory variance',
            'detail': f"On hand: {item.get('quantity', 0)}",
            'location': item.get('location', 'Unassigned'),
            'href': '/inventory_adjustments'
        })
    if not exceptions:
        exceptions = [
            {'severity': 'critical', 'type': 'Replenishment', 'title': 'Pick face below minimum',
             'detail': 'Reserve stock is available; release before next wave.', 'location': 'A-03-01',
             'href': '/replenishment'},
            {'severity': 'high', 'type': 'Receiving', 'title': 'Receipt approaching SLA',
             'detail': 'Container timer has 18 minutes remaining.', 'location': 'Door 06',
             'href': '/receiving'},
            {'severity': 'medium', 'type': 'Inventory', 'title': 'Cycle count review',
             'detail': 'Supervisor approval required for a unit variance.', 'location': 'C-12-04',
             'href': '/cycle_counting'}
        ]

    late_tasks = [
        {
            'priority': task.get('priority', 'high'),
            'task': task.get('description') or task.get('type', 'Warehouse task').replace('_', ' ').title(),
            'owner': task.get('assigned_to') or task.get('worker_name') or 'Unassigned',
            'age': task.get('age') or 'Needs attention',
            'href': '/replenishment' if task.get('type') == 'replenishment' else '/lift_drivers'
        }
        for task in tasks
        if task.get('status', 'open') not in ('complete', 'completed', 'cancelled')
    ][:5]
    if not late_tasks:
        late_tasks = [
            {'priority': 'critical', 'task': 'Release critical replenishment', 'owner': 'Lift team',
             'age': '31 min open', 'href': '/replenishment'},
            {'priority': 'high', 'task': 'Resolve receiving OSD', 'owner': 'Receiving lead',
             'age': '24 min open', 'href': '/receiving'},
            {'priority': 'normal', 'task': 'Approve cycle count variance', 'owner': 'IC supervisor',
             'age': '18 min open', 'href': '/cycle_counting'}
        ]

    return jsonify({
        'success': True,
        'generated_at': datetime.now().isoformat(),
        'warehouse': 'DC Legends Distribution Center',
        'shift': 'Day shift',
        'user': {
            'name': session_data.get('username', 'Warehouse User'),
            'role': session_data.get('role', 'worker'),
            'permissions': WAREHOUSE_OS_ROLES.get(session_data.get('role', 'worker'), ['control_center'])
        },
        'kpis': [
            {'label': 'Receiving Accuracy', 'value': receiving_accuracy, 'unit': '%', 'target': '99.0%', 'tone': 'good'},
            {'label': 'Putaway Accuracy', 'value': accuracy, 'unit': '%', 'target': '99.5%', 'tone': 'good'},
            {'label': 'Inventory Accuracy', 'value': accuracy, 'unit': '%', 'target': '99.0%', 'tone': 'good'},
            {'label': 'Pick Accuracy', 'value': round(min(99.9, accuracy + 0.4), 1), 'unit': '%', 'target': '99.7%', 'tone': 'good'},
            {'label': 'On-Time Shipments', 'value': fill_rate, 'unit': '%', 'target': '98.0%', 'tone': 'good'},
            {'label': 'Dock-to-Stock', 'value': dock_to_stock, 'unit': ' min', 'target': '< 45 min',
             'tone': 'watch' if dock_to_stock > 45 else 'good'}
        ],
        'workload': [
            {'label': 'Active Trucks', 'value': len(active_trucks) or 4, 'href': '/receiving', 'tone': 'blue'},
            {'label': 'Open Variances', 'value': len(variances) or len(holds), 'href': '/inventory_adjustments', 'tone': 'red'},
            {'label': 'Open Replenishments', 'value': len(open_replenishments) or 7, 'href': '/replenishment', 'tone': 'amber'},
            {'label': 'Active Cycle Counts', 'value': len(cycle_counts) or 12, 'href': '/cycle_counting', 'tone': 'violet'}
        ],
        'inventory_summary': {
            'sku_count': len(inventory),
            'units_on_hand': on_hand,
            'negative_inventory': len(negative),
            'empty_pick_faces': len(empty_faces),
            'quality_holds': len(holds)
        },
        'open_receipts': len(open_orders),
        'exceptions': exceptions[:5],
        'late_tasks': late_tasks,
        'ai_readiness': [
            {'name': 'AI Slotting Engine', 'status': 'Foundation ready'},
            {'name': 'Demand Forecasting', 'status': 'Data connector planned'},
            {'name': 'Inventory Risk Alerts', 'status': 'Rule-based preview'},
            {'name': 'Labor Forecasting', 'status': 'Placeholder'}
        ]
    })

# Employee Dashboard Data API
@app.route('/api/employee/dashboard', methods=['GET'])
def get_employee_dashboard():
    """Get personalized dashboard data based on employee role"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        employee_id = session_data.get('employee_id')
        user_role = session_data.get('role', 'worker')
        
        if not employee_id or employee_id not in employees:
            return jsonify({'success': False, 'error': 'Employee not found'}), 404
        
        employee = employees[employee_id]
        
        # Calculate hours worked this week/month
        from datetime import datetime, timedelta
        today = datetime.now()
        week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        month_start = today.strftime('%Y-%m-01')
        
        # Load time attendance data
        time_data_file = os.path.join('data', 'hr_payroll', 'time_attendance.json')
        time_attendance = {}
        if os.path.exists(time_data_file):
            with open(time_data_file, 'r') as f:
                time_attendance = json.load(f)
        
        employee_time = time_attendance.get(employee_id, [])
        hours_this_week = sum(entry.get('hours_worked', 0) for entry in employee_time 
                              if entry.get('date', '') >= week_start)
        hours_this_month = sum(entry.get('hours_worked', 0) for entry in employee_time 
                               if entry.get('date', '') >= month_start)
        
        # Load payroll records
        payroll_file = os.path.join('data', 'hr_payroll', 'payroll_records.json')
        payroll_records = {}
        if os.path.exists(payroll_file):
            with open(payroll_file, 'r') as f:
                payroll_records = json.load(f)
        
        recent_paychecks = payroll_records.get(employee_id, [])[-3:] if employee_id in payroll_records else []
        
        # Build dashboard data based on role
        dashboard_data = {
            'success': True,
            'employee': {
                'name': f"{employee.get('first_name', '')} {employee.get('last_name', '')}",
                'employee_id': employee.get('employee_id', ''),
                'position': employee.get('position', ''),
                'department': employee.get('department', ''),
                'hire_date': employee.get('hire_date', ''),
                'email': employee.get('email', '')
            },
            'time': {
                'hours_this_week': round(hours_this_week, 2),
                'hours_this_month': round(hours_this_month, 2),
                'last_clock_in': employee_time[-1].get('date', 'N/A') if employee_time else 'N/A'
            },
            'pto': {
                'vacation_days': employee.get('vacation_days', 0),
                'sick_days': employee.get('sick_days', 0),
                'total_pto': employee.get('vacation_days', 0) + employee.get('sick_days', 0)
            },
            'payroll': {
                'salary': employee.get('salary', 0),
                'recent_paychecks': recent_paychecks
            },
            'role': user_role
        }
        
        # Add role-specific data
        if user_role == 'admin':
            # Admin sees company-wide metrics
            dashboard_data['admin_metrics'] = {
                'total_employees': len(employees),
                'active_deliveries': len([d for d in deliveries.values() if d.get('status') not in ['completed', 'delivered']]),
                'inventory_value': sum(item.get('quantity', 0) * item.get('unit_cost', 0) 
                                      for item in inventory_items.values())
            }
        elif user_role == 'manager':
            # Manager sees team metrics
            team_members = [emp for emp in employees.values() 
                           if emp.get('manager_id') == employee_id]
            dashboard_data['manager_metrics'] = {
                'team_size': len(team_members),
                'team_members': [{'name': f"{e.get('first_name')} {e.get('last_name')}", 
                                 'position': e.get('position')} for e in team_members],
                'pending_approvals': 0  # Placeholder
            }
        elif user_role in ['picker', 'worker']:
            # Worker/Picker sees their task queue
            my_deliveries = [d for d in deliveries.values() 
                            if d.get('assigned_to') == employee_id and d.get('status') not in ['completed', 'delivered']]
            dashboard_data['worker_metrics'] = {
                'pending_tasks': len(my_deliveries),
                'completed_today': 0  # Placeholder
            }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        logger.error(f"Error getting employee dashboard: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# User Tab Preferences API
@app.route('/api/user/tabs', methods=['GET'])
def get_user_tabs():
    """Get user's saved tabs configuration"""
    try:
        session_data = get_current_session()
        user_id = session_data.get('user_id', 'guest') if session_data else 'guest'
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'
        
        # Initialize user_tabs storage if needed
        if 'user_tabs' not in globals():
            global user_tabs
            user_tabs = {}
        
        # Get user's tabs or return defaults
        user_key = f"{company_id}_{user_id}"
        if user_key in user_tabs:
            return jsonify({
                'success': True,
                'tabs': user_tabs[user_key]['tabs'],
                'homepage': user_tabs[user_key].get('homepage', 'dashboard')
            })
        
        # Return default tabs with hierarchical structure
        default_tabs = [
            {
                'id': 'dashboard',
                'label': 'Dashboard',
                'icon': '🏠',
                'order': 0,
                'is_homepage': True,
                'type': 'main',
                'route': '/main_dashboard'
            },
            {
                'id': 'warehouse',
                'label': 'Warehouse',
                'icon': '🏭',
                'order': 1,
                'type': 'main',
                'expanded': True,
                'children': [
                    {'id': 'receiving', 'label': 'Receiving', 'icon': '📦', 'route': '/receiving'},
                    {'id': 'putaway', 'label': 'Put Away', 'icon': '📥', 'route': '/putaway'},
                    {'id': 'picking', 'label': 'Picking', 'icon': '🎯', 'route': '/order_picking'},
                    {'id': 'packing', 'label': 'Packing', 'icon': '📦', 'route': '/packing'},
                    {'id': 'shipping', 'label': 'Shipping', 'icon': '🚚', 'route': '/shipping'},
                    {'id': 'transfers', 'label': 'Transfers', 'icon': '🔄', 'route': '/transfers'}
                ]
            },
            {
                'id': 'inventory',
                'label': 'Inventory',
                'icon': '📊',
                'order': 2,
                'type': 'main',
                'expanded': False,
                'children': [
                    {'id': 'inventory_view', 'label': 'View Inventory', 'icon': '📋', 'route': '/inventory'},
                    {'id': 'inventory_analysis', 'label': 'Analysis', 'icon': '📈', 'route': '/inventory_analysis'},
                    {'id': 'cycle_counts', 'label': 'Cycle Counts', 'icon': '🔢', 'route': '/cycle_counts'}
                ]
            },
            {
                'id': 'reports',
                'label': 'Reports',
                'icon': '📈',
                'order': 3,
                'type': 'main',
                'route': '/reports',
                'children': [
                    {'id': 'custom_reports', 'label': 'Custom Reports', 'icon': '📊', 'route': '/custom_reports'},
                    {'id': 'analytics', 'label': 'Analytics', 'icon': '📉', 'route': '/analytics_dashboard'}
                ]
            },
            {
                'id': 'admin',
                'label': 'Admin',
                'icon': '⚙️',
                'order': 4,
                'type': 'main',
                'route': '/admin',
                'children': [
                    {'id': 'users', 'label': 'Users', 'icon': '👥', 'route': '/user_management'},
                    {'id': 'settings', 'label': 'Settings', 'icon': '🔧', 'route': '/settings'}
                ]
            }
        ]
        
        return jsonify({
            'success': True,
            'tabs': default_tabs,
            'homepage': 'dashboard'
        })
        
    except Exception as e:
        logger.error(f"Error getting user tabs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user/tabs', methods=['PATCH'])
def update_user_tabs():
    """Update user's tabs configuration"""
    try:
        session_data = get_current_session()
        user_id = session_data.get('user_id', 'guest') if session_data else 'guest'
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'
        
        data = request.get_json()
        
        # Initialize user_tabs storage if needed
        if 'user_tabs' not in globals():
            global user_tabs
            user_tabs = {}
        
        user_key = f"{company_id}_{user_id}"
        user_tabs[user_key] = {
            'tabs': data.get('tabs', []),
            'homepage': data.get('homepage', 'dashboard'),
            'updated_at': datetime.now().isoformat()
        }
        
        save_data()
        
        return jsonify({
            'success': True,
            'tabs': user_tabs[user_key]['tabs'],
            'homepage': user_tabs[user_key]['homepage']
        })
        
    except Exception as e:
        logger.error(f"Error updating user tabs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Warehouse User Tracking and Safety APIs
@app.route('/api/warehouse/user-location', methods=['POST'])
def update_user_location():
    """Update user's current warehouse location"""
    try:
        data = request.get_json()
        user_id = session.get('user_id', 'demo_user_id')
        company_id = session.get('company_id', 'demo')

        # Update user location in tracking system
        location_data = {
            'user_id': user_id,
            'company_id': company_id,
            'zone': data.get('zone'),
            'x': data.get('x', 0),
            'y': data.get('y', 0),
            'timestamp': datetime.now().isoformat(),
            'activity': data.get('activity', 'moving')
        }

        # Store in user activity
        if user_id not in user_activity:
            user_activity[user_id] = []

        user_activity[user_id].append(location_data)

        # Keep only last 100 locations per user
        if len(user_activity[user_id]) > 100:
            user_activity[user_id] = user_activity[user_id][-100:]

        # save_all_data() # This function does not exist, using save_data()
        save_data()
        # log_request(f"Location updated for user {user_id} in zone {data.get('zone')}") # This function does not exist

        return jsonify({'success': True, 'location': location_data})

    except Exception as e:
        logger.error(f"Error updating user location: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/warehouse/nearby-users', methods=['GET'])
def get_nearby_users():
    """Get nearby users for safety warnings"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        current_user_id = session_data.get('user_id')

        # Get all active users in the company
        nearby_users = []
        current_time = datetime.now()

        # Check if user_activity is a list or dict and handle accordingly
        if isinstance(user_activity, list):
            # If it's a list, iterate through items
            for record in user_activity:
                if not isinstance(record, dict):
                    continue

                user_id = record.get('user_id')
                if user_id == current_user_id:
                    continue

                # Check if location is recent (within last 5 minutes)
                timestamp = record.get('timestamp')
                if timestamp:
                    try:
                        update_time = datetime.fromisoformat(timestamp)
                        if (current_time - update_time).total_seconds() > 300:  # 5 minutes
                            continue
                    except:
                        continue

                nearby_users.append({
                    'id': user_id,
                    'name': record.get('username', 'Unknown User'),
                    'role': record.get('role', 'worker'),
                    'location': record.get('location', {}),
                    'status': record.get('status', 'active'),
                    'last_seen': record.get('timestamp', 0)
                })
        elif isinstance(user_activity, dict):
            # If it's a dict, check for company-specific data
            company_activity = user_activity.get(company_id, [])
            if isinstance(company_activity, list):
                for record in company_activity:
                    if not isinstance(record, dict):
                        continue

                    user_id = record.get('user_id')
                    if user_id == current_user_id:
                        continue

                    # Check if location is recent (within last 5 minutes)
                    timestamp = record.get('timestamp')
                    if timestamp:
                        try:
                            update_time = datetime.fromisoformat(timestamp)
                            if (current_time - update_time).total_seconds() > 300:  # 5 minutes
                                continue
                        except:
                            continue

                    nearby_users.append({
                        'id': user_id,
                        'name': record.get('username', 'Unknown User'),
                        'role': record.get('role', 'worker'),
                        'location': record.get('location', {}),
                        'status': record.get('status', 'active'),
                        'last_seen': record.get('timestamp', 0)
                    })

        return jsonify({
            'success': True,
            'users': nearby_users,
            'total_users': len(nearby_users),
            'current_time': current_time.isoformat()
        })

    except Exception as e:
        logger.error(f"Error fetching nearby users: {e}")
        return jsonify({'error': 'Failed to fetch nearby users'}), 500

@app.route('/api/warehouse/navigation/start', methods=['POST'])
def start_warehouse_navigation():
    """Start navigation with enhanced safety tracking"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        destination = data.get('destination')
        start_location = data.get('start_location')

        if not destination:
            return jsonify({'error': 'Destination required'}), 400

        # Log navigation start
        navigation_record = {
            'user_id': session_data.get('user_id'),
            'company_id': session_data.get('company_id'),
            'start_location': start_location,
            'destination': destination,
            'started_at': datetime.now().isoformat(),
            'status': 'active',
            'navigation_id': str(uuid.uuid4())
        }

        logger.info(f"Navigation started: {session_data.get('username')} → {destination}")

        return jsonify({
            'success': True,
            'navigation_id': navigation_record['navigation_id'],
            'message': f'Navigation started to {destination}',
            'safety_mode': 'enhanced',
            'warning_distance': 15,
            'update_frequency': 1000
        })

    except Exception as e:
        logger.error(f"Error starting navigation: {e}")
        return jsonify({'error': 'Failed to start navigation'}), 500

@app.route('/api/warehouse/navigation/stop', methods=['POST'])
def stop_warehouse_navigation():
    """Stop navigation and return to normal safety mode"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        logger.info(f"Navigation stopped: {session_data.get('username')}")

        return jsonify({
            'success': True,
            'message': 'Navigation stopped',
            'safety_mode': 'normal',
            'warning_distance': 10,
            'update_frequency': 2000
        })

    except Exception as e:
        logger.error(f"Error stopping navigation: {e}")
        return jsonify({'error': 'Failed to stop navigation'}), 500

@app.route('/api/qr/receiving', methods=['POST'])
def generate_receiving_qr():
    """Generate QR codes for receiving operations"""
    try:
        data = request.get_json()
        qr_type = data.get('type', 'item')  # 'item' or 'po'

        if qr_type == 'po':
            po_number = data.get('po_number', f'PO-{int(time.time())}')
            qr_data = f"RECEIVING:PO:{po_number}"
        else:
            item_id = data.get('item_id', f'ITEM-{int(time.time())}')
            qr_data = f"RECEIVING:ITEM:{item_id}"

        # Generate QR code
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
        except Exception as qr_error:
            logger.error(f"QR code generation failed: {qr_error}")
            return jsonify({'success': False, 'error': 'QR code generation failed'}), 500

        qr_image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        print(f"✅ Receiving QR generated: {qr_data}")

        return jsonify({
            'success': True,
            'qr_data': qr_data,
            'qr_image': f'data:image/png;base64,{qr_base64}',
            'type': qr_type
        })

    except Exception as e:
        logger.error(f"Receiving QR generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/containers/create', methods=['POST'])
def create_container():
    try:
        data = request.get_json()
        container_id = data.get('container_id', f'CNT-{int(time.time())}')
        container_type = data.get('type', 'Standard Container')
        department = data.get('department', 'Putaway Team')
        location = data.get('location', 'STAGING-AREA')

        # Get current user session
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'

        # Create container record for database
        new_container = {
            'id': str(uuid.uuid4()),
            'container_id': container_id,
            'type': container_type,
            'department': department,
            'location': location,
            'status': 'active',
            'company_id': company_id,
            'created_at': datetime.now().isoformat(),
            'created_by': session_data.get('user_id', 'system') if session_data else 'system',
            'items': []
        }

        # Save to containers database
        containers[new_container['id']] = new_container

        # Generate QR code data
        qr_data = f"CONTAINER:{container_id}:{container_type}:{location}"

        # Generate QR code image
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
        except Exception as qr_error:
            logger.error(f"QR code generation failed: {qr_error}")
            return jsonify({'success': False, 'error': 'QR code generation failed'}), 500

        qr_image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Store QR code record
        qr_record = {
            'id': str(uuid.uuid4()),
            'qr_data': qr_data,
            'type': 'container',
            'container_id': container_id,
            'company_id': company_id,
            'created_at': datetime.now().isoformat(),
            'created_by': session_data.get('user_id', 'system') if session_data else 'system'
        }

        qr_codes[qr_record['id']] = qr_record

        # Save all data
        save_data()

        print(f"✅ Container created: {container_id}")

        return jsonify({
            'success': True,
            'message': f'Container Created Successfully!\nID: {container_id}\nType: {container_type}\nDepartment: {department}',
            'container_id': container_id,
            'container': new_container,
            'qr_data': qr_data,
            'qr_image': f'data:image/png;base64,{qr_base64}',
            'qr_id': qr_record['id']
        })

    except Exception as e:
        logger.error(f"Container creation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/containers/generate-qr', methods=['POST'])
def generate_container_qr():
    """Generate QR code for containers"""
    try:
        data = request.get_json()
        container_id = data.get('container_id', f'CNT-{int(time.time())}')
        container_type = data.get('container_type', 'standard')
        location = data.get('location', 'WAREHOUSE')

        # Get current user session
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'

        # Create QR data
        qr_data = f"CONTAINER:{container_id}:{container_type}:{location}"

        # Generate QR code
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
        except Exception as qr_error:
            logger.error(f"QR code generation failed: {qr_error}")
            return jsonify({'success': False, 'error': 'QR code generation failed'}), 500

        qr_image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Store QR code record
        qr_record = {
            'id': str(uuid.uuid4()),
            'qr_data': qr_data,
            'type': 'container',
            'container_id': container_id,
            'company_id': company_id,
            'created_at': datetime.now().isoformat(),
            'created_by': session_data.get('user_id', 'system') if session_data else 'system'
        }

        qr_codes[qr_record['id']] = qr_record
        save_data()

        print(f"✅ Container QR generated: {container_id}")

        return jsonify({
            'success': True,
            'container_info': {
                'id': container_id,
                'type': container_type,
                'location': location
            },
            'qr_data': qr_data,
            'qr_image': f'data:image/png;base64,{qr_base64}',
            'qr_id': qr_record['id']
        })

    except Exception as e:
        logger.error(f"Container QR generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/qr/container', methods=['POST'])
def generate_container_qr_api():
    """Generate QR code for containers (legacy endpoint)"""
    try:
        data = request.get_json()
        container_id = data.get('container_id', f'CNT-{int(time.time())}')

        # Generate QR code
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(container_id)
            qr.make(fit=True)
        except Exception as qr_error:
            logger.error(f"QR code generation failed: {qr_error}")
            return jsonify({'success': False, 'error': 'QR code generation failed'}), 500

        qr_image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        print(f"✅ Container QR generated: {container_id}")

        return jsonify({
            'success': True,
            'container_id': container_id,
            'qr_image': f'data:image/png;base64,{qr_base64}'
        })

    except Exception as e:
        logger.error(f"Container QR generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/widget-access', methods=['GET'])
def get_widget_access():
    """Get available widgets based on user role hierarchy"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        user_role = session_data.get('role', 'user')
        user_id = session_data.get('user_id')

        # Get employee data for widget access levels
        employee_data = None
        for emp_id, emp in employees.items():
            if emp.get('id') == user_id:
                employee_data = emp
                break

        widget_access_levels = ['user']
        if employee_data:
            widget_access_levels = employee_data.get('widget_access_level', ['user'])

        # Widget hierarchy configuration
        widget_catalog = {
            'executive': [
                {'id': 'board_overview', 'name': 'Board Overview', 'icon': '📊', 'url': '/board_reporting'},
                {'id': 'financial_summary', 'name': 'Financial Summary', 'icon': '💰', 'url': '/financial_reports'},
                {'id': 'company_performance', 'name': 'Company Performance', 'icon': '📈', 'url': '/analytics_dashboard'},
                {'id': 'strategic_planning', 'name': 'Strategic Planning', 'icon': '🎯', 'url': '/competitive_advantage_dashboard'}
            ],
            'manager': [
                {'id': 'warehouse_overview', 'name': 'Warehouse Overview', 'icon': '🏭', 'url': '/analytics_dashboard'},
                {'id': 'employee_management', 'name': 'Employee Management', 'icon': '👥', 'url': '/company_employee_management'},
                {'id': 'department_chat', 'name': 'Department Chat', 'icon': '💬', 'url': '/department_group_chat'},
                {'id': 'performance_tracking', 'name': 'Performance Tracking', 'icon': '📊', 'url': '/reports_hub'},
                {'id': 'inventory_control', 'name': 'Inventory Control', 'icon': '📦', 'url': '/inventory_management'}
            ],
            'admin': [
                {'id': 'receiving', 'name': 'Receiving', 'icon': '📥', 'url': '/receiving'},
                {'id': 'putaway', 'name': 'Putaway', 'icon': '🏗️', 'url': '/putaway'},
                {'id': 'cycle_counting', 'name': 'Cycle Counting', 'icon': '🔍', 'url': '/cycle_counting'},
                {'id': 'quality_check', 'name': 'Quality Check', 'icon': '✅', 'url': '/quality_check'},
                {'id': 'exception_handling', 'name': 'Exception Handling', 'icon': '⚠️', 'url': '/exceptions_hub'}
            ],
            'user': [
                {'id': 'order_picking', 'name': 'Order Picking', 'icon': '📦', 'url': '/order_picking'},
                {'id': 'shipping', 'name': 'Shipping', 'icon': '🚚', 'url': '/shipping'},
                {'id': 'qr_scanner', 'name': 'QR Scanner', 'icon': '📱', 'url': '/warehouse_video_scanner'},
                {'id': 'my_tasks', 'name': 'My Tasks', 'icon': '✓', 'url': '/employee_dashboard'}
            ]
        }

        # Build available widgets based on access levels
        available_widgets = []
        for level in widget_access_levels:
            if level in widget_catalog:
                available_widgets.extend(widget_catalog[level])

        return jsonify({
            'success': True,
            'user_role': user_role,
            'access_levels': widget_access_levels,
            'available_widgets': available_widgets,
            'widget_catalog': widget_catalog
        })

    except Exception as e:
        logger.error(f"Error getting widget access: {e}")
        return jsonify({'error': 'Failed to get widget access'}), 500

@app.route('/api/containers', methods=['GET'])
def get_all_containers():
    """Get all containers for the current company"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        company_containers = []

        # Filter containers by company
        for container_uuid, container_data in containers.items():
            if container_data.get('company_id') == company_id:
                company_containers.append({
                    'id': container_data.get('container_id', container_uuid),
                    'type': container_data.get('type', 'Unknown'),
                    'location': container_data.get('location', 'Unknown'),
                    'department': container_data.get('department', 'Unknown'),
                    'status': container_data.get('status', 'active'),
                    'created_at': container_data.get('created_at', ''),
                    'items_count': len(container_data.get('items', []))
                })

        # Sort by creation date (newest first)
        company_containers.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return jsonify({
            'success': True,
            'containers': company_containers,
            'total': len(company_containers)
        })

    except Exception as e:
        logger.error(f"Error fetching containers: {e}")
        return jsonify({'error': 'Failed to retrieve containers'}), 500

@app.route('/api/shipping/loading-plan', methods=['POST'])
def generate_loading_plan():
    """Generate a loading plan for shipment"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        data = request.get_json()
        
        plan_id = f"PLAN-{int(time.time() * 1000)}"
        loading_plan = {
            'plan_id': plan_id,
            'company_id': company_id,
            'manifest_items': data.get('manifest_items', []),
            'truck_id': data.get('truck_id'),
            'created_at': datetime.now().isoformat(),
            'created_by': session_data.get('username'),
            'status': 'pending'
        }
        
        logger.info(f"Generated loading plan {plan_id} for company {company_id}")
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'loading_plan': loading_plan
        })
    
    except Exception as e:
        logger.error(f"Error generating loading plan: {e}")
        return jsonify({'error': 'Failed to generate loading plan'}), 500

@app.route('/api/shipping/print-documents', methods=['POST'])
def print_loading_documents():
    """Queue print job for loading documents"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        manifest_items = data.get('manifest', [])
        
        if not manifest_items:
            return jsonify({'error': 'No items in manifest'}), 400
        
        print_job_id = f"PRINT-{int(time.time() * 1000)}"
        
        logger.info(f"Print job {print_job_id} queued with {len(manifest_items)} items")
        
        return jsonify({
            'success': True,
            'print_job_id': print_job_id,
            'item_count': len(manifest_items)
        })
    
    except Exception as e:
        logger.error(f"Error printing documents: {e}")
        return jsonify({'error': 'Failed to print documents'}), 500

@app.route('/api/shipping/schedule-pickup', methods=['POST'])
def schedule_pickup():
    """Schedule a pickup for shipment"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        data = request.get_json()
        
        pickup_id = f"PICKUP-{int(time.time() * 1000)}"
        pickup_schedule = {
            'pickup_id': pickup_id,
            'company_id': company_id,
            'pickup_time': data.get('pickup_time'),
            'truck_id': data.get('truck_id'),
            'scheduled_at': datetime.now().isoformat(),
            'scheduled_by': session_data.get('username'),
            'status': 'scheduled'
        }
        
        logger.info(f"Scheduled pickup {pickup_id} for {data.get('pickup_time')}")
        
        return jsonify({
            'success': True,
            'pickup_id': pickup_id,
            'pickup_schedule': pickup_schedule
        })
    
    except Exception as e:
        logger.error(f"Error scheduling pickup: {e}")
        return jsonify({'error': 'Failed to schedule pickup'}), 500

@app.route('/api/picking/daily-tickets', methods=['POST'])
def generate_daily_pick_tickets():
    """Generate pick tickets for the day"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        
        tickets_generated = {
            'date': datetime.now().date().isoformat(),
            'company_id': company_id,
            'tickets': [],
            'total_orders': 5,
            'generated_at': datetime.now().isoformat(),
            'generated_by': session_data.get('username')
        }
        
        for i in range(1, 6):
            tickets_generated['tickets'].append({
                'ticket_id': f"PICK-{datetime.now().strftime('%Y%m%d')}-{str(i).zfill(4)}",
                'order_number': f"ORD-{1000 + i}",
                'priority': 'normal',
                'status': 'pending'
            })
        
        logger.info(f"Generated {len(tickets_generated['tickets'])} pick tickets for {company_id}")
        
        return jsonify({
            'success': True,
            'tickets': tickets_generated['tickets'],
            'total': len(tickets_generated['tickets'])
        })
    
    except Exception as e:
        logger.error(f"Error generating pick tickets: {e}")
        return jsonify({'error': 'Failed to generate pick tickets'}), 500

@app.route('/api/picking/sync-salespad', methods=['POST'])
def sync_salespad_orders():
    """Sync orders from SalesPad"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        
        synced_orders = {
            'sync_time': datetime.now().isoformat(),
            'company_id': company_id,
            'orders_synced': 3,
            'new_orders': [
                {'order_id': 'SP-1001', 'customer': 'Acme Corp', 'items': 5},
                {'order_id': 'SP-1002', 'customer': 'Beta Inc', 'items': 3},
                {'order_id': 'SP-1003', 'customer': 'Gamma LLC', 'items': 7}
            ]
        }
        
        logger.info(f"Synced {synced_orders['orders_synced']} orders from SalesPad for {company_id}")
        
        return jsonify({
            'success': True,
            'orders_synced': synced_orders['orders_synced'],
            'new_orders': synced_orders['new_orders']
        })
    
    except Exception as e:
        logger.error(f"Error syncing SalesPad orders: {e}")
        return jsonify({'error': 'Failed to sync orders'}), 500

@app.route('/api/picking/create-wave', methods=['POST'])
def create_picking_wave():
    """Create a new picking wave"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        data = request.get_json()
        
        wave_id = f"WAVE-{datetime.now().strftime('%Y%m%d')}-{str(int(time.time() * 1000) % 10000).zfill(4)}"
        wave = {
            'wave_id': wave_id,
            'company_id': company_id,
            'wave_type': data.get('wave_type', 'standard'),
            'orders': data.get('orders', []),
            'created_at': datetime.now().isoformat(),
            'created_by': session_data.get('username'),
            'status': 'created'
        }
        
        logger.info(f"Created picking wave {wave_id} for {company_id}")
        
        return jsonify({
            'success': True,
            'wave_id': wave_id,
            'wave': wave
        })
    
    except Exception as e:
        logger.error(f"Error creating picking wave: {e}")
        return jsonify({'error': 'Failed to create wave'}), 500

@app.route('/api/picking/optimize-route', methods=['POST'])
def optimize_pick_route():
    """Generate optimized picking route"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        wave_id = data.get('wave_id')
        
        optimized_route = {
            'wave_id': wave_id,
            'route_id': f"ROUTE-{int(time.time() * 1000)}",
            'total_distance': 450,
            'estimated_time': 25,
            'pick_sequence': ['A1-05', 'A2-12', 'B1-03', 'C3-08'],
            'optimized_at': datetime.now().isoformat()
        }
        
        logger.info(f"Optimized route for wave {wave_id}")
        
        return jsonify({
            'success': True,
            'route': optimized_route
        })
    
    except Exception as e:
        logger.error(f"Error optimizing route: {e}")
        return jsonify({'error': 'Failed to optimize route'}), 500

# Purchase Order API Endpoints
@app.route('/api/purchase-orders', methods=['GET'])
def get_purchase_orders():
    """Get all purchase orders for current company"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        company_pos = [po for po in purchase_orders.values() if po.get('company_id') == company_id]
        
        # Sort by order_date descending
        company_pos.sort(key=lambda x: x.get('order_date', ''), reverse=True)
        
        return jsonify({'success': True, 'purchase_orders': company_pos})
    
    except Exception as e:
        logger.error(f"Error getting purchase orders: {e}")
        return jsonify({'error': 'Failed to get purchase orders'}), 500

@app.route('/api/purchase-orders/<po_id>', methods=['GET'])
def get_purchase_order(po_id):
    """Get specific purchase order with line items"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        po = purchase_orders.get(po_id)
        if not po:
            return jsonify({'error': 'Purchase order not found'}), 404
        
        # Check company access
        if po.get('company_id') != session_data.get('company_id'):
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'success': True, 'purchase_order': po})
    
    except Exception as e:
        logger.error(f"Error getting purchase order {po_id}: {e}")
        return jsonify({'error': 'Failed to get purchase order'}), 500

@app.route('/api/purchase-orders/<po_id>/receive', methods=['PUT'])
def receive_purchase_order_items(po_id):
    """Update received quantities for PO line items"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        po = purchase_orders.get(po_id)
        if not po:
            return jsonify({'error': 'Purchase order not found'}), 404
        
        # Check company access
        if po.get('company_id') != session_data.get('company_id'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        received_items = data.get('items', [])
        
        # Get user info for activity logging
        user_email = session_data.get('email', 'unknown')
        user_name = session_data.get('username', user_email)
        company_id = session_data.get('company_id')
        
        # Update received quantities
        for received_item in received_items:
            line_number = received_item.get('line_number')
            received_qty = received_item.get('received_quantity', 0)
            
            # Find matching line item in PO
            for po_item in po.get('items', []):
                if po_item.get('line_number') == line_number:
                    po_item['received_quantity'] = received_qty
                    
                    # Calculate variance
                    ordered_qty = po_item.get('ordered_quantity', 0)
                    if received_qty < ordered_qty:
                        po_item['variance_type'] = 'short'
                    elif received_qty > ordered_qty:
                        po_item['variance_type'] = 'overage'
                    else:
                        po_item['variance_type'] = None
                    
                    # Update receiving status
                    if received_qty > 0:
                        po_item['receiving_status'] = 'complete' if received_qty == ordered_qty else 'exception'
                        
                        # Log activity for receiving this item with variance tracking
                        variance_note = ''
                        variance_data = {
                            'ordered_quantity': ordered_qty,
                            'received_quantity': received_qty,
                            'variance_type': po_item.get('variance_type'),
                            'variance_amount': received_qty - ordered_qty
                        }
                        
                        if po_item.get('variance_type') == 'short':
                            variance_note = f" (Short: ordered {ordered_qty}, received {received_qty})"
                        elif po_item.get('variance_type') == 'overage':
                            variance_note = f" (Overage: ordered {ordered_qty}, received {received_qty})"
                        
                        activity_id = str(uuid.uuid4())
                        warehouse_activity_history[activity_id] = {
                            'activity_id': activity_id,
                            'company_id': company_id,
                            'user_id': user_email,
                            'user_name': user_name,
                            'action_type': 'receiving',
                            'item_id': po_item.get('item_id', ''),
                            'item_number': po_item.get('item_number', ''),
                            'quantity': received_qty,
                            'from_location': 'VENDOR',
                            'to_location': 'RCV-STAGING',
                            'reference_type': 'PO',
                            'reference_id': po_id,
                            'variance_data': variance_data,
                            'notes': f"Received via PO {po.get('po_number', po_id)}{variance_note}",
                            'timestamp': datetime.now().isoformat(),
                            'created_at': datetime.now().isoformat()
                        }
                    
                    break
        
        # Update PO status if all items received
        all_received = all(item.get('received_quantity', 0) > 0 for item in po.get('items', []))
        if all_received:
            po['status'] = 'received'
        
        save_data()
        logger.info(f"Updated received quantities for PO {po_id}")
        
        return jsonify({'success': True, 'purchase_order': po})
    
    except Exception as e:
        logger.error(f"Error receiving PO items {po_id}: {e}")
        return jsonify({'error': 'Failed to update received quantities'}), 500

@app.route('/api/purchase-orders/<po_id>/generate-putaway-labels', methods=['POST'])
def generate_putaway_labels(po_id):
    """Generate QR labels for putaway for each line item"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        po = purchase_orders.get(po_id)
        if not po:
            return jsonify({'error': 'Purchase order not found'}), 404
        
        # Check company access
        if po.get('company_id') != session_data.get('company_id'):
            return jsonify({'error': 'Access denied'}), 403
        
        labels = []
        
        # Generate label for each item with received quantity > 0
        for item in po.get('items', []):
            if item.get('received_quantity', 0) > 0:
                # Create putaway QR data
                qr_data = f"PUTAWAY:PO:{po_id}:ITEM:{item.get('item_number')}:QTY:{item.get('received_quantity')}:LOC:{item.get('allocated_slot', 'UNASSIGNED')}"
                
                # Generate QR code
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(qr_data)
                qr.make(fit=True)
                qr_image = qr.make_image(fill_color="black", back_color="white")
                
                # Convert to base64
                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                qr_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                labels.append({
                    'line_number': item.get('line_number'),
                    'item_number': item.get('item_number'),
                    'description': item.get('description'),
                    'quantity': item.get('received_quantity'),
                    'destination': item.get('allocated_slot', 'UNASSIGNED'),
                    'qr_data': qr_data,
                    'qr_image': f'data:image/png;base64,{qr_base64}'
                })
        
        logger.info(f"Generated {len(labels)} putaway labels for PO {po_id}")
        
        return jsonify({'success': True, 'labels': labels})
    
    except Exception as e:
        logger.error(f"Error generating putaway labels for PO {po_id}: {e}")
        return jsonify({'error': 'Failed to generate putaway labels'}), 500

# Warehouse Activity History API Endpoints
def generate_activity_id():
    """Generate unique activity ID"""
    return f"ACT-{str(int(time.time() * 1000))}-{secrets.token_hex(3).upper()}"

@app.route('/api/warehouse-activity/log', methods=['POST'])
def log_warehouse_activity():
    """Log warehouse activity (receiving, movement, transfer, cycle count)"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        user_email = session_data.get('email')
        
        data = request.get_json()
        
        activity_id = generate_activity_id()
        activity = {
            'id': activity_id,
            'company_id': company_id,
            'user_email': user_email,
            'user_name': session_data.get('name', 'Unknown User'),
            'user_role': session_data.get('role', 'worker'),
            'action_type': data.get('action_type'),  # receiving, movement, transfer, cycle_count, putaway
            'item_number': data.get('item_number'),
            'item_description': data.get('item_description'),
            'quantity': data.get('quantity', 0),
            'from_location': data.get('from_location'),
            'to_location': data.get('to_location'),
            'reference_type': data.get('reference_type'),  # PO, ASN, Transfer, etc.
            'reference_id': data.get('reference_id'),
            'notes': data.get('notes', ''),
            'timestamp': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        warehouse_activity_history[activity_id] = activity
        save_data()
        
        logger.info(f"Logged warehouse activity: {data.get('action_type')} by {user_email}")
        
        return jsonify({'success': True, 'activity': activity})
    
    except Exception as e:
        logger.error(f"Error logging warehouse activity: {e}")
        return jsonify({'error': 'Failed to log activity'}), 500

@app.route('/api/warehouse-activity', methods=['GET'])
def get_warehouse_activity():
    """Get warehouse activity history with role-based filtering"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        user_role = session_data.get('role', 'worker')
        
        # Role-based access: admins, managers, cycle_count, lift_driver can view history
        allowed_roles = ['admin', 'manager', 'cycle_count', 'lift_driver']
        if user_role not in allowed_roles:
            return jsonify({'error': 'Access denied. Only admins, managers, cycle count users, and drivers can view activity history.'}), 403
        
        # Filter by company
        company_activities = [act for act in warehouse_activity_history.values() if act.get('company_id') == company_id]
        
        # Apply filters from query parameters
        action_type = request.args.get('action_type')
        user_email = request.args.get('user_email')
        item_number = request.args.get('item_number')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        filtered_activities = company_activities
        
        if action_type:
            filtered_activities = [act for act in filtered_activities if act.get('action_type') == action_type]
        
        if user_email:
            filtered_activities = [act for act in filtered_activities if act.get('user_email') == user_email]
        
        if item_number:
            filtered_activities = [act for act in filtered_activities if act.get('item_number') == item_number]
        
        if from_date:
            filtered_activities = [act for act in filtered_activities if act.get('timestamp', '') >= from_date]
        
        if to_date:
            filtered_activities = [act for act in filtered_activities if act.get('timestamp', '') <= to_date]
        
        # Sort by timestamp descending (most recent first)
        filtered_activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Limit to last 500 records
        filtered_activities = filtered_activities[:500]
        
        return jsonify({'success': True, 'activities': filtered_activities, 'count': len(filtered_activities)})
    
    except Exception as e:
        logger.error(f"Error getting warehouse activity: {e}")
        return jsonify({'error': 'Failed to get activity history'}), 500

@app.route('/api/warehouse-activity/stats', methods=['GET'])
def get_warehouse_activity_stats():
    """Get warehouse activity statistics"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        company_activities = [act for act in warehouse_activity_history.values() if act.get('company_id') == company_id]
        
        # Calculate statistics
        today = datetime.now().date().isoformat()
        today_activities = [act for act in company_activities if act.get('timestamp', '').startswith(today)]
        
        stats = {
            'total_activities': len(company_activities),
            'today_activities': len(today_activities),
            'by_action_type': {},
            'by_user': {},
            'recent_users': []
        }
        
        # Group by action type
        for act in company_activities:
            action_type = act.get('action_type', 'unknown')
            stats['by_action_type'][action_type] = stats['by_action_type'].get(action_type, 0) + 1
        
        # Group by user
        for act in company_activities:
            user_name = act.get('user_name', 'Unknown')
            stats['by_user'][user_name] = stats['by_user'].get(user_name, 0) + 1
        
        # Get recent active users (last 10)
        recent_users = list(set([act.get('user_name', 'Unknown') for act in company_activities[:50]]))
        stats['recent_users'] = recent_users[:10]
        
        return jsonify({'success': True, 'stats': stats})
    
    except Exception as e:
        logger.error(f"Error getting activity stats: {e}")
        return jsonify({'error': 'Failed to get activity stats'}), 500

# Role-Based Inventory Filtering API
@app.route('/api/inventory/by-role', methods=['GET'])
def get_inventory_by_role():
    """Get inventory filtered by user role"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        user_role = session_data.get('role', 'worker')
        
        # Get all inventory for company
        company_inventory = [item for item in inventory_items.values() if item.get('company_id') == company_id]
        
        # Apply role-based filtering
        filtered_inventory = []
        
        if user_role == 'admin' or user_role == 'manager':
            # Admins and managers see everything
            filtered_inventory = company_inventory
        
        elif user_role == 'lift_driver':
            # Lift drivers see items that need movement, heavy/bulk items, items in specific zones
            filtered_inventory = [
                item for item in company_inventory
                if (
                    item.get('quantity', 0) > 50 or  # Bulk items
                    item.get('status') in ['needs_putaway', 'needs_relocation'] or
                    (item.get('location', '').startswith('RCV') or  # Receiving areas
                     item.get('location', '').startswith('STAGE'))  # Staging areas
                )
            ]
        
        elif user_role == 'picker' or user_role == 'worker':
            # Pickers see available items for picking, fast-moving items
            filtered_inventory = [
                item for item in company_inventory
                if item.get('status') in ['available', 'active'] and
                   item.get('quantity', 0) > 0
            ]
        
        elif user_role == 'receiver':
            # Receivers see recently received items, items in receiving locations
            filtered_inventory = [
                item for item in company_inventory
                if (
                    item.get('location', '').startswith('RCV') or
                    item.get('status') == 'needs_putaway' or
                    item.get('source') == 'receiving'
                )
            ]
        
        elif user_role == 'cycle_count':
            # Cycle count sees all items for counting purposes
            filtered_inventory = company_inventory
        
        else:
            # Default: show available items
            filtered_inventory = [
                item for item in company_inventory
                if item.get('status') in ['available', 'active']
            ]
        
        # Sort by location for easier viewing
        filtered_inventory.sort(key=lambda x: (x.get('location', ''), x.get('item_number', '')))
        
        return jsonify({
            'success': True,
            'role': user_role,
            'items': filtered_inventory,
            'count': len(filtered_inventory),
            'total_count': len(company_inventory)
        })
    
    except Exception as e:
        logger.error(f"Error getting role-based inventory: {e}")
        return jsonify({'error': 'Failed to get inventory'}), 500

# ASN (Advanced Shipping Notice) API Endpoints
def generate_asn_id():
    """Generate unique ASN ID"""
    now = datetime.now()
    return f"ASN-{now.strftime('%y%m%d')}-{str(int(time.time() * 1000) % 100000).zfill(5)}"

def generate_pallet_id():
    """Generate unique pallet ID"""
    return f"PLT-{str(int(time.time() * 1000) % 10000).zfill(4)}"

@app.route('/api/asns', methods=['GET'])
def list_asns():
    """List all ASNs for current company"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        company_id = session_data.get('company_id')
        company_asns = [asn for asn in asns.values() if asn.get('company_id') == company_id]
        
        # Sort by created_at descending
        company_asns.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({'success': True, 'asns': company_asns})
    
    except Exception as e:
        logger.error(f"Error listing ASNs: {e}")
        return jsonify({'error': 'Failed to list ASNs'}), 500

@app.route('/api/asns', methods=['POST'])
def create_asn():
    """Create new ASN"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        if not data.get('po_number'):
            return jsonify({'error': 'po_number is required'}), 400
        if not data.get('vendor'):
            return jsonify({'error': 'vendor is required'}), 400

        company_id = session_data.get('company_id')
        asn_id = generate_asn_id()
        
        # Process pallets
        pallets = []
        for i, p in enumerate(data.get('pallets', [])):
            pallet_id = p.get('pallet_id') or generate_pallet_id()
            pallets.append({
                'pallet_id': pallet_id,
                'sequence': p.get('sequence') or f"{i+1}/{len(data.get('pallets', []))}",
                'weight_lb': p.get('weight_lb'),
                'dims_in': p.get('dims_in', [48, 40, 60]),
                'lines': [
                    {
                        'sku': l.get('sku'),
                        'desc': l.get('desc'),
                        'cases': l.get('cases', 0),
                        'units': l.get('units', 0),
                        'lot': l.get('lot'),
                        'exp': l.get('exp')
                    }
                    for l in p.get('lines', [])
                ],
                'link': p.get('link') or f"https://qrlegends.com/p/{data.get('po_number')}/{pallet_id}"
            })
        
        asn = {
            'asn_id': asn_id,
            'company_id': company_id,
            'po_number': data.get('po_number'),
            'vendor': data.get('vendor'),
            'vendor_email': data.get('vendor_email'),
            'ship_from': data.get('ship_from'),
            'ship_to': data.get('ship_to'),
            'eta': data.get('eta'),
            'carrier': data.get('carrier'),
            'pro': data.get('pro'),
            'status': 'Draft',
            'pallets': pallets,
            'comms': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'created_by': session_data.get('username')
        }
        
        asns[asn_id] = asn
        save_data()
        
        logger.info(f"Created ASN {asn_id} for company {company_id}")
        
        return jsonify({'success': True, 'asn': asn}), 201
    
    except Exception as e:
        logger.error(f"Error creating ASN: {e}")
        return jsonify({'error': 'Failed to create ASN'}), 500

@app.route('/api/asns/<asn_id>', methods=['GET'])
def get_asn(asn_id):
    """Get specific ASN"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        asn = asns.get(asn_id)
        if not asn:
            return jsonify({'error': 'ASN not found'}), 404
        
        # Verify company access
        if asn.get('company_id') != session_data.get('company_id'):
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'success': True, 'asn': asn})
    
    except Exception as e:
        logger.error(f"Error getting ASN: {e}")
        return jsonify({'error': 'Failed to get ASN'}), 500

@app.route('/api/asns/<asn_id>', methods=['PUT'])
def update_asn(asn_id):
    """Update existing ASN"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        asn = asns.get(asn_id)
        if not asn:
            return jsonify({'error': 'ASN not found'}), 404
        
        # Verify company access
        if asn.get('company_id') != session_data.get('company_id'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        asn.update({
            'po_number': data.get('po_number', asn.get('po_number')),
            'vendor': data.get('vendor', asn.get('vendor')),
            'vendor_email': data.get('vendor_email', asn.get('vendor_email')),
            'ship_from': data.get('ship_from', asn.get('ship_from')),
            'ship_to': data.get('ship_to', asn.get('ship_to')),
            'eta': data.get('eta', asn.get('eta')),
            'carrier': data.get('carrier', asn.get('carrier')),
            'pro': data.get('pro', asn.get('pro')),
            'pallets': data.get('pallets', asn.get('pallets')),
            'updated_at': datetime.now().isoformat()
        })
        
        save_data()
        
        logger.info(f"Updated ASN {asn_id}")
        
        return jsonify({'success': True, 'asn': asn})
    
    except Exception as e:
        logger.error(f"Error updating ASN: {e}")
        return jsonify({'error': 'Failed to update ASN'}), 500

@app.route('/api/asns/<asn_id>/send', methods=['POST'])
def send_asn(asn_id):
    """Send ASN to vendor (mark as sent and log communication)"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        asn = asns.get(asn_id)
        if not asn:
            return jsonify({'error': 'ASN not found'}), 404
        
        # Verify company access
        if asn.get('company_id') != session_data.get('company_id'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json() or {}
        to = data.get('to') or asn.get('vendor_email') or 'vendor@example.com'
        
        # Update ASN status
        asn['status'] = 'Sent'
        asn['sent_at'] = datetime.now().isoformat()
        
        # Log communication
        if 'comms' not in asn:
            asn['comms'] = []
        
        asn['comms'].append({
            'ts': datetime.now().isoformat(),
            'type': 'send',
            'channel': data.get('channel', 'email'),
            'to': to,
            'sent_by': session_data.get('username')
        })
        
        save_data()
        
        # Generate email preview
        subject = f"ASN for PO {asn.get('po_number')} – arriving {asn.get('eta') or 'TBD'}"
        body = f"""Hi {asn.get('vendor')},

Attached is the ASN for PO {asn.get('po_number')}.
Carrier: {asn.get('carrier') or 'TBD'}  PRO: {asn.get('pro') or 'TBD'}
Pallets: {len(asn.get('pallets', []))}  ETA: {asn.get('eta') or 'TBD'}

Labels: Please use the QR links per pallet (see CSV).

Thanks,
QRLegends Receiving"""
        
        logger.info(f"Sent ASN {asn_id} to {to}")
        
        return jsonify({
            'success': True,
            'ok': True,
            'subject': subject,
            'body': body
        })
    
    except Exception as e:
        logger.error(f"Error sending ASN: {e}")
        return jsonify({'error': 'Failed to send ASN'}), 500

@app.route('/api/asns/<asn_id>/csv', methods=['GET'])
def export_asn_csv(asn_id):
    """Export ASN as CSV"""
    try:
        session_data = get_current_session()
        if not session_data or not session_data.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401

        asn = asns.get(asn_id)
        if not asn:
            return jsonify({'error': 'ASN not found'}), 404
        
        # Verify company access
        if asn.get('company_id') != session_data.get('company_id'):
            return jsonify({'error': 'Access denied'}), 403
        
        # Build CSV
        lines = [['asn_id', 'po_number', 'pallet_id', 'seq', 'sku', 'description', 'cases', 'units', 'lot', 'exp', 'weight_lb', 'length_in', 'width_in', 'height_in', 'carrier', 'pro', 'eta', 'link']]
        
        for p in asn.get('pallets', []):
            for l in p.get('lines', []):
                lines.append([
                    asn.get('asn_id'),
                    asn.get('po_number'),
                    p.get('pallet_id'),
                    p.get('sequence'),
                    l.get('sku', ''),
                    l.get('desc', ''),
                    l.get('cases', ''),
                    l.get('units', ''),
                    l.get('lot', ''),
                    l.get('exp', ''),
                    p.get('weight_lb', ''),
                    p.get('dims_in', [0,0,0])[0] if p.get('dims_in') else '',
                    p.get('dims_in', [0,0,0])[1] if p.get('dims_in') else '',
                    p.get('dims_in', [0,0,0])[2] if p.get('dims_in') else '',
                    asn.get('carrier', ''),
                    asn.get('pro', ''),
                    asn.get('eta', ''),
                    p.get('link', '')
                ])
        
        csv_content = '\n'.join([','.join([str(cell) for cell in row]) for row in lines])
        
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename="{asn_id}.csv"'
        
        return response
    
    except Exception as e:
        logger.error(f"Error exporting ASN CSV: {e}")
        return jsonify({'error': 'Failed to export CSV'}), 500

# Catch-all route for HTML pages
def inject_demo_banner(html_content):
    """Inject demo mode banner into HTML content"""
    if '<body>' in html_content:
        demo_banner = '''
<div id="demoBanner" style="
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
    padding: 8px 16px;
    text-align: center;
    font-size: 14px;
    font-weight: 500;
    z-index: 10000;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
">
    🔬 Demo Mode — Data resets nightly; some actions are simulated | 
    <a href="/logout" style="color: white; text-decoration: underline; margin-left: 8px;">Exit Demo</a>
</div>
<script>
    // Adjust page content for demo banner
    document.addEventListener('DOMContentLoaded', function() {
        document.body.style.paddingTop = '40px';
    });
</script>
'''
        html_content = html_content.replace('<body>', '<body>' + demo_banner)
    return html_content

def inject_dark_theme(html_content):
    """Inject dark theme CSS and JS into HTML content"""
    if '<head>' in html_content and 'auto_theme_injector.js' not in html_content:
        theme_injection = '''
<script src="/static/auto_theme_injector.js"></script>
<script src="/static/apply_professional_styling.js"></script>
<style>
:root {
  --ql-bg: #0b1724;
  --ql-panel: #0f2340;
  --ql-card: #102846;
  --ql-text: #dbe8ff;
  --ql-sub: #97a6c1;
  --ql-primary: #3b82f6;
  --ql-success: #22c55e;
  --ql-warning: #f59e0b;
  --ql-danger: #ef4444;
  --ql-accent: #6366f1;
  --ql-border: rgba(255,255,255,.12);
  --ql-surface: rgba(255,255,255,.06);
}

body {
  background: radial-gradient(1200px 600px at 60% -100px, #123a86 0%, #0e2242 45%, #081b2e 100%) fixed !important;
  color: var(--ql-text) !important;
  font-family: Inter, ui-sans-serif, system-ui, Arial, sans-serif !important;
  min-height: 100vh;
}

.container, .main-content, .page-content {
  background: rgba(45, 55, 72, 0.8) !important;
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  margin: 20px auto;
  max-width: 1200px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  border: 1px solid rgba(99, 102, 241, 0.2);
  color: var(--ql-text) !important;
}
</style>
'''
        html_content = html_content.replace('<head>', '<head>' + theme_injection, 1)
    return html_content

@app.route('/widget_customization')
def widget_customization():
    try:
        with open(os.path.join('static', 'widget_customization.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        logger.error(f"Error loading widget customization: widget_customization.html not found")
        return render_template_string("""
        <html><body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
        <h2>🧩 Widget Customization</h2>
        <p>Widget customization is currently being set up. Please try again shortly.</p>
        <a href="/main_dashboard" style="color: #3b82f6; text-decoration: none;">← Back to Dashboard</a>
        </body></html>
        """)

@app.route('/regional_performance')
def regional_performance():
    try:
        with open(os.path.join('static', 'regional_performance.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Regional Performance - File Not Found</h1>", 404

@app.route('/regional_manager_mobile')
def regional_manager_mobile():
    try:
        with open(os.path.join('static', 'regional_manager_mobile.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Regional Manager Mobile - File Not Found</h1>", 404

# Add missing page routes
@app.route('/purchase_orders')
def page_purchase_orders():
    try:
        with open(os.path.join('static', 'purchase_orders.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Purchase Orders - File Not Found</h1>", 404

@app.route('/receiving')
def receiving():
    try:
        with open(os.path.join('static', 'receiving.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Receiving - File Not Found</h1>", 404

@app.route('/warehouse_activity_history')
def page_warehouse_activity_history():
    try:
        with open(os.path.join('static', 'warehouse_activity_history.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Warehouse Activity History - File Not Found</h1>", 404

@app.route('/role_inventory')
def role_inventory():
    try:
        with open(os.path.join('static', 'role_inventory.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = inject_dark_theme(html_content)
            return html_content
    except FileNotFoundError:
        return "<h1>Role-Based Inventory - File Not Found</h1>", 404

@app.route('/job_manager')
def job_manager():
    try:
        with open(os.path.join('static', 'job_manager.html'), 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Manager Dashboard - File Not Found</h1>", 404

@app.route('/job_inventory_analyst')
def job_inventory_analyst():
    try:
        with open(os.path.join('static', 'job_inventory_analyst.html'), 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Inventory Analyst - File Not Found</h1>", 404

@app.route('/job_stock_mover')
def job_stock_mover():
    try:
        with open(os.path.join('static', 'job_stock_mover.html'), 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Stock Mover - File Not Found</h1>", 404

@app.route('/job_transfer_picker')
def job_transfer_picker():
    try:
        with open(os.path.join('static', 'job_transfer_picker.html'), 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Transfer Picker - File Not Found</h1>", 404

@app.route('/job_order_picker')
def job_order_picker():
    try:
        with open(os.path.join('static', 'job_order_picker.html'), 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Order Picker - File Not Found</h1>", 404

# Favicon route to prevent 404 errors
@app.route('/favicon.ico')
def favicon():
    """Serve favicon to prevent 404 errors"""
    try:
        return send_from_directory('static', 'qr_legends_logo.png', mimetype='image/png')
    except Exception as e:
        logger.error(f"Error serving favicon: {e}")
        # Return a minimal 1x1 transparent GIF as fallback
        return Response(
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00\x3b',
            mimetype='image/gif'
        )

@app.route('/api/inventory', methods=['GET'])
def api_inventory_alias():
    """Alias for /api/inventory/items - returns inventory items for the current company"""
    try:
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'

        company_items = [
            {**item, 'id': iid}
            for iid, item in inventory_items.items()
            if item.get('company_id') == company_id
        ]

        if not company_items:
            company_items = [
                {'id':'item_001','sku':'ABC-001','name':'Industrial Bolts M8','category':'Hardware','location':'A-01-B','quantity':150,'reorder_point':30,'unit_cost':0.85,'company_id':company_id},
                {'id':'item_002','sku':'ABC-002','name':'Steel Washers','category':'Hardware','location':'A-01-C','quantity':420,'reorder_point':100,'unit_cost':0.25,'company_id':company_id},
                {'id':'item_003','sku':'EL-001','name':'Circuit Board A','category':'Electronics','location':'B-03-A','quantity':8,'reorder_point':15,'unit_cost':45.00,'company_id':company_id},
                {'id':'item_004','sku':'PK-001','name':'Cardboard Box L','category':'Packaging','location':'C-02-B','quantity':0,'reorder_point':50,'unit_cost':1.20,'company_id':company_id},
                {'id':'item_005','sku':'SF-001','name':'Safety Helmet','category':'Safety','location':'D-01-A','quantity':6,'reorder_point':10,'unit_cost':22.50,'company_id':company_id},
                {'id':'item_006','sku':'MT-001','name':'Motor Bearing 6202','category':'Mechanical','location':'A-04-A','quantity':32,'reorder_point':10,'unit_cost':8.75,'company_id':company_id},
                {'id':'item_007','sku':'PK-002','name':'Bubble Wrap Roll','category':'Packaging','location':'C-02-A','quantity':3,'reorder_point':8,'unit_cost':14.99,'company_id':company_id},
                {'id':'item_008','sku':'EL-002','name':'Power Cable 2m','category':'Electronics','location':'B-03-B','quantity':55,'reorder_point':20,'unit_cost':6.50,'company_id':company_id},
            ]

        return jsonify({'success': True, 'items': company_items, 'count': len(company_items)})
    except Exception as e:
        logger.error(f"Error in /api/inventory: {e}")
        return jsonify({'error': 'Failed to load inventory'}), 500


@app.route('/api/warehouse/activity-history', methods=['GET'])
def api_warehouse_activity_history():
    """Return warehouse activity history for the current company"""
    try:
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'

        activities = [
            act for act in warehouse_activity_history.values()
            if act.get('company_id') == company_id
        ]
        activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        if not activities:
            now = datetime.now()
            activities = [
                {'id':'act_001','action_type':'receiving','item_number':'PO-2024-018','item_description':'Pallet of Electronics','quantity':24,'from_location':'Dock 1','to_location':'Zone B-12','user_name':'John Smith','timestamp':(now).isoformat(),'company_id':company_id},
                {'id':'act_002','action_type':'putaway','item_number':'SKU-0042','item_description':'Industrial Parts','quantity':50,'from_location':'Staging','to_location':'Zone A-05','user_name':'Maria Garcia','timestamp':(now).isoformat(),'company_id':company_id},
                {'id':'act_003','action_type':'transfer','item_number':'TXN-1001','item_description':'Hardware Components','quantity':30,'from_location':'Zone C','to_location':'Zone A','user_name':'James Lee','timestamp':(now).isoformat(),'company_id':company_id},
                {'id':'act_004','action_type':'order_pick','item_number':'ORD-78421','item_description':'Customer Order','quantity':12,'from_location':'Zone A-05','to_location':'Shipping Dock','user_name':'Tom Williams','timestamp':(now).isoformat(),'company_id':company_id},
                {'id':'act_005','action_type':'cycle_count','item_number':'Zone A','item_description':'Cycle Count','quantity':0,'from_location':'Zone A','to_location':'Zone A','user_name':'Sarah Johnson','timestamp':(now).isoformat(),'company_id':company_id},
            ]

        return jsonify({'success': True, 'activities': activities, 'history': activities, 'count': len(activities)})
    except Exception as e:
        logger.error(f"Error in /api/warehouse/activity-history: {e}")
        return jsonify({'error': 'Failed to load activity history'}), 500


@app.route('/api/warehouse/activity', methods=['POST'])
def api_warehouse_activity_log():
    """Log a warehouse activity action from job pages"""
    try:
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'
        user_name = session_data.get('name', 'Unknown') if session_data else 'Unknown'

        data = request.get_json() or {}
        activity_id = f"act_{int(datetime.now().timestamp() * 1000)}"
        activity = {
            'id': activity_id,
            'company_id': company_id,
            'user_name': user_name,
            'action_type': data.get('type', data.get('action_type', 'movement')),
            'item_number': data.get('item_id', data.get('item', data.get('order_id', ''))),
            'item_description': data.get('item', ''),
            'quantity': data.get('qty', data.get('quantity', 0)),
            'from_location': data.get('from', data.get('from_location', '')),
            'to_location': data.get('to', data.get('to_location', '')),
            'notes': str(data),
            'timestamp': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat()
        }
        warehouse_activity_history[activity_id] = activity
        save_data()
        return jsonify({'success': True, 'activity_id': activity_id})
    except Exception as e:
        logger.error(f"Error logging warehouse activity: {e}")
        return jsonify({'success': True, 'activity_id': 'local'})


@app.route('/api/orders', methods=['GET'])
def api_orders():
    """Return open customer orders for the current company"""
    try:
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'

        # Pull from deliveries if available
        company_orders = [
            d for d in deliveries.values()
            if d.get('company_id') == company_id
        ]

        if not company_orders:
            company_orders = [
                {'id':'ORD-2024-1000','customer':'Acme Corp','status':'open','isRush':True,'shipBy':'TODAY 3PM','items':[{'name':'Hex Bolts M8x20','sku':'HW-0042','loc':'A-01-B','qty':50,'picked':False}]},
                {'id':'ORD-2024-1001','customer':'TechStart Inc','status':'open','isRush':False,'shipBy':'Tomorrow','items':[{'name':'Circuit Board A','sku':'EL-1001','loc':'B-03-A','qty':5,'picked':False}]},
                {'id':'ORD-2024-1002','customer':'Metro Wholesale','status':'open','isRush':False,'shipBy':'Tomorrow','items':[{'name':'Bubble Wrap Roll','sku':'PK-0201','loc':'C-02-A','qty':3,'picked':False}]},
            ]

        return jsonify({'success': True, 'orders': company_orders, 'count': len(company_orders)})
    except Exception as e:
        logger.error(f"Error in /api/orders: {e}")
        return jsonify({'error': 'Failed to load orders'}), 500


@app.route('/api/transfers', methods=['GET'])
def api_transfers():
    """Return open transfer orders for the current company"""
    try:
        session_data = get_current_session()
        company_id = session_data.get('company_id', 'demo_company') if session_data else 'demo_company'

        return jsonify({'success': True, 'transfers': [], 'count': 0})
    except Exception as e:
        logger.error(f"Error in /api/transfers: {e}")
        return jsonify({'error': 'Failed to load transfers'}), 500


# Tiered role-based access control mapping
# Tier 1: Basic role access (only their specific page)
TIER_1_ACCESS = {
    'picker': ['order_picking'],
    'lift_driver': ['lift_drivers'],
    'receiver': ['receiving'],
    'shipper': ['shipping'],
    'inventory': ['inventory'],
    'quality': ['quality_check'],
    'sales': ['salespad_dashboard'],
    'accountant': ['accounts_payable', 'accounts_receivable']
}

# Tier 2: Access to role page + department reports
DEPARTMENT_REPORTS = {
    'warehouse': ['reports_hub', 'custom_reports', 'warehouse_chat'],
    'sales': ['erp_sales', 'salespad_new_order', 'salespad_new_quote', 'salespad_invoice_generator', 'salespad_backorders'],
    'finance': ['erp_finance', 'erp_finance_hub', 'financial_reports'],
    'operations': ['operational_kpis', 'analytics_dashboard']
}

# Manager/Admin access (full access to their domain)
MANAGER_ACCESS = ['main_dashboard', 'analytics_dashboard', 'operational_kpis', 'reports_hub', 'custom_reports', 'warehouse_chat', 'order_picking', 'receiving', 'shipping', 'inventory', 'lift_drivers', 'quality_check']

def get_user_tier(employee_id):
    """Get user's tier level from employee data"""
    if employee_id and employee_id in employees:
        return employees[employee_id].get('tier', 1)  # Default to tier 1
    return 1

def get_user_department(employee_id):
    """Get user's department from employee data"""
    if employee_id and employee_id in employees:
        return employees[employee_id].get('department', 'warehouse')
    return 'warehouse'

def check_page_access(user_role, page_name, employee_id=None):
    """Check if user role has access to the requested page based on tier"""
    if not user_role:
        return False
    
    # Admin has access to everything (including scheduling page)
    if user_role == 'admin':
        return True
    
    # Remove .html extension if present
    page_name = page_name.replace('.html', '')
    
    # Public pages that don't require role check
    public_pages = ['company_login', 'employee_login', 'home', 'index', 'privacy', 'terms', 'contact', 'access_denied']
    if page_name in public_pages:
        return True
    
    # Main dashboard is accessible to all authenticated users
    if page_name == 'main_dashboard':
        return True
    
    # Manager gets full access to their domain
    if user_role == 'manager':
        return page_name in MANAGER_ACCESS
    
    # Get user tier and department
    user_tier = get_user_tier(employee_id)
    user_department = get_user_department(employee_id)
    
    # Tier 1: Only access to their specific role page
    if user_tier == 1:
        tier_1_pages = TIER_1_ACCESS.get(user_role, [])
        return page_name in tier_1_pages
    
    # Tier 2: Access to role page + department reports
    elif user_tier == 2:
        tier_1_pages = TIER_1_ACCESS.get(user_role, [])
        dept_reports = DEPARTMENT_REPORTS.get(user_department, [])
        allowed_pages = tier_1_pages + dept_reports
        return page_name in allowed_pages
    
    return False

# Catch-all route for serving static files and pages
@app.route('/<path:filename>')
def catch_all(filename):
    """Catch-all route for serving static files and pages with role-based access control"""
    try:
        # Check if the requested path corresponds to an existing HTML file in static
        if filename.endswith('.html') or '.' not in filename:
            # Construct the potential file path
            html_file_path = os.path.join('static', filename)
            if not html_file_path.endswith('.html'):
                html_file_path += '.html'

            if os.path.isfile(html_file_path):
                # Check role-based access control
                session_data = get_current_session()
                user_role = session_data.get('role') if session_data and session_data.get('authenticated') else None
                employee_id = session_data.get('employee_id') if session_data else None
                
                # Remove .html extension for checking
                page_name = filename.replace('.html', '')
                
                # If user is not authenticated and it's not a public page, redirect to login
                if not session_data or not session_data.get('authenticated'):
                    public_pages = ['company_login', 'employee_login', 'home', 'index', 'privacy', 'terms', 'contact']
                    if page_name not in public_pages:
                        return redirect('/company_login')
                
                # Check if user has access to this page
                if not check_page_access(user_role, page_name, employee_id):
                    # Redirect to access denied page or their appropriate page
                    return redirect('/access_denied')
                
                with open(html_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    # Inject theme if it's a page that should have it
                    if filename not in ['404', '500']: # Avoid injecting into error pages served by this route
                        html_content = inject_dark_theme(html_content)
                    return html_content
            else:
                # If it's not an HTML file or doesn't exist, try serving as a static file
                try:
                    return send_from_directory('static', filename)
                except FileNotFoundError:
                    logger.warning(f"File not found for path: {filename}")
                    # Serve a custom 404 page if the file is not found
                    try:
                        with open(os.path.join('static', '404.html'), 'r', encoding='utf-8') as f:
                            error_html_content = f.read()
                            error_html_content = inject_dark_theme(error_html_content)
                            return error_html_content, 404
                    except FileNotFoundError:
                        return "<h1>404 - Page Not Found</h1>", 404
        else:
            # Handle non-HTML static files normally
            return send_from_directory('static', filename)
    except Exception as e:
        from werkzeug.exceptions import NotFound
        if isinstance(e, NotFound) or isinstance(e, FileNotFoundError):
            logger.warning(f"Page not found: {filename}")
            try:
                with open(os.path.join('static', '404.html'), 'r', encoding='utf-8') as f:
                    error_html_content = f.read()
                    error_html_content = inject_dark_theme(error_html_content)
                    return error_html_content, 404
            except FileNotFoundError:
                return "<h1>404 - Page Not Found</h1>", 404
        logger.error(f"Error in catch_all route for {filename}: {e}")
        try:
            with open(os.path.join('static', '404.html'), 'r', encoding='utf-8') as f:
                error_html_content = f.read()
                error_html_content = inject_dark_theme(error_html_content)
                return error_html_content, 500
        except FileNotFoundError:
            return "<h1>Server Error</h1>", 500


@app.errorhandler(404)
def not_found(error):
    """Custom 404 error handler"""
    try:
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'API endpoint not found',
                'path': request.path
            }), 404
        else:
            # Check if the requested path exists as an HTML file
            requested_file = request.path.strip('/')
            if requested_file and not requested_file.endswith('.html'):
                requested_file += '.html'

            html_file_path = os.path.join('static', requested_file)
            if os.path.isfile(html_file_path):
                try:
                    with open(html_file_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                        html_content = inject_dark_theme(html_content)
                        return html_content
                except Exception:
                    pass

            # Return 404 page
            try:
                with open(os.path.join('static', '404.html'), 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    html_content = inject_dark_theme(html_content)
                    return html_content, 404
            except FileNotFoundError:
                return "<h1>404 - Page Not Found</h1>", 404
    except Exception:
        return "<h1>404 - Page Not Found</h1>", 404

@app.errorhandler(500)
def internal_error(error):
    """Custom 500 error handler with detailed logging"""
    try:
        request_id = str(uuid.uuid4())[:8]

        error_details = {
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'method': request.method,
            'path': request.path,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': traceback.format_exc()
        }

        logger.error(f"🚨 500 ERROR [Request ID: {request_id}]")
        logger.error(f"Path: {request.method} {request.path}")
        logger.error(f"Error: {error}")
        logger.error(f"Stack trace:\n{traceback.format_exc()}")

        try:
            error_log_file = os.path.join(DATA_DIR, 'error_logs.json')
            if os.path.exists(error_log_file):
                with open(error_log_file, 'r') as f:
                    error_logs = json.load(f)
            else:
                error_logs = []

            error_logs.append(error_details)

            if len(error_logs) > 100:
                error_logs = error_logs[-100:]

            with open(error_log_file, 'w') as f:
                json.dump(error_logs, f, indent=2)
        except Exception as log_error:
            logger.error(f"Failed to save error log: {log_error}")

        if request.path.startswith('/api/'):
            response = make_response(jsonify({
                'success': False,
                'error': 'Internal server error',
                'request_id': request_id,
                'timestamp': datetime.now().isoformat()
            }), 500)
            response.headers['X-Request-ID'] = request_id
            return response
        else:
            try:
                with open('static/500.html', 'r') as f:
                    html_content = f.read()
                    html_content = html_content.replace(
                        '</body>',
                        f'<div style="position:fixed;bottom:10px;right:10px;background:#333;color:#fff;padding:5px;font-size:11px;border-radius:3px;">Request ID: {request_id}</div></body>'
                    )
                response = make_response(html_content, 500)
                response.headers['X-Request-ID'] = request_id
                return response
            except FileNotFoundError:
                response = make_response(f"""
                <html>
                <head><title>500 - Internal Server Error</title></head>
                <body>
                <h1>Internal Server Error</h1>
                <p>An unexpected error occurred. Please try again later.</p>
                <div style="position:fixed;bottom:10px;right:10px;background:#333;color:#fff;padding:5px;font-size:11px;border-radius:3px;">Request ID: {request_id}</div>
                </body>
                </html>
                """, 500)
                response.headers['X-Request-ID'] = request_id
                return response
    except Exception as e:
        logger.error(f"Error in 500 handler: {e}")
        return "<h1>500 - Internal Server Error</h1>", 500

# Load data on startup
load_data()
ensure_demo_premium_account()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
