# ---- app/routes/student_routes.py ----
import os
import io
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, 
    current_app, send_from_directory, session, make_response, send_file
)
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from app.models import db, Student, Payment, User, RegistrationSlip, Registration
from app.models import CourseEnrollment
from app.utils.helpers import allowed_file

from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import qr

# Blueprint definition
student_bp = Blueprint('student', __name__)

# ---------------- Helper Decorator ----------------
def student_required(f):
    """Decorator to ensure student is logged in before accessing a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('student.student_login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- Student Authentication ----------------
@student_bp.route('/login', methods=['GET', 'POST'])
def student_login():
    # If already logged in as student, redirect to dashboard
    if 'student_id' in session:
        return redirect(url_for('student.student_dashboard'))
    
    # If logged in as a different role (admin/lecturer), ask to logout first
    if 'user_id' in session and session.get('role') in ['admin', 'lecturer']:
        flash("Please log out from your current role before accessing student login.", "warning")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        student_number = request.form.get('student_number')
        password = request.form.get('password')

        user = User.query.filter_by(username=student_number, role='student').first()
        if user and user.check_password(password):
            session['student_id'] = user.student_id
            flash("Login successful!", "success")
            return redirect(url_for('student.student_dashboard'))
        else:
            flash("Invalid student number or password", "danger")

    return render_template('student/login.html')

@student_bp.route('/logout')
def student_logout():
    session.pop('student_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('student.student_login'))

# ---------------- Dashboard ----------------
@student_bp.route('/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('student_id')
    student = Student.query.get(student_id)
    payments = Payment.query.filter_by(student_id=student_id).order_by(Payment.submitted_date.desc()).all()
    
    # Check for approved payment and registration slip
    approved_payment = Payment.query.filter_by(
        student_id=student_id, 
        status='approved'
    ).first()
    
    # Check if registration slip exists for this student
    registration_slip = RegistrationSlip.query.filter_by(
        student_id=student_id
    ).first()
    
    return render_template('student/dashboard.html', 
                         payments=payments, 
                         student=student,
                         approved_payment=approved_payment,
                         registration_slip=registration_slip)

# ---------------- Payment Upload ----------------
@student_bp.route('/upload_payment', methods=['GET', 'POST'])
@student_required
def upload_payment():
    if request.method == 'POST':
        student_id = session.get('student_id')
        student = Student.query.get(student_id)
        
        if not student:
            flash('Student not found.', 'danger')
            return redirect(url_for('student.student_dashboard'))
            
        payment_slip = request.files.get('payment_slip')

        if not payment_slip:
            flash('Please upload a payment slip.', 'danger')
            return redirect(url_for('student.upload_payment'))

        if payment_slip and allowed_file(payment_slip.filename):
            filename = secure_filename(payment_slip.filename)
            # Add timestamp to make filename unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
                os.makedirs(current_app.config['UPLOAD_FOLDER'])

            payment_slip.save(upload_path)

            payment = Payment(
                slip_filename=filename, 
                student_id=student_id,
                status='pending',
                submitted_date=datetime.utcnow()
            )
            db.session.add(payment)
            db.session.commit()

            flash('Payment slip uploaded successfully! It is now pending approval.', 'success')
            return redirect(url_for('student.student_dashboard'))
        else:
            flash('Invalid file format. Please upload an image or PDF.', 'danger')
            return redirect(url_for('student.upload_payment'))

    return render_template('student/upload_payment.html')

@student_bp.route('/delete_payment/<int:payment_id>', methods=['POST'])
@student_required
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)

    if payment.student_id != session.get('student_id'):
        flash("You are not authorized to delete this payment.", "danger")
        return redirect(url_for('student.student_dashboard'))

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], payment.slip_filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(payment)
    db.session.commit()
    flash('Payment deleted successfully!', 'success')
    return redirect(url_for('student.student_dashboard'))

# ---------------- Registration Slip Routes (VIEW ONLY) ----------------
@student_bp.route('/registration_slip')
@student_required
def view_registration_slip():
    """Display registration slip for the logged-in student (VIEW ONLY)."""
    student_id = session.get('student_id')
    student = Student.query.get_or_404(student_id)
    
    # Check if registration slip exists for this student
    registration_slip = RegistrationSlip.query.filter_by(
        student_id=student_id
    ).first()
    
    if not registration_slip:
        flash("No registration slip found. Please contact administration.", "warning")
        return redirect(url_for('student.student_dashboard'))
    
    # Get the latest approved payment
    approved_payment = Payment.query.filter_by(
        student_id=student_id, 
        status='approved'
    ).order_by(Payment.submitted_date.desc()).first()

    return render_template(
        'student/registration_slip.html',
        student=student,
        slip=registration_slip,
        payment=approved_payment
    )

@student_bp.route('/registration_slip/download')
@student_required
def download_registration_slip():
    """Download registration slip as PDF (generated from admin)."""
    student_id = session.get('student_id')
    student = Student.query.get_or_404(student_id)
    
    # Check if registration slip exists for this student
    registration_slip = RegistrationSlip.query.filter_by(
        student_id=student_id
    ).first()
    
    if not registration_slip:
        flash("No registration slip found. Please contact administration.", "warning")
        return redirect(url_for('student.student_dashboard'))
    
    # Check if PDF file exists
    if not registration_slip.pdf_filename:
        flash("PDF version not available. Please contact administration.", "warning")
        return redirect(url_for('student.view_registration_slip'))
    
    # Serve the PDF file that was generated by admin
    return send_from_directory(
        current_app.config['REGISTRATION_SLIP_FOLDER'],
        registration_slip.pdf_filename,
        as_attachment=True,
        download_name=f"Registration_Slip_{student.student_number}.pdf"
    )

# ---------------- Timetable Download ----------------
@student_bp.route('/download_timetable')
@student_required
def download_timetable():
    """Generate and download timetable PDF"""
    student_id = session.get('student_id')
    student = Student.query.get(student_id)
    
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for('student.student_dashboard'))
    
    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,
        textColor=colors.HexColor('#1e3c72')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=12,
        textColor=colors.HexColor('#2a5298')
    )
    
    # Build story (content)
    story = []
    
    # University Header
    story.append(Paragraph("CAVENDISH UNIVERSITY", title_style))
    story.append(Paragraph("Lusaka, Zambia", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Document Title
    story.append(Paragraph("STUDENT TIMETABLE", title_style))
    story.append(Spacer(1, 30))
    
    # Student Information
    story.append(Paragraph("STUDENT INFORMATION", heading_style))
    
    student_data = [
        ["Student Name:", student.name],
        ["Student ID:", student.student_number],
        ["Academic Year:", "2024/2025"],
        ["Semester:", "FIRST SEMESTER"],
        ["Date Generated:", datetime.now().strftime('%d-%m-%Y')]
    ]
    
    # Create table for student info
    normal_style = styles['Normal']
    table_data = []
    for label, value in student_data:
        table_data.append([Paragraph(f"<b>{label}</b>", normal_style), Paragraph(value, normal_style)])
    
    student_table = Table(table_data, colWidths=[2*inch, 3*inch])
    student_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(student_table)
    story.append(Spacer(1, 30))
    
    # Timetable Data
    story.append(Paragraph("CLASS SCHEDULE", heading_style))
    
    # Sample timetable data - replace with actual data from your database
    timetable_data = [
        ['Day', 'Time', 'Course Code', 'Course Name', 'Venue', 'Lecturer'],
        ['Monday', '08:00-10:00', 'CS101', 'Introduction to Programming', 'LT1', 'Dr. Smith'],
        ['Monday', '10:00-12:00', 'MATH101', 'Calculus I', 'Room 201', 'Prof. Johnson'],
        ['Tuesday', '09:00-11:00', 'PHY101', 'Physics I', 'Lab 3', 'Dr. Brown'],
        ['Wednesday', '14:00-16:00', 'CS102', 'Data Structures', 'LT2', 'Dr. Davis'],
        ['Thursday', '11:00-13:00', 'STAT101', 'Statistics', 'Room 105', 'Prof. Wilson'],
        ['Friday', '10:00-12:00', 'CS103', 'Algorithms', 'LT1', 'Dr. Taylor'],
    ]
    
    # Create timetable table
    timetable_table = Table(timetable_data, colWidths=[0.8*inch, 1.2*inch, 1*inch, 2*inch, 0.8*inch, 1.2*inch])
    timetable_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(timetable_table)
    story.append(Spacer(1, 30))
    
    # Important Notes
    story.append(Paragraph("IMPORTANT NOTES", heading_style))
    notes = [
        "1. This timetable is subject to changes. Please check regularly for updates.",
        "2. Students are expected to be punctual for all classes.",
        "3. Any timetable conflicts should be reported to the academic office immediately.",
        "4. Laboratory sessions will be scheduled separately.",
    ]
    
    for note in notes:
        story.append(Paragraph(note, normal_style))
        story.append(Spacer(1, 5))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    # Create response
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=timetable_{student.student_number}.pdf'
    
    return response


# ---------------- Docket Routes ----------------
def _get_tuition_total(student: Student) -> float:
    """Return tuition total for a student. Default fallback used if not set."""
    # For now, use a default tuition; in future this should come from program or admin settings
    default_tuition = 1000.0
    return getattr(student, 'tuition_total', default_tuition) or default_tuition


def _paid_percentage(student_id: int) -> float:
    """Compute percentage of tuition paid based on approved payments."""
    student = Student.query.get(student_id)
    if not student:
        return 0.0
    tuition = _get_tuition_total(student)
    approved_payments = Payment.query.filter_by(student_id=student_id, status='approved').all()
    total_paid = sum(p.amount or 0.0 for p in approved_payments)
    try:
        return min(100.0, (total_paid / tuition) * 100.0)
    except Exception:
        return 0.0


@student_bp.route('/docket')
@student_required
def docket():
    """Display docket availability based on payment thresholds."""
    student_id = session.get('student_id')
    student = Student.query.get_or_404(student_id)
    percent = _paid_percentage(student_id)

    # thresholds
    thresholds = {
        'CAT1': 50.0,
        'CAT2': 75.0,
        'FINAL': 100.0,
    }

    availability = {k: (percent >= v) for k, v in thresholds.items()}

    return render_template('student/docket.html', student=student, percent=percent, availability=availability)


@student_bp.route('/docket/download/<assessment>')
@student_required
def docket_download(assessment):
    """Download docket in Word-friendly HTML (served as .doc) if threshold met; else deny."""
    student_id = session.get('student_id')
    student = Student.query.get_or_404(student_id)
    percent = _paid_percentage(student_id)

    thresholds = {'CAT1':50.0, 'CAT2':75.0, 'FINAL':100.0}
    required = thresholds.get(assessment.upper())
    if required is None:
        flash('Invalid assessment specified.', 'danger')
        return redirect(url_for('student.docket'))

    if percent < required:
        flash(f'You must have paid at least {required}% of tuition to download this docket.', 'warning')
        return redirect(url_for('student.docket'))

    # Build a simple HTML that Word can open
    html = f"""
    <html>
    <head><meta charset='utf-8'><title>Docket - {assessment}</title></head>
    <body>
    <h1>Docket - {assessment}</h1>
    <p>Student: {student.name} ({student.student_number})</p>
    <p>Assessment: {assessment}</p>
    <p>Issued: {datetime.utcnow().strftime('%Y-%m-%d')}</p>
    <hr/>
    <p>This docket is issued for printing purposes. Verify your details before printing.</p>
    </body></html>
    """

    response = make_response(html)
    response.headers['Content-Type'] = 'application/msword'
    response.headers['Content-Disposition'] = f'attachment; filename=Docket_{assessment}_{student.student_number}.doc'
    return response


@student_bp.route('/docket/print/<assessment>')
@student_required
def docket_print(assessment):
    """Generate a printable PDF containing a QR code representing the docket link."""
    student_id = session.get('student_id')
    student = Student.query.get_or_404(student_id)
    percent = _paid_percentage(student_id)

    thresholds = {'CAT1':50.0, 'CAT2':75.0, 'FINAL':100.0}
    required = thresholds.get(assessment.upper())
    if required is None:
        flash('Invalid assessment specified.', 'danger')
        return redirect(url_for('student.docket'))

    if percent < required:
        flash(f'You must have paid at least {required}% of tuition to print this docket.', 'warning')
        return redirect(url_for('student.docket'))

    # Create a PDF with QR code using reportlab
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Docket - {assessment}", styles['Title']))
    story.append(Paragraph(f"Student: {student.name} ({student.student_number})", styles['Normal']))
    story.append(Spacer(1, 12))

    # Create QR drawing that encodes a URL to view the docket online
    docket_url = url_for('student.docket', _external=True) + f"#assessment={assessment}"
    qr_code = qr.QrCodeWidget(docket_url)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    d = Drawing(150, 150)
    d.add(qr_code)
    story.append(d)
    story.append(Spacer(1, 12))
    story.append(Paragraph('Scan this QR code to verify docket details online.', styles['Normal']))

    doc.build(story)
    buf.seek(0)
    return send_file(buf, mimetype='application/pdf', download_name=f'Docket_{assessment}_{student.student_number}.pdf', as_attachment=True)


# ---------------- Student Results (session-based) ----------------
@student_bp.route('/results')
@student_required
def student_results():
    """Student-facing results view using session-based auth."""
    student_id = session.get('student_id')
    student = Student.query.get_or_404(student_id)

    # Payment percent controls visibility
    percent = _paid_percentage(student_id)

    # Require at least 50% payment to view results (adjustable rule)
    can_view = percent >= 50.0

    enrollments = []
    results = []
    average_marks = 0.0
    if can_view:
        enrollments = CourseEnrollment.query.filter_by(student_id=student_id).order_by(
            CourseEnrollment.academic_year.desc(), CourseEnrollment.semester.desc()
        ).all()

        # Build results list for template and compute average marks if 'marks' attribute exists
        marks_list = []
        for e in enrollments:
            course = getattr(e, 'course', None)
            course_code = course.code if course else ''
            course_name = course.title if course else ''
            grade = getattr(e, 'grade', None) or ''
            marks = getattr(e, 'marks', None) or ''
            results.append({
                'course_code': course_code,
                'course_name': course_name,
                'grade': grade,
                'marks': marks,
                'semester': e.semester,
                'academic_year': e.academic_year,
            })
            try:
                if isinstance(marks, (int, float)):
                    marks_list.append(float(marks))
            except Exception:
                pass

        if marks_list:
            average_marks = sum(marks_list) / len(marks_list)

    # Pass variables expected by the student results template
    return render_template('student/results.html', results=results, average_marks=average_marks, student=student, can_view=can_view)

# ---------------- Student Registration ----------------
@student_bp.route('/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        student_number = request.form.get('student_number')
        name = request.form.get('name')
        email = request.form.get('email')
        program = request.form.get('program')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([student_number, name, password, confirm_password]):
            flash("All fields are required.", "danger")
            return redirect(url_for('student.student_register'))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('student.student_register'))

        student = Student.query.filter_by(student_number=student_number).first()
        if not student:
            student = Student(student_number=student_number, name=name, email=email or None, program=program or None)
            db.session.add(student)
            db.session.commit()
        else:
            # update optional fields if provided
            if email:
                student.email = email
            if program:
                student.program = program
            db.session.add(student)
            db.session.commit()

        user = User.query.filter_by(student_id=student.id, role='student').first()
        if user:
            flash("This student ID is already registered.", "danger")
            return redirect(url_for('student.student_register'))

        # Ensure email uniqueness
        provided_email = email or f"{student_number}@cavendish.ac.zm"
        existing_email = User.query.filter_by(email=provided_email).first()
        if existing_email:
            flash("The provided email is already in use.", "danger")
            return redirect(url_for('student.student_register'))

        user = User(
            username=student_number,
            email=provided_email,
            role="student",
            student_id=student.id
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("✅ Registration successful! You can now log in.", "success")
        return redirect(url_for('student.student_login'))

    return render_template('student/register.html')


# ---------------- Semester Registration (Student) ----------------
@student_bp.route('/semester_register', methods=['GET', 'POST'])
@student_required
def semester_register():
    """Allow a logged-in student to register for the next semester and upload proof of payment."""
    student_id = session.get('student_id')
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        academic_year = request.form.get('academic_year')
        semester = request.form.get('semester')
        program = request.form.get('program')
        mode_of_study = request.form.get('mode_of_study')
        is_returning = True if request.form.get('is_returning') else False
        modules = request.form.get('modules')
        amount = request.form.get('amount')

        proof = request.files.get('proof')
        if not all([academic_year, semester, program, modules, proof]):
            flash('All fields including proof of payment are required.', 'danger')
            return redirect(url_for('student.semester_register'))

        if not allowed_file(proof.filename):
            flash('Invalid file type for proof. Use JPG/PNG/PDF.', 'danger')
            return redirect(url_for('student.semester_register'))

        filename = secure_filename(proof.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reg_{student.student_number}_{timestamp}_{filename}"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])
        proof.save(upload_path)

        # Create Registration record
        registration = Registration(
            academic_year=academic_year,
            semester=semester,
            is_registered=False,
            student_id=student_id,
            program=program,
            mode_of_study=mode_of_study,
            modules=modules,
            is_returning=is_returning
        )
        db.session.add(registration)
        db.session.commit()

        # Save a payment record for this proof (pending)
        try:
            amt = float(amount) if amount else None
        except Exception:
            amt = None

        payment = Payment(
            slip_filename=filename,
            student_id=student_id,
            status='pending',
            submitted_date=datetime.utcnow(),
            amount=amt,
            description=f"Registration payment for {academic_year} {semester} - {program}"
        )
        db.session.add(payment)
        db.session.commit()

        flash('Registration submitted and proof uploaded. Awaiting admin confirmation.', 'success')
        return redirect(url_for('student.student_dashboard'))

    # GET - render form
    return render_template('student/semester_register.html', student=student)

# ---------------- Serve Uploaded Files ----------------
@student_bp.route("/uploads/<filename>")
@student_required
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)