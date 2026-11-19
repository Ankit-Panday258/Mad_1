from datetime import datetime, date, time
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'examiner', 'student'
    status = db.Column(db.String(20), default='active')  # 'active', 'pending', 'deactivated'
    
    # Profile fields
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))  # For examiners & students
    roll_no = db.Column(db.String(50))      # For students
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    slots_created = db.relationship('Slot', backref='examiner', lazy=True, foreign_keys='Slot.examiner_id')
    bookings = db.relationship('Booking', backref='student', lazy=True, foreign_keys='Booking.student_id')
    evaluations_given = db.relationship('Evaluation', backref='examiner', lazy=True, foreign_keys='Evaluation.examiner_id')
    evaluations_received = db.relationship('Evaluation', backref='student', lazy=True, foreign_keys='Evaluation.student_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Active')  # 'Active', 'Inactive'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with exams
    examinations = db.relationship('Examination', backref='course', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Course {self.course_code}: {self.course_name}>'


class Examination(db.Model):
    __tablename__ = 'examinations'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    exam_name = db.Column(db.String(150), nullable=False)
    exam_type = db.Column(db.String(50), default='Viva')  # 'Viva', 'Practical', 'Project Demo', 'Assessment'
    duration = db.Column(db.Integer, default=30)  # in minutes
    max_marks = db.Column(db.Integer, default=100)
    
    # Timelines
    slot_creation_start_date = db.Column(db.Date, nullable=False)
    slot_creation_end_date = db.Column(db.Date, nullable=False)
    slot_booking_start_date = db.Column(db.Date, nullable=False)
    slot_booking_end_date = db.Column(db.Date, nullable=False)
    
    # Status: 'Draft', 'Slot Creation', 'Booking Open', 'Closed', 'Completed'
    status = db.Column(db.String(30), default='Draft')
    instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    rubrics = db.relationship('Rubric', backref='examination', lazy=True, cascade='all, delete-orphan')
    slots = db.relationship('Slot', backref='examination', lazy=True, cascade='all, delete-orphan')
    evaluations = db.relationship('Evaluation', backref='examination', lazy=True, cascade='all, delete-orphan')

    def is_slot_creation_allowed(self):
        # Admin status must be 'Slot Creation' OR today within slot creation dates
        today = date.today()
        if self.status == 'Slot Creation':
            return True
        if self.slot_creation_start_date and self.slot_creation_end_date:
            return self.slot_creation_start_date <= today <= self.slot_creation_end_date
        return False

    def is_booking_allowed(self):
        # Admin status must be 'Booking Open' OR today within booking dates
        today = date.today()
        if self.status == 'Booking Open':
            return True
        if self.slot_booking_start_date and self.slot_booking_end_date:
            return self.slot_booking_start_date <= today <= self.slot_booking_end_date
        return False

    def __repr__(self):
        return f'<Examination {self.exam_name}>'


class Rubric(db.Model):
    __tablename__ = 'rubrics'
    
    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey('examinations.id'), nullable=False)
    criterion_name = db.Column(db.String(150), nullable=False)
    max_marks = db.Column(db.Float, nullable=False)
    weightage = db.Column(db.Float, default=1.0)
    description = db.Column(db.Text)

    scores = db.relationship('EvaluationScore', backref='rubric', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Rubric {self.criterion_name} ({self.max_marks} marks)>'


class Slot(db.Model):
    __tablename__ = 'slots'
    
    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey('examinations.id'), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    max_capacity = db.Column(db.Integer, default=1, nullable=False)
    booked_seats = db.Column(db.Integer, default=0, nullable=False)
    # Status: 'Available', 'Full', 'Cancelled', 'Completed'
    status = db.Column(db.String(20), default='Available')
    room_link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='slot', lazy=True, cascade='all, delete-orphan')

    @property
    def available_seats(self):
        return max(0, self.max_capacity - self.booked_seats)

    def update_status(self):
        if self.status != 'Cancelled' and self.status != 'Completed':
            if self.booked_seats >= self.max_capacity:
                self.status = 'Full'
            else:
                self.status = 'Available'

    def __repr__(self):
        return f'<Slot {self.date} {self.start_time}-{self.end_time}>'


class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('slots.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    # Status: 'Booked', 'Cancelled', 'Completed'
    status = db.Column(db.String(20), default='Booked')

    # Relationship to evaluation
    evaluation = db.relationship('Evaluation', backref='booking', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Booking #{self.id} Student:{self.student_id} Slot:{self.slot_id}>'


class Evaluation(db.Model):
    __tablename__ = 'evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    examination_id = db.Column(db.Integer, db.ForeignKey('examinations.id'), nullable=False)
    total_marks = db.Column(db.Float, default=0.0)
    remarks = db.Column(db.Text)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)

    scores = db.relationship('EvaluationScore', backref='evaluation', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Evaluation #{self.id} Marks:{self.total_marks}>'


class EvaluationScore(db.Model):
    __tablename__ = 'evaluation_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id'), nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey('rubrics.id'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)
    criterion_remarks = db.Column(db.String(255))

    def __repr__(self):
        return f'<Score Rubric:{self.rubric_id} Marks:{self.marks_obtained}>'
