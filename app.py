import os
from datetime import datetime, date, time
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from models import db, User, Course, Examination, Rubric, Slot, Booking, Evaluation, EvaluationScore

def create_app():
    app = Flask(__name__)
    
    # App configuration
    app.config['SECRET_KEY'] = 'mad1-emp-portal-secret-key-2026'
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'emp.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Ensure instance directory exists
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)

    db.init_app(app)

    # ----------------------------------------------------
    # Helper Decorators for Role-Based Access Control
    # ----------------------------------------------------
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first to access this page.', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    def role_required(*allowed_roles):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if 'user_id' not in session:
                    flash('Please log in first.', 'warning')
                    return redirect(url_for('login'))
                if session.get('role') not in allowed_roles:
                    flash('You do not have permission to access this page.', 'danger')
                    return redirect(url_for('dashboard_redirect'))
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    # ----------------------------------------------------
    # Public & Auth Routes
    # ----------------------------------------------------
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/dashboard')
    @login_required
    def dashboard_redirect():
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'examiner':
            return redirect(url_for('examiner_dashboard'))
        elif role == 'student':
            return redirect(url_for('student_dashboard'))
        return redirect(url_for('index'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'user_id' in session:
            return redirect(url_for('dashboard_redirect'))

        if request.method == 'POST':
            login_id = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            # Allow login using either username or email
            user = User.query.filter((User.username == login_id) | (User.email == login_id)).first()

            if user and user.check_password(password):
                # Check examiner approval status
                if user.role == 'examiner' and user.status == 'pending':
                    flash('Your examiner registration is pending Admin approval. Please wait for an administrator to approve your account.', 'warning')
                    return render_template('login.html')
                
                if user.status == 'deactivated':
                    flash('Your account has been deactivated. Please contact the administrator.', 'danger')
                    return render_template('login.html')

                # Set session variables
                session['user_id'] = user.id
                session['username'] = user.username
                session['full_name'] = user.full_name
                session['role'] = user.role

                flash(f'Welcome back, {user.full_name}!', 'success')
                return redirect(url_for('dashboard_redirect'))
            else:
                flash('Invalid username/email or password. Please try again.', 'danger')

        return render_template('login.html')

    @app.route('/register/student', methods=['GET', 'POST'])
    def register_student():
        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            roll_no = request.form.get('roll_no', '').strip()
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            department = request.form.get('department', '').strip()
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('register_student.html')

            if len(password) < 6:
                flash('Password must be at least 6 characters long.', 'danger')
                return render_template('register_student.html')

            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                flash('Username is already taken. Please choose another.', 'danger')
                return render_template('register_student.html')

            if User.query.filter_by(email=email).first():
                flash('Email is already registered. Please login or use a different email.', 'danger')
                return render_template('register_student.html')

            # Create student user
            student = User(
                username=username,
                email=email,
                role='student',
                status='active',
                full_name=full_name,
                roll_no=roll_no,
                department=department,
                phone=phone
            )
            student.set_password(password)
            db.session.add(student)
            db.session.commit()

            flash('Registration successful! You can now log in to your student account.', 'success')
            return redirect(url_for('login'))

        return render_template('register_student.html')

    @app.route('/register/examiner', methods=['GET', 'POST'])
    def register_examiner():
        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            department = request.form.get('department', '').strip()
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('register_examiner.html')

            if len(password) < 6:
                flash('Password must be at least 6 characters long.', 'danger')
                return render_template('register_examiner.html')

            if User.query.filter_by(username=username).first():
                flash('Username is already taken. Please choose another.', 'danger')
                return render_template('register_examiner.html')

            if User.query.filter_by(email=email).first():
                flash('Email is already registered.', 'danger')
                return render_template('register_examiner.html')

            # Create examiner user (status is pending until admin approves)
            examiner = User(
                username=username,
                email=email,
                role='examiner',
                status='pending',
                full_name=full_name,
                department=department,
                phone=phone
            )
            examiner.set_password(password)
            db.session.add(examiner)
            db.session.commit()

            flash('Registration submitted successfully! Your account requires Admin approval before you can log in.', 'info')
            return redirect(url_for('login'))

        return render_template('register_examiner.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('index'))

    # ----------------------------------------------------
    # Admin Routes
    # ----------------------------------------------------
    @app.route('/admin/dashboard')
    @login_required
    @role_required('admin')
    def admin_dashboard():
        # Counts for dashboard metrics
        courses_count = Course.query.count()
        exams_count = Examination.query.count()
        examiners_count = User.query.filter_by(role='examiner').count()
        pending_examiners_count = User.query.filter_by(role='examiner', status='pending').count()
        students_count = User.query.filter_by(role='student').count()
        slots_count = Slot.query.count()
        bookings_count = Booking.query.count()

        recent_exams = Examination.query.order_by(Examination.created_at.desc()).limit(5).all()
        recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
        pending_examiners = User.query.filter_by(role='examiner', status='pending').all()

        return render_template('admin/dashboard.html',
                               courses_count=courses_count,
                               exams_count=exams_count,
                               examiners_count=examiners_count,
                               pending_examiners_count=pending_examiners_count,
                               students_count=students_count,
                               slots_count=slots_count,
                               bookings_count=bookings_count,
                               recent_exams=recent_exams,
                               recent_bookings=recent_bookings,
                               pending_examiners=pending_examiners)

    @app.route('/admin/courses')
    @login_required
    @role_required('admin')
    def admin_courses():
        courses = Course.query.order_by(Course.course_code.asc()).all()
        return render_template('admin/courses.html', courses=courses)

    @app.route('/admin/courses/create', methods=['GET', 'POST'])
    @login_required
    @role_required('admin')
    def admin_create_course():
        if request.method == 'POST':
            code = request.form.get('course_code', '').strip().upper()
            name = request.form.get('course_name', '').strip()
            description = request.form.get('description', '').strip()
            status = request.form.get('status', 'Active')

            if Course.query.filter_by(course_code=code).first():
                flash(f'Course code {code} already exists!', 'danger')
                return render_template('admin/course_form.html', action='Create', course=None)

            new_course = Course(
                course_code=code,
                course_name=name,
                description=description,
                status=status
            )
            db.session.add(new_course)
            db.session.commit()
            flash(f'Course "{name}" created successfully.', 'success')
            return redirect(url_for('admin_courses'))

        return render_template('admin/course_form.html', action='Create', course=None)

    @app.route('/admin/courses/edit/<int:course_id>', methods=['GET', 'POST'])
    @login_required
    @role_required('admin')
    def admin_edit_course(course_id):
        course = Course.query.get_or_404(course_id)
        if request.method == 'POST':
            code = request.form.get('course_code', '').strip().upper()
            name = request.form.get('course_name', '').strip()
            description = request.form.get('description', '').strip()
            status = request.form.get('status', 'Active')

            # Check duplicate code if changed
            existing = Course.query.filter(Course.course_code == code, Course.id != course.id).first()
            if existing:
                flash(f'Course code {code} is already used by another course.', 'danger')
                return render_template('admin/course_form.html', action='Edit', course=course)

            course.course_code = code
            course.course_name = name
            course.description = description
            course.status = status
            db.session.commit()
            flash('Course updated successfully.', 'success')
            return redirect(url_for('admin_courses'))

        return render_template('admin/course_form.html', action='Edit', course=course)

    @app.route('/admin/courses/delete/<int:course_id>', methods=['POST'])
    @login_required
    @role_required('admin')
    def admin_delete_course(course_id):
        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        flash('Course and associated examinations deleted successfully.', 'info')
        return redirect(url_for('admin_courses'))

    @app.route('/admin/exams')
    @login_required
    @role_required('admin')
    def admin_exams():
        exams = Examination.query.order_by(Examination.created_at.desc()).all()
        return render_template('admin/exams.html', exams=exams)

    @app.route('/admin/exams/create', methods=['GET', 'POST'])
    @login_required
    @role_required('admin')
    def admin_create_exam():
        courses = Course.query.filter_by(status='Active').all()
        if request.method == 'POST':
            try:
                course_id = int(request.form.get('course_id'))
                exam_name = request.form.get('exam_name', '').strip()
                exam_type = request.form.get('exam_type', 'Viva')
                duration = int(request.form.get('duration', 30))
                max_marks = int(request.form.get('max_marks', 100))
                
                # Parse date strings to date objects
                slot_creation_start = datetime.strptime(request.form.get('slot_creation_start_date'), '%Y-%m-%d').date()
                slot_creation_end = datetime.strptime(request.form.get('slot_creation_end_date'), '%Y-%m-%d').date()
                slot_booking_start = datetime.strptime(request.form.get('slot_booking_start_date'), '%Y-%m-%d').date()
                slot_booking_end = datetime.strptime(request.form.get('slot_booking_end_date'), '%Y-%m-%d').date()
                
                status = request.form.get('status', 'Draft')
                instructions = request.form.get('instructions', '').strip()

                new_exam = Examination(
                    course_id=course_id,
                    exam_name=exam_name,
                    exam_type=exam_type,
                    duration=duration,
                    max_marks=max_marks,
                    slot_creation_start_date=slot_creation_start,
                    slot_creation_end_date=slot_creation_end,
                    slot_booking_start_date=slot_booking_start,
                    slot_booking_end_date=slot_booking_end,
                    status=status,
                    instructions=instructions
                )
                db.session.add(new_exam)
                db.session.commit()
                flash(f'Examination "{exam_name}" created successfully.', 'success')
                return redirect(url_for('admin_exams'))
            except Exception as e:
                flash(f'Error creating examination: {str(e)}', 'danger')

        return render_template('admin/exam_form.html', action='Create', exam=None, courses=courses)

    @app.route('/admin/exams/edit/<int:exam_id>', methods=['GET', 'POST'])
    @login_required
    @role_required('admin')
    def admin_edit_exam(exam_id):
        exam = Examination.query.get_or_404(exam_id)
        courses = Course.query.filter_by(status='Active').all()

        if request.method == 'POST':
            try:
                exam.course_id = int(request.form.get('course_id'))
                exam.exam_name = request.form.get('exam_name', '').strip()
                exam.exam_type = request.form.get('exam_type', 'Viva')
                exam.duration = int(request.form.get('duration', 30))
                exam.max_marks = int(request.form.get('max_marks', 100))
                
                exam.slot_creation_start_date = datetime.strptime(request.form.get('slot_creation_start_date'), '%Y-%m-%d').date()
                exam.slot_creation_end_date = datetime.strptime(request.form.get('slot_creation_end_date'), '%Y-%m-%d').date()
                exam.slot_booking_start_date = datetime.strptime(request.form.get('slot_booking_start_date'), '%Y-%m-%d').date()
                exam.slot_booking_end_date = datetime.strptime(request.form.get('slot_booking_end_date'), '%Y-%m-%d').date()
                
                exam.status = request.form.get('status', 'Draft')
                exam.instructions = request.form.get('instructions', '').strip()

                db.session.commit()
                flash('Examination updated successfully.', 'success')
                return redirect(url_for('admin_exams'))
            except Exception as e:
                flash(f'Error updating examination: {str(e)}', 'danger')

        return render_template('admin/exam_form.html', action='Edit', exam=exam, courses=courses)

    @app.route('/admin/exams/delete/<int:exam_id>', methods=['POST'])
    @login_required
    @role_required('admin')
    def admin_delete_exam(exam_id):
        exam = Examination.query.get_or_404(exam_id)
        db.session.delete(exam)
        db.session.commit()
        flash('Examination deleted successfully.', 'info')
        return redirect(url_for('admin_exams'))

    @app.route('/admin/exams/<int:exam_id>/status', methods=['POST'])
    @login_required
    @role_required('admin')
    def admin_change_exam_status(exam_id):
        exam = Examination.query.get_or_404(exam_id)
        new_status = request.form.get('status')
        if new_status in ['Draft', 'Slot Creation', 'Booking Open', 'Closed', 'Completed']:
            exam.status = new_status
            db.session.commit()
            flash(f'Status for "{exam.exam_name}" updated to {new_status}.', 'success')
        return redirect(url_for('admin_exams'))

    # Rubrics Management
    @app.route('/admin/exams/<int:exam_id>/rubrics')
    @login_required
    @role_required('admin')
    def admin_exam_rubrics(exam_id):
        exam = Examination.query.get_or_404(exam_id)
        return render_template('admin/rubrics.html', exam=exam)

    @app.route('/admin/exams/<int:exam_id>/rubrics/create', methods=['POST'])
    @login_required
    @role_required('admin')
    def admin_create_rubric(exam_id):
        exam = Examination.query.get_or_404(exam_id)
        criterion_name = request.form.get('criterion_name', '').strip()
        max_marks = float(request.form.get('max_marks', 10))
        weightage = float(request.form.get('weightage', 1.0))
        description = request.form.get('description', '').strip()

        rubric = Rubric(
            examination_id=exam.id,
            criterion_name=criterion_name,
            max_marks=max_marks,
            weightage=weightage,
            description=description
        )
        db.session.add(rubric)
        db.session.commit()
        flash(f'Rubric criterion "{criterion_name}" added.', 'success')
        return redirect(url_for('admin_exam_rubrics', exam_id=exam.id))

    @app.route('/admin/rubrics/delete/<int:rubric_id>', methods=['POST'])
    @login_required
    @role_required('admin')
    def admin_delete_rubric(rubric_id):
        rubric = Rubric.query.get_or_404(rubric_id)
        exam_id = rubric.examination_id
        db.session.delete(rubric)
        db.session.commit()
        flash('Rubric criterion deleted.', 'info')
        return redirect(url_for('admin_exam_rubrics', exam_id=exam_id))

    # Examiners Management
    @app.route('/admin/examiners')
    @login_required
    @role_required('admin')
    def admin_examiners():
        examiners = User.query.filter_by(role='examiner').all()
        return render_template('admin/examiners.html', examiners=examiners)

    @app.route('/admin/examiners/<int:user_id>/status/<string:action>', methods=['POST'])
    @login_required
    @role_required('admin')
    def admin_examiner_status(user_id, action):
        examiner = User.query.filter_by(id=user_id, role='examiner').first_or_404()
        if action == 'approve':
            examiner.status = 'active'
            flash(f'Examiner {examiner.full_name} has been approved.', 'success')
        elif action == 'deactivate':
            examiner.status = 'deactivated'
            flash(f'Examiner {examiner.full_name} has been deactivated.', 'warning')
        elif action == 'activate':
            examiner.status = 'active'
            flash(f'Examiner {examiner.full_name} has been activated.', 'success')
        db.session.commit()
        return redirect(url_for('admin_examiners'))

    # Students Management
    @app.route('/admin/students')
    @login_required
    @role_required('admin')
    def admin_students():
        students = User.query.filter_by(role='student').order_by(User.full_name.asc()).all()
        return render_template('admin/students.html', students=students)

    # Slots Management & Reassignment
    @app.route('/admin/slots')
    @login_required
    @role_required('admin')
    def admin_slots():
        slots = Slot.query.order_by(Slot.date.desc(), Slot.start_time.asc()).all()
        active_examiners = User.query.filter_by(role='examiner', status='active').all()
        return render_template('admin/slots.html', slots=slots, active_examiners=active_examiners)

    @app.route('/admin/slots/<int:slot_id>/reassign', methods=['POST'])
    @login_required
    @role_required('admin')
    def admin_reassign_slot(slot_id):
        slot = Slot.query.get_or_404(slot_id)
        new_examiner_id = int(request.form.get('examiner_id'))
        new_examiner = User.query.filter_by(id=new_examiner_id, role='examiner').first_or_404()
        
        slot.examiner_id = new_examiner.id
        db.session.commit()
        flash(f'Slot reassigned to examiner {new_examiner.full_name}.', 'success')
        return redirect(url_for('admin_slots'))

    # Bookings Management & Rescheduling
    @app.route('/admin/bookings')
    @login_required
    @role_required('admin')
    def admin_bookings():
        bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
        return render_template('admin/bookings.html', bookings=bookings)

    @app.route('/admin/bookings/<int:booking_id>/reschedule', methods=['POST'])
    @login_required
    @role_required('admin')
    def admin_reschedule_booking(booking_id):
        booking = Booking.query.get_or_404(booking_id)
        new_slot_id = int(request.form.get('new_slot_id'))
        new_slot = Slot.query.get_or_404(new_slot_id)

        if new_slot.available_seats <= 0:
            flash('Target slot is already full. Cannot reschedule.', 'danger')
            return redirect(url_for('admin_bookings'))

        old_slot = booking.slot
        # Decrement old slot count if booking was active
        if booking.status == 'Booked':
            old_slot.booked_seats = max(0, old_slot.booked_seats - 1)
            old_slot.update_status()

        # Assign new slot and increment
        booking.slot_id = new_slot.id
        booking.status = 'Booked'
        new_slot.booked_seats += 1
        new_slot.update_status()

        db.session.commit()
        flash(f'Booking #{booking.id} rescheduled successfully to {new_slot.date} ({new_slot.start_time.strftime("%H:%M")}).', 'success')
        return redirect(url_for('admin_bookings'))

    # Admin Unified Search
    @app.route('/admin/search')
    @login_required
    @role_required('admin')
    def admin_search():
        query = request.args.get('q', '').strip()
        students = []
        examiners = []
        exams = []
        bookings = []

        if query:
            # Search students
            students = User.query.filter(
                User.role == 'student',
                (User.full_name.ilike(f'%{query}%')) | 
                (User.roll_no.ilike(f'%{query}%')) | 
                (User.email.ilike(f'%{query}%')) |
                (User.username.ilike(f'%{query}%'))
            ).all()

            # Search examiners
            examiners = User.query.filter(
                User.role == 'examiner',
                (User.full_name.ilike(f'%{query}%')) | 
                (User.department.ilike(f'%{query}%')) | 
                (User.email.ilike(f'%{query}%'))
            ).all()

            # Search examinations
            exams = Examination.query.filter(
                (Examination.exam_name.ilike(f'%{query}%')) |
                (Examination.exam_type.ilike(f'%{query}%'))
            ).all()

            # Search bookings by ID if query is numeric
            if query.isdigit():
                booking = Booking.query.get(int(query))
                if booking:
                    bookings.append(booking)

        return render_template('admin/search.html',
                               query=query,
                               students=students,
                               examiners=examiners,
                               exams=exams,
                               bookings=bookings)

    # ----------------------------------------------------
    # Examiner Routes
    # ----------------------------------------------------
    @app.route('/examiner/dashboard')
    @login_required
    @role_required('examiner')
    def examiner_dashboard():
        examiner_id = session['user_id']
        my_slots = Slot.query.filter_by(examiner_id=examiner_id).order_by(Slot.date.desc(), Slot.start_time.asc()).all()
        slots_count = len(my_slots)
        
        # Calculate total students booked in examiner's slots
        total_booked_students = sum(s.booked_seats for s in my_slots)

        # Count pending evaluations
        pending_evaluations = 0
        for slot in my_slots:
            for b in slot.bookings:
                if b.status == 'Booked' and not b.evaluation:
                    pending_evaluations += 1

        # Assigned examinations (exams for which the examiner has slots or can create slots)
        available_exams = Examination.query.filter(
            Examination.status.in_(['Slot Creation', 'Booking Open', 'Draft'])
        ).all()

        return render_template('examiner/dashboard.html',
                               slots_count=slots_count,
                               total_booked_students=total_booked_students,
                               pending_evaluations=pending_evaluations,
                               my_slots=my_slots[:5],
                               available_exams=available_exams)

    @app.route('/examiner/slots')
    @login_required
    @role_required('examiner')
    def examiner_slots():
        examiner_id = session['user_id']
        slots = Slot.query.filter_by(examiner_id=examiner_id).order_by(Slot.date.desc(), Slot.start_time.asc()).all()
        return render_template('examiner/slots.html', slots=slots)

    @app.route('/examiner/slots/create', methods=['GET', 'POST'])
    @login_required
    @role_required('examiner')
    def examiner_create_slot():
        examiner_id = session['user_id']
        exams = Examination.query.all()
        
        # Filter exams that currently allow slot creation
        creatable_exams = [e for e in exams if e.is_slot_creation_allowed()]

        if request.method == 'POST':
            try:
                exam_id = int(request.form.get('examination_id'))
                exam = Examination.query.get_or_404(exam_id)

                # Check if slot creation is permitted for this exam
                if not exam.is_slot_creation_allowed():
                    flash(f'Slot creation for "{exam.exam_name}" is currently closed.', 'danger')
                    return render_template('examiner/create_slot.html', exams=creatable_exams)

                slot_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
                start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
                end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
                capacity = int(request.form.get('max_capacity', 1))
                room_link = request.form.get('room_link', '').strip()

                if start_time >= end_time:
                    flash('Slot End Time must be later than Start Time.', 'danger')
                    return render_template('examiner/create_slot.html', exams=creatable_exams)

                new_slot = Slot(
                    examination_id=exam.id,
                    examiner_id=examiner_id,
                    date=slot_date,
                    start_time=start_time,
                    end_time=end_time,
                    max_capacity=capacity,
                    booked_seats=0,
                    status='Available',
                    room_link=room_link
                )
                db.session.add(new_slot)
                db.session.commit()
                flash('Examination slot created successfully!', 'success')
                return redirect(url_for('examiner_slots'))
            except Exception as e:
                flash(f'Error creating slot: {str(e)}', 'danger')

        return render_template('examiner/create_slot.html', exams=creatable_exams)

    @app.route('/examiner/slots/edit/<int:slot_id>', methods=['GET', 'POST'])
    @login_required
    @role_required('examiner')
    def examiner_edit_slot(slot_id):
        examiner_id = session['user_id']
        slot = Slot.query.filter_by(id=slot_id, examiner_id=examiner_id).first_or_404()

        # Slots can only be edited before booking starts or if no bookings exist
        if slot.booked_seats > 0:
            flash('This slot already has student bookings and cannot be modified.', 'danger')
            return redirect(url_for('examiner_slots'))

        if request.method == 'POST':
            try:
                slot.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
                slot.start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
                slot.end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
                slot.max_capacity = int(request.form.get('max_capacity', 1))
                slot.room_link = request.form.get('room_link', '').strip()

                if slot.start_time >= slot.end_time:
                    flash('Slot End Time must be later than Start Time.', 'danger')
                    return render_template('examiner/edit_slot.html', slot=slot)

                slot.update_status()
                db.session.commit()
                flash('Slot updated successfully.', 'success')
                return redirect(url_for('examiner_slots'))
            except Exception as e:
                flash(f'Error updating slot: {str(e)}', 'danger')

        return render_template('examiner/edit_slot.html', slot=slot)

    @app.route('/examiner/slots/delete/<int:slot_id>', methods=['POST'])
    @login_required
    @role_required('examiner')
    def examiner_delete_slot(slot_id):
        examiner_id = session['user_id']
        slot = Slot.query.filter_by(id=slot_id, examiner_id=examiner_id).first_or_404()

        if slot.booked_seats > 0:
            flash('Cannot delete a slot with existing student bookings.', 'danger')
            return redirect(url_for('examiner_slots'))

        db.session.delete(slot)
        db.session.commit()
        flash('Slot deleted successfully.', 'info')
        return redirect(url_for('examiner_slots'))

    @app.route('/examiner/slots/<int:slot_id>/bookings')
    @login_required
    @role_required('examiner')
    def examiner_slot_bookings(slot_id):
        examiner_id = session['user_id']
        slot = Slot.query.filter_by(id=slot_id, examiner_id=examiner_id).first_or_404()
        return render_template('examiner/slot_bookings.html', slot=slot)

    @app.route('/examiner/evaluate/<int:booking_id>', methods=['GET', 'POST'])
    @login_required
    @role_required('examiner')
    def examiner_evaluate_booking(booking_id):
        examiner_id = session['user_id']
        booking = Booking.query.get_or_404(booking_id)

        # Security check: Examiners can evaluate only students booked into their own slots
        if booking.slot.examiner_id != examiner_id:
            flash('Unauthorized: You can only evaluate students in your assigned slots.', 'danger')
            return redirect(url_for('examiner_dashboard'))

        exam = booking.slot.examination
        rubrics = exam.rubrics

        if request.method == 'POST':
            remarks = request.form.get('remarks', '').strip()
            total_marks = 0.0

            # Check if evaluation already exists
            evaluation = Evaluation.query.filter_by(booking_id=booking.id).first()
            if not evaluation:
                evaluation = Evaluation(
                    booking_id=booking.id,
                    student_id=booking.student_id,
                    examiner_id=examiner_id,
                    examination_id=exam.id,
                    remarks=remarks,
                    is_published=True
                )
                db.session.add(evaluation)
                db.session.flush()
            else:
                evaluation.remarks = remarks
                evaluation.evaluated_at = datetime.utcnow()
                # Clear existing rubric scores to overwrite
                EvaluationScore.query.filter_by(evaluation_id=evaluation.id).delete()

            # Record scores per rubric criterion
            for r in rubrics:
                score_val = float(request.form.get(f'rubric_{r.id}', 0.0))
                crit_remark = request.form.get(f'rubric_remark_{r.id}', '').strip()
                # Clamp score
                score_val = min(r.max_marks, max(0.0, score_val))
                total_marks += score_val

                eval_score = EvaluationScore(
                    evaluation_id=evaluation.id,
                    rubric_id=r.id,
                    marks_obtained=score_val,
                    criterion_remarks=crit_remark
                )
                db.session.add(eval_score)

            evaluation.total_marks = round(total_marks, 2)
            booking.status = 'Completed'
            db.session.commit()

            flash(f'Evaluation submitted for student {booking.student.full_name}. Total Marks: {evaluation.total_marks}/{exam.max_marks}', 'success')
            return redirect(url_for('examiner_slot_bookings', slot_id=booking.slot_id))

        existing_eval = Evaluation.query.filter_by(booking_id=booking.id).first()
        return render_template('examiner/evaluate.html', booking=booking, exam=exam, rubrics=rubrics, evaluation=existing_eval)

    # ----------------------------------------------------
    # Student Routes
    # ----------------------------------------------------
    @app.route('/student/dashboard')
    @login_required
    @role_required('student')
    def student_dashboard():
        student_id = session['user_id']
        my_bookings = Booking.query.filter_by(student_id=student_id).order_by(Booking.booking_date.desc()).all()
        
        upcoming_bookings = [b for b in my_bookings if b.status == 'Booked']
        completed_bookings = [b for b in my_bookings if b.status == 'Completed']

        # Available exams for booking
        all_exams = Examination.query.all()
        available_exams = [e for e in all_exams if e.is_booking_allowed()]

        # Results
        results = Evaluation.query.filter_by(student_id=student_id, is_published=True).order_by(Evaluation.evaluated_at.desc()).all()

        return render_template('student/dashboard.html',
                               upcoming_bookings=upcoming_bookings,
                               completed_bookings=completed_bookings,
                               available_exams=available_exams,
                               results=results)

    @app.route('/student/exams')
    @login_required
    @role_required('student')
    def student_exams():
        query = request.args.get('q', '').strip()
        course_filter = request.args.get('course', '').strip()

        exam_query = Examination.query.join(Course)

        if query:
            exam_query = exam_query.filter(Examination.exam_name.ilike(f'%{query}%'))
        if course_filter:
            exam_query = exam_query.filter(Course.course_code == course_filter)

        exams = exam_query.order_by(Examination.created_at.desc()).all()
        courses = Course.query.filter_by(status='Active').all()

        return render_template('student/exams.html', exams=exams, courses=courses, query=query, selected_course=course_filter)

    @app.route('/student/exams/<int:exam_id>/slots')
    @login_required
    @role_required('student')
    def student_exam_slots(exam_id):
        student_id = session['user_id']
        exam = Examination.query.get_or_404(exam_id)

        # Check if student has already booked this exam
        existing_booking = Booking.query.join(Slot).filter(
            Booking.student_id == student_id,
            Slot.examination_id == exam.id,
            Booking.status == 'Booked'
        ).first()

        slots = Slot.query.filter_by(examination_id=exam.id, status='Available').order_by(Slot.date.asc(), Slot.start_time.asc()).all()

        return render_template('student/exam_slots.html', exam=exam, slots=slots, existing_booking=existing_booking)

    @app.route('/student/book/<int:slot_id>', methods=['POST'])
    @login_required
    @role_required('student')
    def student_book_slot(slot_id):
        student_id = session['user_id']
        slot = Slot.query.get_or_404(slot_id)
        exam = slot.examination

        # 1. Check if booking is allowed for this exam
        if not exam.is_booking_allowed():
            flash(f'Slot booking for "{exam.exam_name}" is currently closed.', 'danger')
            return redirect(url_for('student_exams'))

        # 2. Check if student already booked a slot for this examination
        existing = Booking.query.join(Slot).filter(
            Booking.student_id == student_id,
            Slot.examination_id == exam.id,
            Booking.status == 'Booked'
        ).first()

        if existing:
            flash(f'You have already booked a slot for "{exam.exam_name}". You cannot book duplicate slots.', 'warning')
            return redirect(url_for('student_bookings'))

        # 3. Check slot capacity to prevent overbooking
        if slot.booked_seats >= slot.max_capacity:
            flash('This slot has just reached full capacity. Please choose another slot.', 'danger')
            return redirect(url_for('student_exam_slots', exam_id=exam.id))

        # 4. Create booking
        booking = Booking(
            student_id=student_id,
            slot_id=slot.id,
            status='Booked'
        )
        db.session.add(booking)

        # 5. Update slot count & status
        slot.booked_seats += 1
        slot.update_status()

        db.session.commit()
        flash(f'Successfully booked slot for "{exam.exam_name}" on {slot.date} at {slot.start_time.strftime("%H:%M")}!', 'success')
        return redirect(url_for('student_bookings'))

    @app.route('/student/bookings')
    @login_required
    @role_required('student')
    def student_bookings():
        student_id = session['user_id']
        bookings = Booking.query.filter_by(student_id=student_id).order_by(Booking.booking_date.desc()).all()
        return render_template('student/bookings.html', bookings=bookings, today=date.today())

    @app.route('/student/bookings/cancel/<int:booking_id>', methods=['POST'])
    @login_required
    @role_required('student')
    def student_cancel_booking(booking_id):
        student_id = session['user_id']
        booking = Booking.query.filter_by(id=booking_id, student_id=student_id).first_or_404()

        if booking.status != 'Booked':
            flash('Only active bookings can be cancelled.', 'warning')
            return redirect(url_for('student_bookings'))

        # Check booking deadline: can cancel only if slot date is today or later, and booking deadline hasn't passed
        exam = booking.slot.examination
        today = date.today()
        if exam.slot_booking_end_date and today > exam.slot_booking_end_date:
            flash('Booking cancellation deadline for this exam has passed.', 'danger')
            return redirect(url_for('student_bookings'))

        # Cancel booking
        booking.status = 'Cancelled'
        slot = booking.slot
        slot.booked_seats = max(0, slot.booked_seats - 1)
        slot.update_status()

        db.session.commit()
        flash(f'Your booking for "{exam.exam_name}" has been cancelled.', 'info')
        return redirect(url_for('student_bookings'))

    @app.route('/student/results')
    @login_required
    @role_required('student')
    def student_results():
        student_id = session['user_id']
        evaluations = Evaluation.query.filter_by(student_id=student_id, is_published=True).order_by(Evaluation.evaluated_at.desc()).all()
        return render_template('student/results.html', evaluations=evaluations)

    @app.route('/student/results/<int:eval_id>/scorecard')
    @login_required
    def student_scorecard(eval_id):
        # Student viewing own scorecard or Admin viewing
        evaluation = Evaluation.query.get_or_404(eval_id)
        if session.get('role') == 'student' and evaluation.student_id != session['user_id']:
            abort(403)
        return render_template('student/scorecard.html', evaluation=evaluation)

    @app.route('/student/profile', methods=['GET', 'POST'])
    @login_required
    @role_required('student')
    def student_profile():
        user = User.query.get_or_404(session['user_id'])
        if request.method == 'POST':
            user.full_name = request.form.get('full_name', '').strip()
            user.phone = request.form.get('phone', '').strip()
            user.department = request.form.get('department', '').strip()
            user.roll_no = request.form.get('roll_no', '').strip()
            
            # Update password if provided
            new_pass = request.form.get('new_password', '')
            if new_pass:
                if len(new_pass) < 6:
                    flash('New password must be at least 6 characters.', 'danger')
                    return render_template('student/profile.html', user=user)
                user.set_password(new_pass)

            db.session.commit()
            session['full_name'] = user.full_name
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('student_profile'))

        return render_template('student/profile.html', user=user)

    # ----------------------------------------------------
    # Database Initialization & Demo Seeding Helper
    # ----------------------------------------------------
    with app.app_context():
        db.create_all()
        # Seed pre-existing admin
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@emp.edu',
                role='admin',
                status='active',
                full_name='System Administrator',
                department='Examination Division'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Pre-existing Admin created: admin / admin123")

    @app.route('/admin/seed-demo-data', methods=['POST'])
    @login_required
    @role_required('admin')
    def admin_seed_demo_data():
        from seed_data import populate_sample_data
        populate_sample_data()
        flash('Demo courses, examinations, examiners, and rubrics loaded successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return app

app = create_app()

if __name__ == '__main__':
    # Run the application locally
    app.run(debug=True, port=5000)
