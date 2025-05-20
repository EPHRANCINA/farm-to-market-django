import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import re
import datetime
from functools import wraps
import time
from translations import TRANSLATIONS

# Flask application setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # Generate a random secret key

# Setup directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')

# Create necessary directories
os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Configure Flask app
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['DATABASE'] = os.path.join(INSTANCE_DIR, 'farm_to_market.db')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Translations dictionary
translations = {
    'en': {
        'welcome_title': 'Welcome to Farm to Market',
        'welcome_subtitle': 'Connecting farmers directly with buyers for fresh, local produce',
        'get_started': 'Get Started',
        'learn_more': 'Learn More',
        'features': 'Features',
        'for_farmers': 'For Farmers',
        'for_buyers': 'For Buyers',
        'feature1_title': 'List Your Crops',
        'feature1_desc': 'Easily list your crops and reach potential buyers',
        'feature2_title': 'Manage Inventory',
        'feature2_desc': 'Track your crop inventory and sales',
        'feature3_title': 'Find Fresh Produce',
        'feature3_desc': 'Browse and find fresh produce from local farmers',
        'feature4_title': 'Direct Contact',
        'feature4_desc': 'Connect directly with farmers in your area',
        'login_title': 'Login',
        'login_subtitle': 'Welcome back! Please login to your account',
        'username': 'Username',
        'password': 'Password',
        'remember_me': 'Remember me',
        'login_button': 'Login',
        'no_account': 'No account?',
        'register_link': 'Register here',
        'register_title': 'Register',
        'register_subtitle': 'Create your account to get started',
        'email': 'Email',
        'confirm_password': 'Confirm Password',
        'role': 'Role',
        'farmer': 'Farmer',
        'buyer': 'Buyer',
        'register_button': 'Register',
        'have_account': 'Already have an account?',
        'login_link': 'Login here',
        'add_crop': 'Add New Crop',
        'crop_name': 'Crop Name',
        'quantity': 'Quantity',
        'unit': 'Unit',
        'price': 'Price',
        'region': 'Region',
        'farmer_name': 'Farmer Name',
        'contact_info': 'Contact Info',
        'image': 'Image',
        'submit': 'Submit',
        'search': 'Search',
        'sort_by': 'Sort by',
        'date': 'Date',
        'price_low': 'Price (Low to High)',
        'price_high': 'Price (High to Low)',
        'previous': 'Previous',
        'next': 'Next',
        'no_crops': 'No crops found',
        'error': 'Error',
        'success': 'Success',
        'crop_added': 'Crop added successfully',
        'crop_error': 'Error adding crop',
        'logout': 'Logout',
        'dashboard': 'Dashboard',
        'welcome': 'Welcome',
        'language': 'Language',
        'english': 'English',
        'swahili': 'Swahili',
        'edit_crop': 'Edit Crop',
        'update_crop': 'Update Crop',
        'cancel': 'Cancel',
        'image_optional': 'Leave empty to keep current image',
        'select_unit': 'Select Unit',
        'delete_confirm': 'Are you sure you want to delete this crop?',
        'delete': 'Delete',
        'edit': 'Edit'
    },
    'sw': {
        'welcome_title': 'Karibu kwenye Farm to Market',
        'welcome_subtitle': 'Kuunganisha wakulima moja kwa moja na wanunuzi kwa mazao safi na ya kienyeji',
        'get_started': 'Anza',
        'learn_more': 'Jifunze Zaidi',
        'features': 'Vipengele',
        'for_farmers': 'Kwa Wakulima',
        'for_buyers': 'Kwa Wanunuzi',
        'feature1_title': 'Orodhesha Mazao Yako',
        'feature1_desc': 'Orodhesha mazao yako kwa urahisi na ufikie wanunuzi wanaowezekana',
        'feature2_title': 'Dhibiti Hifadhi',
        'feature2_desc': 'Fuatilia hifadhi yako ya mazao na mauzo',
        'feature3_title': 'Tafuta Mazao Safi',
        'feature3_desc': 'Vinjari na tafuta mazao safi kutoka kwa wakulima wa kienyeji',
        'feature4_title': 'Wasiliana Moja kwa Moja',
        'feature4_desc': 'Wasiliana moja kwa moja na wakulima katika eneo lako',
        'login_title': 'Ingia',
        'login_subtitle': 'Karibu tena! Tafadhali ingia kwenye akaunti yako',
        'username': 'Jina la mtumiaji',
        'password': 'Nywila',
        'remember_me': 'Nikumbuke',
        'login_button': 'Ingia',
        'no_account': 'Huna akaunti?',
        'register_link': 'Jisajili hapa',
        'register_title': 'Jisajili',
        'register_subtitle': 'Unda akaunti yako kuanza',
        'email': 'Barua pepe',
        'confirm_password': 'Thibitisha Nywila',
        'role': 'Jukumu',
        'farmer': 'Mkulima',
        'buyer': 'Mnunuzi',
        'register_button': 'Jisajili',
        'have_account': 'Tayari una akaunti?',
        'login_link': 'Ingia hapa',
        'add_crop': 'Ongeza Mazao Mapya',
        'crop_name': 'Jina la Mazao',
        'quantity': 'Kiasi',
        'unit': 'Kipimo',
        'price': 'Bei',
        'region': 'Mkoa',
        'farmer_name': 'Jina la Mkulima',
        'contact_info': 'Mawasiliano',
        'image': 'Picha',
        'submit': 'Wasilisha',
        'search': 'Tafuta',
        'sort_by': 'Panga kwa',
        'date': 'Tarehe',
        'price_low': 'Bei (Chini hadi Juu)',
        'price_high': 'Bei (Juu hadi Chini)',
        'previous': 'Iliyopita',
        'next': 'Ifuatayo',
        'no_crops': 'Hakuna mazao yaliyopatikana',
        'error': 'Hitilafu',
        'success': 'Imefanikiwa',
        'crop_added': 'Mazao yameongezwa kwa mafanikio',
        'crop_error': 'Hitilafu katika kuongeza mazao',
        'logout': 'Toka',
        'dashboard': 'Dashibodi',
        'welcome': 'Karibu',
        'language': 'Lugha',
        'english': 'Kiingereza',
        'swahili': 'Kiswahili',
        'edit_crop': 'Hariri Mazao',
        'update_crop': 'Sasisha Mazao',
        'cancel': 'Ghairi',
        'image_optional': 'Acha tupu ili kubaki na picha ya sasa',
        'select_unit': 'Chagua Kipimo',
        'delete_confirm': 'Una uhakika unataka kufuta mazao haya?',
        'delete': 'Futa',
        'edit': 'Hariri'
    }
}

