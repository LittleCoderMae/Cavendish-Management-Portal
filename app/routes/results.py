#app/routes/results.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import db, User, UserRole, Student, Course, CourseEnrollment, Lecturer

results_bp = Blueprint('results', __name__)

# ------------------------------------------------------------
# LECTURER & ADMIN GRADE MANAGEMENT (Using CourseEnrollment)
# ------------------------------------------------------------

@results_bp.route('/publish', methods=['POST'])
@login_required
def publish_grade():
    """
    Lecturer/Admin submits or updates a grade for a student's course enrollment.
    Requires: student_number, course_code, grade, academic_year, semester.
    """
    # FIXED: Added is_admin() method check
    if not current_user.is_lecturer() and current_user.role != UserRole.ADMIN:
        return jsonify({'success': False, 'message': 'Access denied.'}), 403
    
    if current_user.is_lecturer() and not current_user.lecturer_profile:
        return jsonify({'success': False, 'message': 'Lecturer profile not linked.'}), 400

    try:
        data = request.get_json()
        # Data needed for lookup
        student_number = data.get('student_number')
        course_code = data.get('course_code')
        grade = data.get('grade')
        academic_year = data.get('academic_year')
        semester = data.get('semester')

        # 1. Look up student and course objects
        student = Student.query.filter_by(student_number=student_number).first()
        course = Course.query.filter_by(code=course_code).first()
        
        if not student or not course:
            return jsonify({'success': False, 'message': 'Invalid Student or Course details provided.'}), 404

        # 2. Security check: Lecturer must teach the course
        if current_user.is_lecturer() and course.primary_lecturer_id != current_user.lecturer_profile.id:
            return jsonify({'success': False, 'message': 'Authorization required for this course.'}), 403

        # 3. Find the specific enrollment record
        enrollment = CourseEnrollment.query.filter_by(
            student_id=student.id,
            course_id=course.id,
            academic_year=academic_year,
            semester=semester
        ).first()
        
        if not enrollment:
            return jsonify({'success': False, 'message': 'Enrollment record not found for this period.'}), 404

        # 4. Update the grade
        enrollment.grade = grade
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Grade {grade} published for {student_number} in {course_code}.'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error publishing grade: {str(e)}'}), 500

# FIXED: Added missing student_id parameter to route
@results_bp.route('/view/<int:student_id>')
@login_required
def view_student_results(student_id):
    """View all enrollment results for a specific student."""
    # FIXED: Corrected admin check
    if not current_user.is_lecturer() and current_user.role != UserRole.ADMIN:
        flash('Access denied.', 'error')
        return redirect(url_for('auth.login'))

    student = Student.query.get(student_id)
    if not student:
        flash('Student not found.', 'error')
        # FIXED: Redirect to appropriate dashboard based on role
        if current_user.is_lecturer():
            return redirect(url_for('lecturer.dashboard'))
        else:
            return redirect(url_for('admin.dashboard'))

    # Query enrollments for that student
    student_enrollments = CourseEnrollment.query.filter_by(student_id=student_id).order_by(
        CourseEnrollment.academic_year.desc(),
        CourseEnrollment.semester.desc()
    ).all()

    return render_template('lecturer/student_results_view.html', 
                         enrollments=student_enrollments, 
                         student=student)

@results_bp.route('/manage')
@login_required
def manage_results():
    """Management view for all course enrollments (grades)."""
    if not current_user.is_lecturer() and current_user.role != UserRole.ADMIN:
        flash('Access denied.', 'error')
        return redirect(url_for('auth.login'))

    # Get all students for search/dropdown
    all_students = Student.query.all()

    # Base query joining necessary tables
    enrollments_query = CourseEnrollment.query.join(Student).join(Course)

    if current_user.is_lecturer():
        # Lecturers only see enrollments for courses they teach
        lecturer_id = current_user.lecturer_profile.id if current_user.lecturer_profile else -1
        enrollments_query = enrollments_query.filter(Course.primary_lecturer_id == lecturer_id)

    # Order for display
    results = enrollments_query.order_by(
        CourseEnrollment.academic_year.desc(),
        Student.student_number.asc()
    ).all()

    return render_template('admin/results_management.html', 
                         students=all_students, 
                         enrollments=results)

