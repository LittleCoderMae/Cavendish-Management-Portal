from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from functools import wraps
from ..extensions import db
from ..models import User, Lecturer, UserRole
import re

# --- Mock Authentication Setup (Simulates Flask-Login) ---
# In a real Flask app, you would use Flask-Login or similar for proper authentication.
# We are using a mock object to allow the templates to render without the full auth setup.

class MockUser:
    """A simple class to hold mock user data and state."""
    def __init__(self, is_authenticated=False):
        self.is_authenticated = is_authenticated
        self.id = 'LCT-1001'
        self.name = 'Dr. Elara Vance'
        self.email = 'elara.vance@university.edu'
        self.course_count = 2

    def is_lecturer(self):
        """Used in the navigation bar logic."""
        return True

# Global Mock User State
current_user = MockUser(is_authenticated=False)

# --- Validation Helper Functions ---
def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit."
    return True, "Password is strong."

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def login_required(f):
    """A decorator to restrict access to authenticated users."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            # Redirect to the login route defined in this blueprint
            return redirect(url_for('lecturer.lecturer_login')) 
        return f(*args, **kwargs)
    return decorated_function

# --- Blueprint Definition ---
# This is the object that app/__init__.py needs to import!
import os
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'lecturer')
lecturer_bp = Blueprint('lecturer', __name__, url_prefix='/lecturer', template_folder=template_dir)

# --- Mock Data for Templates ---
MOCK_COURSES = [
    {'id': 101, 'course_code': 'CS-101', 'course_title': 'Introduction to Programming', 'students_count': 45},
    {'id': 205, 'course_code': 'MA-205', 'course_title': 'Discrete Mathematics', 'students_count': 62},
]

MOCK_STUDENTS = [
    {'reg_number': 'CAV/001/22', 'name': 'Alice Johnson', 'email': 'alice@student.edu'},
    {'reg_number': 'CAV/002/22', 'name': 'Bob Smith', 'email': 'bob@student.edu'},
    {'reg_number': 'CAV/003/22', 'name': 'Charlie Brown', 'email': 'charlie@student.edu'},
    {'reg_number': 'CAV/004/22', 'name': 'Diana Prince', 'email': 'diana@student.edu'},
]
ALL_STUDENTS_COUNT = len(MOCK_STUDENTS)

# --- Routes ---

@lecturer_bp.route('/login', methods=['GET', 'POST'])
def lecturer_login():
    """Handles lecturer login form display and submission (URL: /lecturer/login)."""
    # If already logged in as lecturer via User-based auth, redirect to dashboard
    if 'user_id' in session and session.get('role') == 'lecturer':
        return redirect(url_for('lecturer.dashboard'))
    
    # If logged in as a different role (student/admin), ask to logout first
    if 'user_id' in session and session.get('role') in ['admin', 'student']:
        flash("Please log out from your current role before accessing lecturer login.", "warning")
        return redirect(url_for('index'))
    
    if 'student_id' in session:
        flash("Please log out from your student account before accessing lecturer login.", "warning")
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check against User table with role='lecturer'
        user = User.query.filter_by(email=email, role='lecturer').first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = 'lecturer'
            flash('Login successful! Welcome back.', 'success')
            return redirect(url_for('lecturer.dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('lecturer_login.html')

@lecturer_bp.route('/register', methods=['GET', 'POST'])
def lecturer_register():
    """Handles lecturer account registration (URL: /lecturer/register)."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        department = request.form.get('department')
        staff_number = request.form.get('staff_number')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        terms = request.form.get('terms')

        # Validation
        if not all([name, email, department, staff_number, password, confirm_password]):
            flash('All fields marked with * are required.', 'error')
            return render_template('lecturer_register.html')

        if not validate_email(email):
            flash('Please enter a valid email address.', 'error')
            return render_template('lecturer_register.html')

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return render_template('lecturer_register.html')

        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return render_template('lecturer_register.html')

        if not terms:
            flash('You must agree to the Terms and Conditions to continue.', 'error')
            return render_template('lecturer_register.html')

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This email address is already registered. Please log in or use a different email.', 'error')
            return render_template('lecturer_register.html')

        # Check if staff number already exists
        existing_lecturer = Lecturer.query.filter_by(staff_number=staff_number).first()
        if existing_lecturer:
            flash('This staff number is already registered. Please contact support.', 'error')
            return render_template('lecturer_register.html')

        try:
            # Create new lecturer profile
            lecturer = Lecturer(
                staff_number=staff_number,
                name=name,
                email=email,
                department=department,
                phone=phone
            )
            db.session.add(lecturer)
            db.session.flush()  # Get the lecturer ID

            # Create new user account
            user = User(
                username=email.split('@')[0],  # Use part of email as username
                email=email,
                role=UserRole.LECTURER,
                lecturer_id=lecturer.id
            )
            user.set_password(password)
            db.session.add(user)
            
            db.session.commit()

            flash('Account created successfully! You can now log in with your email and password.', 'success')
            return redirect(url_for('lecturer.lecturer_login'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration. Please try again. {str(e)}', 'error')
            return render_template('lecturer_register.html')

    return render_template('lecturer_register.html')

@lecturer_bp.route('/dashboard')
@login_required
def dashboard():
    """Displays the lecturer's main dashboard (URL: /lecturer/dashboard)."""
    return render_template('dashboard.html', current_user=current_user, courses=MOCK_COURSES)

@lecturer_bp.route('/students')
@login_required
def students():
    """Displays a list of students, filterable by course (URL: /lecturer/students)."""
    selected_course_id = request.args.get('course_id', 'all')
    
    # Mock filtering logic
    filtered_students = MOCK_STUDENTS 
    
    return render_template(
        'students.html',
        current_user=current_user,
        students=filtered_students,
        courses_taught=MOCK_COURSES,
        selected_course_id=selected_course_id,
        all_students_count=ALL_STUDENTS_COUNT
    )

@lecturer_bp.route('/results')
@login_required
def results():
    """Page for entering and managing student results (URL: /lecturer/results)."""
    # NOTE: The template for this is still missing.
    return render_template('results.html', current_user=current_user)

@lecturer_bp.route('/profile')
@login_required
def profile():
    """Displays the lecturer's profile information (URL: /lecturer/profile)."""
    # NOTE: The template for this is still missing.
    return render_template('profile.html', current_user=current_user)

@lecturer_bp.route('/logout')
def logout():
    """Handles lecturer logout (URL: /lecturer/logout)."""
    global current_user
    if current_user.is_authenticated:
        current_user = MockUser(is_authenticated=False) # 'Log out' the mock user
        flash('You have been successfully logged out.', 'success')
    return redirect(url_for('lecturer.lecturer_login'))