# Helper function to get translations
def get_translation(key):
    lang = session.get('language', 'en')
    return translations.get(lang, translations['en']).get(key, key)

# Make get_translation available in templates
app.jinja_env.globals.update(get_translation=get_translation)

# Language selection route
@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in translations:
        session['language'] = lang
    return redirect(request.referrer or url_for('index'))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {str(e)}")
        raise

def init_db():
    try:
        print("Initializing database...")  # Debug print
        print(f"Database path: {app.config['DATABASE']}")  # Debug print
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        
        # Create crops table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id INTEGER NOT NULL,
                crop_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                price REAL NOT NULL,
                region TEXT NOT NULL,
                farmer_name TEXT NOT NULL,
                contact_info TEXT NOT NULL,
                image_path TEXT,
                date_posted TEXT NOT NULL,
                FOREIGN KEY (farmer_id) REFERENCES users (id)
            )
        ''')

        conn.commit()
        print("Database initialized successfully")  # Debug print
        
    except sqlite3.Error as e:
        print(f"Error initializing database: {str(e)}")  # Debug print
        raise
        
    finally:
        if 'conn' in locals():
            conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def farmer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'farmer':
            flash('You must be logged in as a farmer to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize database when the app starts
with app.app_context():
    init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
                         (username, email, generate_password_hash(password), role))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'error')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash('Login successful!', 'success')
                
                if user['role'] == 'farmer':
                    return redirect(url_for('farmer_dashboard'))
                else:
                    return redirect(url_for('buyer_dashboard'))
            else:
                flash('Invalid username or password.', 'error')
                
        except sqlite3.Error as e:
            print(f"Database error in login: {str(e)}")
            flash('An error occurred during login. Please try again.', 'error')
            
        finally:
            conn.close()
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/farmer_dashboard')
@farmer_required
def farmer_dashboard():
    try:
        print("Accessing farmer dashboard...")  # Debug print
        print(f"User ID in session: {session.get('user_id')}")  # Debug print
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get farmer's information first
        cursor.execute('SELECT username, email FROM users WHERE id = ?', (session['user_id'],))
        farmer_info = cursor.fetchone()
        
        if not farmer_info:
            print("No farmer info found")  # Debug print
            flash('Farmer information not found', 'error')
            return redirect(url_for('index'))
            
        print(f"Found farmer info: {farmer_info}")  # Debug print
        
        # Get farmer's crops
        cursor.execute('''
            SELECT id, crop_name, quantity, unit, price, region, 
                   farmer_name, contact_info, date_posted, image_path
            FROM crops 
            WHERE farmer_id = ? 
            ORDER BY date_posted DESC
        ''', (session['user_id'],))
        
        crops = cursor.fetchall()
        print(f"Found {len(crops)} crops")  # Debug print
        
        # Convert crops to list of dictionaries for easier template handling
        crops_list = []
        for crop in crops:
            crops_list.append({
                'id': crop['id'],
                'crop_name': crop['crop_name'],
                'quantity': crop['quantity'],
                'unit': crop['unit'],
                'price': crop['price'],
                'region': crop['region'],
                'farmer_name': crop['farmer_name'],
                'contact_info': crop['contact_info'],
                'date_posted': crop['date_posted'],
                'image_path': crop['image_path']
            })
        
        return render_template('farmer_dashboard.html', 
                             session=session,
                             crops=crops_list,
                             farmer_info=farmer_info)
                             
    except sqlite3.Error as e:
        print(f"Database error in farmer dashboard: {str(e)}")  # Debug print
        flash('An error occurred while loading the dashboard.', 'error')
        return redirect(url_for('index'))
        
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/buyer_dashboard')
@login_required
def buyer_dashboard():
    try:
        print("Accessing buyer dashboard...")  # Debug print
        print(f"User ID in session: {session.get('user_id')}")  # Debug print
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, perform a thorough cleanup of invalid crops
        cursor.execute('''
            DELETE FROM crops 
            WHERE farmer_id NOT IN (SELECT id FROM users WHERE role = 'farmer')
            OR farmer_id IS NULL
            OR farmer_id NOT IN (SELECT id FROM users)
        ''')
        conn.commit()
        
        # Get query parameters
        search = request.args.get('search', '')
        region = request.args.get('region', '')
        sort = request.args.get('sort', 'date')
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Number of items per page
        
        # Build the base query with strict validation
        query = '''
            SELECT c.*, u.username as farmer_username 
            FROM crops c 
            INNER JOIN users u ON c.farmer_id = u.id 
            WHERE u.role = 'farmer'
            AND c.farmer_id IN (SELECT id FROM users WHERE role = 'farmer')
        '''
        params = []
        
        # Add search condition
        if search:
            query += ' AND (c.crop_name LIKE ? OR c.farmer_name LIKE ?)'
            search_term = f'%{search}%'
            params.extend([search_term, search_term])
        
        # Add region filter
        if region:
            query += ' AND c.region = ?'
            params.append(region)
        
        # Add sorting
        if sort == 'price_low':
            query += ' ORDER BY c.price ASC'
        elif sort == 'price_high':
            query += ' ORDER BY c.price DESC'
        else:  # Default sort by date
            query += ' ORDER BY c.date_posted DESC'
        
        # Get total count for pagination
        count_query = f"SELECT COUNT(*) FROM ({query})"
        cursor.execute(count_query, params)
        total_items = cursor.fetchone()[0]
        total_pages = (total_items + per_page - 1) // per_page
        
        # Ensure page is within valid range
        page = max(1, min(page, total_pages)) if total_pages > 0 else 1
        
        # Add pagination
        query += ' LIMIT ? OFFSET ?'
        params.extend([per_page, (page - 1) * per_page])
        
        # Execute the final query
        cursor.execute(query, params)
        crops = cursor.fetchall()
        print(f"Found {len(crops)} crops for buyer dashboard")  # Debug log
        
        # Debug print for image paths
        for crop in crops:
            print(f"Crop: {crop['crop_name']}, Image path: {crop['image_path']}")
        
        # Convert crops to list of dictionaries for easier template handling
        crops_list = []
        for crop in crops:
            crops_list.append({
                'id': crop['id'],
                'crop_name': crop['crop_name'],
                'quantity': crop['quantity'],
                'unit': crop['unit'],
                'price': crop['price'],
                'region': crop['region'],
                'farmer_name': crop['farmer_name'],
                'contact_info': crop['contact_info'],
                'date_posted': crop['date_posted'],
                'image_path': crop['image_path'],
                'farmer_username': crop['farmer_username']
            })
        
        # Get unique regions for filter dropdown
        cursor.execute('SELECT DISTINCT region FROM crops ORDER BY region')
        regions = [row['region'] for row in cursor.fetchall()]
        
        return render_template('buyer_dashboard.html', 
                             session=session,
                             crops=crops_list,
                             search=search,
                             region=region,
                             sort=sort,
                             page=page,
                             total_pages=total_pages,
                             regions=regions)
                             
    except sqlite3.Error as e:
        print(f"Database error in buyer dashboard: {str(e)}")  # Debug print
        flash('An error occurred while loading the dashboard.', 'error')
        return redirect(url_for('index'))
        
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/add_crop', methods=['POST'])
@farmer_required
def add_crop():
    try:
        # Get form data
        crop_name = request.form.get('crop_name')
        quantity = request.form.get('quantity')
        unit = request.form.get('unit')
        price = request.form.get('price')
        region = request.form.get('region')
        farmer_name = request.form.get('farmer_name')
        contact_info = request.form.get('contact_info')
        
        # Validate form data
        if not all([crop_name, quantity, unit, price, region, farmer_name, contact_info]):
            flash('All fields are required', 'error')
            return redirect(url_for('farmer_dashboard'))
            
        # Validate phone number format
        if not re.match(r'^0\d{9}$', contact_info):
            flash('Contact information must be a valid phone number starting with 0 and containing exactly 10 digits', 'error')
            return redirect(url_for('farmer_dashboard'))
        
        # Initialize image_path
        image_path = None
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                if not allowed_file(file.filename):
                    flash('Invalid file type. Only PNG, JPG, JPEG, and GIF files are allowed.', 'error')
                    return redirect(url_for('farmer_dashboard'))
                
                # Check file size (max 5MB)
                if len(file.read()) > 5 * 1024 * 1024:  # 5MB in bytes
                    flash('Image file size must be less than 5MB', 'error')
                    return redirect(url_for('farmer_dashboard'))
                file.seek(0)  # Reset file pointer after reading
                    
                filename = secure_filename(file.filename)
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                
                # Ensure the upload directory exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # Save the file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                print(f"Saved image to: {file_path}")  # Debug print
                
                # Store the relative path in the database using forward slashes
                image_path = os.path.join('uploads', filename).replace('\\', '/')
                print(f"Storing image path in database: {image_path}")  # Debug print
        
        # Get current timestamp
        date_posted = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert crop into database
        cursor.execute('''
            INSERT INTO crops (farmer_id, crop_name, quantity, unit, price, region, 
                             farmer_name, contact_info, image_path, date_posted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], crop_name, quantity, unit, price, region, 
              farmer_name, contact_info, image_path, date_posted))
        
        conn.commit()
        print(f"Added crop with image path: {image_path}")  # Debug print
        flash('Crop added successfully!', 'success')
        
    except sqlite3.Error as e:
        print(f"Database error in add_crop: {str(e)}")  # Debug print
        flash('Error adding crop. Please try again.', 'error')
        
    finally:
        if 'conn' in locals():
            conn.close()
            
    return redirect(url_for('farmer_dashboard'))