@results_bp.route('/bulk-upload', methods=['POST'])
@login_required
def bulk_upload():
    """Placeholder for CSV/Excel bulk upload of grades."""
    if current_user.role != UserRole.ADMIN:
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})

        # TODO: Implement robust CSV/Excel file parsing and batch insert/update into CourseEnrollment
        return jsonify({'success': True, 'message': 'Results uploaded successfully (Parsing logic placeholder).'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error uploading file: {str(e)}'}), 500

# ------------------------------------------------------------
# STUDENT RESULTS VIEW
# ------------------------------------------------------------

@results_bp.route('/my-results')
@login_required
def my_results():
    """Student view of their own results."""
    if not current_user.is_student() or not current_user.student_profile:
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('auth.login'))

    student_id = current_user.student_profile.id
    student_enrollments = CourseEnrollment.query.filter_by(student_id=student_id).order_by(
        CourseEnrollment.academic_year.desc(),
        CourseEnrollment.semester.desc()
    ).all()

    # Calculate grade distribution (simplified stats)
    total_courses = len(student_enrollments)
    grade_count = {}
    for enrollment in student_enrollments:
        grade = enrollment.grade or 'N/A'
        grade_count[grade] = grade_count.get(grade, 0) + 1

    return render_template('student/results.html', 
                         enrollments=student_enrollments, 
                         total_courses=total_courses, 
                         grade_count=grade_count)

# ------------------------------------------------------------
# API ENDPOINTS
# ------------------------------------------------------------

# FIXED: Added missing student_id parameter to route
@results_bp.route('/api/student/<int:student_id>')
@login_required
def get_student_results_api(student_id):
    """API endpoint to get results (enrollments) for a student."""
    if not current_user.is_lecturer() and current_user.role != UserRole.ADMIN:
        return jsonify({'error': 'Access denied'}), 403

    # Query CourseEnrollment and join with Course
    enrollments = CourseEnrollment.query.filter_by(student_id=student_id).join(Course).all()
    
    results_data = [{
        'id': enrollment.id,
        'course_code': enrollment.course.code,
        'course_name': enrollment.course.title,
        'grade': enrollment.grade,
        'semester': enrollment.semester,
        'academic_year': enrollment.academic_year
    } for enrollment in enrollments]

    return jsonify({'results': results_data})

# FIXED: Added missing enrollment_id parameter to route
@results_bp.route('/api/delete/<int:enrollment_id>', methods=['DELETE'])
@login_required
def delete_result_api(enrollment_id):
    """API endpoint to delete a specific enrollment record (grade)."""
    if current_user.role != UserRole.ADMIN:
        return jsonify({'error': 'Access denied. Admins only.'}), 403

    try:
        enrollment = CourseEnrollment.query.get(enrollment_id)
        if not enrollment:
            return jsonify({'error': 'Enrollment record not found'}), 404
        
        db.session.delete(enrollment)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Enrollment record deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting enrollment: {str(e)}'}), 500

# ------------------------------------------------------------
# RESULTS ANALYSIS
# ------------------------------------------------------------

@results_bp.route('/analysis')
@login_required
def results_analysis():
    """General analysis of enrollment/grade data."""
    if not current_user.is_lecturer() and current_user.role != UserRole.ADMIN:
        flash('Access denied.', 'error')
        return redirect(url_for('auth.login'))

    # Get results statistics
    total_enrollments = CourseEnrollment.query.count()
    distinct_students = db.session.query(CourseEnrollment.student_id).distinct().count()
    distinct_courses = db.session.query(CourseEnrollment.course_id).distinct().count()

    # Grade distribution
    grade_distribution = db.session.query(
        CourseEnrollment.grade,
        db.func.count(CourseEnrollment.id)
    ).filter(CourseEnrollment.grade.isnot(None)).group_by(CourseEnrollment.grade).all()

    # Enrollment count per course
    course_enrollment_counts = db.session.query(
        Course.code,
        Course.title,
        db.func.count(CourseEnrollment.id).label('enrollment_count')
    ).select_from(CourseEnrollment).join(Course).group_by(Course.code, Course.title).all()

    return render_template('admin/results_analysis.html',
                         total_enrollments=total_enrollments,
                         distinct_students=distinct_students,
                         distinct_courses=distinct_courses,
                         grade_distribution=grade_distribution,
                         course_enrollment_counts=course_enrollment_counts)