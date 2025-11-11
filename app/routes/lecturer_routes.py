from flask import Blueprint, render_template, redirect, url_for, flash, request
from functools import wraps

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
lecturer_bp = Blueprint('lecturer', __name__, url_prefix='/lecturer', template_folder='templates/lecturer')

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
    global current_user
    if current_user.is_authenticated:
        return redirect(url_for('lecturer.dashboard'))

    if request.method == 'POST':
        staff_id = request.form.get('staff_id')
        password = request.form.get('password')
        
        # Mock Login Check (Staff ID: LCT-1001, Password: password)
        if staff_id == 'LCT-1001' and password == 'password': 
            current_user = MockUser(is_authenticated=True)
            flash('Login successful! Welcome back, Dr. Vance.', 'success')
            return redirect(url_for('lecturer.dashboard'))
        else:
            flash('Invalid Staff ID or password.', 'error')

    return render_template('login.html')

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