@app.route('/edit_crop/<int:crop_id>', methods=['GET', 'POST'])
@farmer_required
def edit_crop(crop_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            # Get form data
            crop_name = request.form.get('crop_name', '').strip()
            quantity = request.form.get('quantity', '').strip()
            unit = request.form.get('unit', '').strip()
            price = request.form.get('price', '').strip()
            region = request.form.get('region', '').strip()
            farmer_name = request.form.get('farmer_name', '').strip()
            contact_info = request.form.get('contact_info', '').strip()
            
            # Validation errors list
            errors = []
            
            # Validate crop name
            if not crop_name:
                errors.append('Crop name is required')
            elif len(crop_name) < 2 or len(crop_name) > 50:
                errors.append('Crop name must be between 2 and 50 characters')
            elif not re.match(r'^[a-zA-Z\s\-]+$', crop_name):
                errors.append('Crop name can only contain letters, spaces, and hyphens')
                
            # Validate quantity
            if not quantity:
                errors.append('Quantity is required')
            else:
                try:
                    quantity = float(quantity)
                    if quantity <= 0:
                        errors.append('Quantity must be greater than 0')
                    elif quantity > 10000:
                        errors.append('Quantity cannot exceed 10,000')
                except ValueError:
                    errors.append('Quantity must be a valid number')
                    
            # Validate unit
            valid_units = ['kg', 'tons', 'grams', 'lbs', 'bags']
            if not unit:
                errors.append('Unit is required')
            elif unit not in valid_units:
                errors.append('Invalid unit selected')
                
            # Validate price
            if not price:
                errors.append('Price is required')
            else:
                try:
                    price = float(price)
                    if price <= 0:
                        errors.append('Price must be greater than 0')
                    elif price > 100000:
                        errors.append('Price cannot exceed 100,000')
                except ValueError:
                    errors.append('Price must be a valid number')
                    
            # Validate region
            if not region:
                errors.append('Region is required')
            elif len(region) < 2 or len(region) > 50:
                errors.append('Region must be between 2 and 50 characters')
            elif not re.match(r'^[a-zA-Z\s\-]+$', region):
                errors.append('Region can only contain letters, spaces, and hyphens')
                
            # Validate farmer name
            if not farmer_name:
                errors.append('Farmer name is required')
            elif len(farmer_name) < 2 or len(farmer_name) > 50:
                errors.append('Farmer name must be between 2 and 50 characters')
            elif not re.match(r'^[a-zA-Z\s\-]+$', farmer_name):
                errors.append('Farmer name can only contain letters, spaces, and hyphens')
                
            # Validate contact information
            if not contact_info:
                errors.append('Contact information is required')
            else:
                # Check if it's a phone number
                if re.match(r'^\d+$', contact_info):
                    if not contact_info.startswith('0'):
                        errors.append('Phone number must start with 0')
                    elif len(contact_info) != 10:
                        errors.append('Phone number must be exactly 10 digits')
                # Check if it's an email
                elif '@' in contact_info:
                    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', contact_info):
                        errors.append('Invalid email format')
                    elif len(contact_info) > 100:
                        errors.append('Email address is too long')
                else:
                    errors.append('Contact information must be either a valid phone number or email address')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return redirect(url_for('edit_crop', crop_id=crop_id))
            
            # Handle image upload
            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    if not allowed_file(file.filename):
                        flash('Invalid file type. Only PNG, JPG, JPEG, and GIF files are allowed.', 'error')
                        return redirect(url_for('edit_crop', crop_id=crop_id))
                    
                    # Check file size (max 5MB)
                    if len(file.read()) > 5 * 1024 * 1024:  # 5MB in bytes
                        flash('Image file size must be less than 5MB', 'error')
                        return redirect(url_for('edit_crop', crop_id=crop_id))
                    file.seek(0)  # Reset file pointer after reading
                        
                    filename = secure_filename(file.filename)
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_path = os.path.join('uploads', filename)
            
            # Update crop in database
            if image_path:
                cursor.execute('''
                    UPDATE crops 
                    SET crop_name = ?, quantity = ?, unit = ?, price = ?, 
                        region = ?, farmer_name = ?, contact_info = ?, image_path = ?
                    WHERE id = ? AND farmer_id = ?
                ''', (crop_name, quantity, unit, price, region, farmer_name, 
                      contact_info, image_path, crop_id, session['user_id']))
            else:
                cursor.execute('''
                    UPDATE crops 
                    SET crop_name = ?, quantity = ?, unit = ?, price = ?, 
                        region = ?, farmer_name = ?, contact_info = ?
                    WHERE id = ? AND farmer_id = ?
                ''', (crop_name, quantity, unit, price, region, farmer_name, 
                      contact_info, crop_id, session['user_id']))
            
            conn.commit()
            flash('Crop updated successfully!', 'success')
            return redirect(url_for('farmer_dashboard'))
            
        else:  # GET request
            # Get crop details
            cursor.execute('''
                SELECT * FROM crops 
                WHERE id = ? AND farmer_id = ?
            ''', (crop_id, session['user_id']))
            crop = cursor.fetchone()
            
            if not crop:
                flash('Crop not found or you do not have permission to edit it.', 'error')
                return redirect(url_for('farmer_dashboard'))
            
            return render_template('edit_crop.html', crop=crop)
            
    except sqlite3.Error as e:
        print(f"Database error in edit_crop: {str(e)}")
        flash('An error occurred while editing the crop.', 'error')
        return redirect(url_for('farmer_dashboard'))
        
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/delete_crop/<int:crop_id>', methods=['POST'])
@farmer_required
def delete_crop(crop_id):
    try:
        print(f"Attempting to delete crop with ID: {crop_id}")  # Debug log
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First verify the crop exists and belongs to the farmer
        cursor.execute('''
            SELECT id, image_path, farmer_id, crop_name 
            FROM crops 
            WHERE id = ?
        ''', (crop_id,))
        crop = cursor.fetchone()
        
        print(f"Found crop to delete: {dict(crop) if crop else None}")  # Debug log
        
        if not crop:
            print(f"Crop {crop_id} not found")  # Debug log
            flash('Crop not found.', 'error')
            return redirect(url_for('farmer_dashboard'))
            
        if crop['farmer_id'] != session['user_id']:
            print(f"Crop {crop_id} belongs to farmer {crop['farmer_id']}, not {session['user_id']}")  # Debug log
            flash('You do not have permission to delete this crop.', 'error')
            return redirect(url_for('farmer_dashboard'))
        
        # Delete the crop with explicit farmer_id check
        cursor.execute('''
            DELETE FROM crops 
            WHERE id = ? AND farmer_id = ?
        ''', (crop_id, session['user_id']))
        
        # Verify the deletion
        if cursor.rowcount == 0:
            print(f"Failed to delete crop {crop_id}")  # Debug log
            flash('Failed to delete crop. Please try again.', 'error')
            return redirect(url_for('farmer_dashboard'))
            
        conn.commit()
        print(f"Successfully deleted crop {crop_id}")  # Debug log
        
        # Delete the associated image file if it exists
        if crop['image_path']:
            try:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                        os.path.basename(crop['image_path']))
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"Deleted image file: {image_path}")  # Debug log
            except Exception as e:
                print(f"Error deleting image file: {str(e)}")
        
        # Verify the crop is actually deleted
        cursor.execute('SELECT id FROM crops WHERE id = ?', (crop_id,))
        if cursor.fetchone():
            print(f"Warning: Crop {crop_id} still exists after deletion")  # Debug log
            flash('Error: Crop was not properly deleted. Please try again.', 'error')
            return redirect(url_for('farmer_dashboard'))
        
        flash('Crop deleted successfully!', 'success')
        
    except sqlite3.Error as e:
        print(f"Database error in delete_crop: {str(e)}")
        flash('An error occurred while deleting the crop.', 'error')
        
    finally:
        if 'conn' in locals():
            conn.close()
            
    return redirect(url_for('farmer_dashboard'))

