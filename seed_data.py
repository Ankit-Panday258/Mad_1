from datetime import date, time, timedelta, datetime
from models import db, User, Course, Examination, Rubric, Slot, Booking, Evaluation, EvaluationScore

def populate_sample_data():
    today = date.today()

    # 1. Create Sample Courses
    course1 = Course.query.filter_by(course_code='CS101').first()
    if not course1:
        course1 = Course(
            course_code='CS101',
            course_name='Modern Application Development 1 (MAD 1)',
            description='Building web applications using Flask, Jinja2, SQLite, and Bootstrap.',
            status='Active'
        )
        db.session.add(course1)

    course2 = Course.query.filter_by(course_code='CS102').first()
    if not course2:
        course2 = Course(
            course_code='CS102',
            course_name='Database Management Systems (DBMS)',
            description='Relational database design, SQL queries, normalization, and indexing.',
            status='Active'
        )
        db.session.add(course2)

    course3 = Course.query.filter_by(course_code='CS201').first()
    if not course3:
        course3 = Course(
            course_code='CS201',
            course_name='Data Structures and Algorithms (DSA)',
            description='Core data structures, algorithm analysis, and problem-solving.',
            status='Active'
        )
        db.session.add(course3)

    db.session.commit()

    # 2. Create Sample Examiners
    examiner1 = User.query.filter_by(username='ramesh_faculty').first()
    if not examiner1:
        examiner1 = User(
            username='ramesh_faculty',
            email='ramesh@emp.edu',
            role='examiner',
            status='active',
            full_name='Dr. Ramesh Kumar',
            department='Computer Science',
            phone='9876543211'
        )
        examiner1.set_password('examiner123')
        db.session.add(examiner1)

    examiner2 = User.query.filter_by(username='priya_faculty').first()
    if not examiner2:
        examiner2 = User(
            username='priya_faculty',
            email='priya@emp.edu',
            role='examiner',
            status='pending',  # Pending approval for testing Admin approve flow
            full_name='Dr. Priya Sharma',
            department='Data Science',
            phone='9876543212'
        )
        examiner2.set_password('examiner123')
        db.session.add(examiner2)

    # 3. Create Sample Students
    student1 = User.query.filter_by(username='rahul_student').first()
    if not student1:
        student1 = User(
            username='rahul_student',
            email='rahul@student.edu',
            role='student',
            status='active',
            full_name='Rahul Verma',
            roll_no='21F1001234',
            department='BS Data Science',
            phone='9123456789'
        )
        student1.set_password('student123')
        db.session.add(student1)

    student2 = User.query.filter_by(username='sneha_student').first()
    if not student2:
        student2 = User(
            username='sneha_student',
            email='sneha@student.edu',
            role='student',
            status='active',
            full_name='Sneha Patel',
            roll_no='21F1005678',
            department='BS Programming',
            phone='9123456780'
        )
        student2.set_password('student123')
        db.session.add(student2)

    db.session.commit()

    # 4. Create Sample Examination
    exam1 = Examination.query.filter_by(exam_name='MAD 1 Project Demo & Viva').first()
    if not exam1:
        exam1 = Examination(
            course_id=course1.id,
            exam_name='MAD 1 Project Demo & Viva',
            exam_type='Project Demo',
            duration=30,
            max_marks=100,
            slot_creation_start_date=today - timedelta(days=7),
            slot_creation_end_date=today + timedelta(days=14),
            slot_booking_start_date=today - timedelta(days=5),
            slot_booking_end_date=today + timedelta(days=10),
            status='Booking Open',
            instructions='Please ensure your local environment is running with Flask and SQLite ready for demonstration.'
        )
        db.session.add(exam1)
        db.session.commit()

        # Add Rubrics for exam1
        r1 = Rubric(examination_id=exam1.id, criterion_name='Core Architecture & Functionalities', max_marks=40, weightage=1.0, description='All roles (Admin, Examiner, Student) implemented per spec.')
        r2 = Rubric(examination_id=exam1.id, criterion_name='Database & Data Integrity', max_marks=20, weightage=1.0, description='SQLite models, relational constraints, no overbooking.')
        r3 = Rubric(examination_id=exam1.id, criterion_name='Live Demonstration & Viva Q&A', max_marks=30, weightage=1.0, description='Ability to answer viva questions and demonstrate live workflows.')
        r4 = Rubric(examination_id=exam1.id, criterion_name='Project Report & Guidelines', max_marks=10, weightage=1.0, description='Complete 5-page report with ER diagram and AI declaration.')
        db.session.add_all([r1, r2, r3, r4])
        db.session.commit()

    exam2 = Examination.query.filter_by(exam_name='DBMS Practical Evaluation').first()
    if not exam2:
        exam2 = Examination(
            course_id=course2.id,
            exam_name='DBMS Practical Evaluation',
            exam_type='Practical',
            duration=45,
            max_marks=50,
            slot_creation_start_date=today - timedelta(days=2),
            slot_creation_end_date=today + timedelta(days=10),
            slot_booking_start_date=today + timedelta(days=1),
            slot_booking_end_date=today + timedelta(days=8),
            status='Slot Creation',
            instructions='Practical SQL query execution and normalization tasks.'
        )
        db.session.add(exam2)
        db.session.commit()

        r_dbms1 = Rubric(examination_id=exam2.id, criterion_name='Complex SQL Queries', max_marks=25, weightage=1.0, description='Joins, subqueries, group by')
        r_dbms2 = Rubric(examination_id=exam2.id, criterion_name='Schema Design & Normalization', max_marks=25, weightage=1.0, description='BCNF / 3NF justification')
        db.session.add_all([r_dbms1, r_dbms2])
        db.session.commit()

    # 5. Create Sample Slots for Examiner 1
    slot1 = Slot.query.filter_by(examination_id=exam1.id, examiner_id=examiner1.id).first()
    if not slot1:
        slot1 = Slot(
            examination_id=exam1.id,
            examiner_id=examiner1.id,
            date=today + timedelta(days=2),
            start_time=time(10, 0),
            end_time=time(10, 30),
            max_capacity=2,
            booked_seats=1,
            status='Available',
            room_link='Google Meet: https://meet.google.com/abc-defg-hij'
        )
        slot2 = Slot(
            examination_id=exam1.id,
            examiner_id=examiner1.id,
            date=today + timedelta(days=2),
            start_time=time(11, 0),
            end_time=time(11, 30),
            max_capacity=1,
            booked_seats=0,
            status='Available',
            room_link='Room 204, Academic Block A'
        )
        db.session.add_all([slot1, slot2])
        db.session.commit()

        # Create one sample booking for student1
        booking1 = Booking(
            student_id=student1.id,
            slot_id=slot1.id,
            status='Completed'
        )
        db.session.add(booking1)
        db.session.commit()

        # Add sample evaluation for viva demonstration
        eval1 = Evaluation(
            booking_id=booking1.id,
            student_id=student1.id,
            examiner_id=examiner1.id,
            examination_id=exam1.id,
            total_marks=88.0,
            remarks='Strong project architecture and clear database design. Answered all viva questions proficiently.',
            is_published=True
        )
        db.session.add(eval1)
        db.session.flush()

        score1 = EvaluationScore(evaluation_id=eval1.id, rubric_id=r1.id, marks_obtained=36.0, criterion_remarks='All core roles implemented smoothly')
        score2 = EvaluationScore(evaluation_id=eval1.id, rubric_id=r2.id, marks_obtained=18.0, criterion_remarks='Clean SQLite schema with relations')
        score3 = EvaluationScore(evaluation_id=eval1.id, rubric_id=r3.id, marks_obtained=25.0, criterion_remarks='Answered questions with good understanding')
        score4 = EvaluationScore(evaluation_id=eval1.id, rubric_id=r4.id, marks_obtained=9.0, criterion_remarks='Report well structured')
        db.session.add_all([score1, score2, score3, score4])
        db.session.commit()

    print("Sample data populated successfully.")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        populate_sample_data()