@app.route('/cleanup_crops')
@login_required
def cleanup_crops():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find crops that don't have a valid farmer
        cursor.execute('''
            DELETE FROM crops 
            WHERE farmer_id NOT IN (SELECT id FROM users)
        ''')
        
        # Also delete any crops that don't have a valid farmer_id
        cursor.execute('''
            DELETE FROM crops 
            WHERE farmer_id IS NULL
        ''')
        
        conn.commit()
        flash('Database cleanup completed.', 'success')
        
    except sqlite3.Error as e:
        print(f"Database error in cleanup: {str(e)}")
        flash('An error occurred during cleanup.', 'error')
        
    finally:
        if 'conn' in locals():
            conn.close()
            
    return redirect(url_for('buyer_dashboard'))

@app.route('/force_delete_all_crops')
@farmer_required
def force_delete_all_crops():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all crops for this farmer
        cursor.execute('''
            SELECT id, image_path 
            FROM crops 
            WHERE farmer_id = ?
        ''', (session['user_id'],))
        crops = cursor.fetchall()
        
        # Delete all crops for this farmer
        cursor.execute('''
            DELETE FROM crops 
            WHERE farmer_id = ?
        ''', (session['user_id'],))
        
        # Delete associated image files
        for crop in crops:
            if crop['image_path']:
                try:
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                            os.path.basename(crop['image_path']))
                    if os.path.exists(image_path):
                        os.remove(image_path)
                except Exception as e:
                    print(f"Error deleting image file: {str(e)}")
        
        conn.commit()
        
        # Verify deletion
        cursor.execute('SELECT COUNT(*) FROM crops WHERE farmer_id = ?', (session['user_id'],))
        remaining = cursor.fetchone()[0]
        
        if remaining == 0:
            flash('All crops have been successfully deleted.', 'success')
        else:
            flash(f'Warning: {remaining} crops could not be deleted.', 'warning')
        
    except sqlite3.Error as e:
        print(f"Database error in force_delete_all_crops: {str(e)}")
        flash('An error occurred while deleting crops.', 'error')
        
    finally:
        if 'conn' in locals():
            conn.close()
            
    return redirect(url_for('farmer_dashboard'))

@app.route('/reset_all_crops')
@login_required
def reset_all_crops():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, get all image paths before deletion
        cursor.execute('SELECT image_path FROM crops')
        image_paths = cursor.fetchall()
        
        # Delete all crops from the database
        cursor.execute('DELETE FROM crops')
        
        # Delete all associated image files
        for row in image_paths:
            if row['image_path']:
                try:
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                            os.path.basename(row['image_path']))
                    if os.path.exists(image_path):
                        os.remove(image_path)
                except Exception as e:
                    print(f"Error deleting image file: {str(e)}")
        
        conn.commit()
        
        # Verify deletion
        cursor.execute('SELECT COUNT(*) FROM crops')
        remaining = cursor.fetchone()[0]
        
        if remaining == 0:
            flash('All crops have been successfully removed from the system.', 'success')
        else:
            flash(f'Warning: {remaining} crops could not be deleted.', 'warning')
        
    except sqlite3.Error as e:
        print(f"Database error in reset_all_crops: {str(e)}")
        flash('An error occurred while resetting crops.', 'error')
        
    finally:
        if 'conn' in locals():
            conn.close()
            
    return redirect(url_for('index'))

@app.route('/reset_database')
@login_required
def reset_database():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Drop and recreate the crops table
        cursor.execute('DROP TABLE IF EXISTS crops')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id INTEGER NOT NULL,
                crop_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                price REAL NOT NULL,
                region TEXT NOT NULL,
                farmer_name TEXT NOT NULL,
                contact_info TEXT NOT NULL,
                image_path TEXT,
                date_posted TEXT NOT NULL,
                FOREIGN KEY (farmer_id) REFERENCES users (id)
            )
        ''')
        
        # Delete all files in the uploads directory
        upload_dir = app.config['UPLOAD_FOLDER']
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")  # Debug print
            except Exception as e:
                print(f"Error deleting file {file_path}: {str(e)}")
        
        conn.commit()
        print("Database reset completed successfully")  # Debug print
        flash('Database has been completely reset. All crops have been removed.', 'success')
        
    except sqlite3.Error as e:
        print(f"Database error in reset_database: {str(e)}")
        flash('An error occurred while resetting the database.', 'error')
        
    finally:
        if 'conn' in locals():
            conn.close()
            
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 