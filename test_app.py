import unittest
from datetime import date, time, timedelta
from app import create_app
from models import db, User, Course, Examination, Rubric, Slot, Booking, Evaluation, EvaluationScore

class EMPTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Ensure default admin exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@emp.edu',
                    role='admin',
                    status='active',
                    full_name='System Administrator'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_01_admin_login(self):
        response = self.login('admin', 'admin123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Administrator Dashboard', response.data)

    def test_02_student_registration_and_login(self):
        # Register student
        res = self.client.post('/register/student', data=dict(
            full_name='Test Student',
            roll_no='21F1000001',
            username='student_test',
            email='teststudent@emp.edu',
            department='BS Data Science',
            phone='9999999999',
            password='password123',
            confirm_password='password123'
        ), follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Registration successful', res.data)

        # Login student
        res_login = self.login('student_test', 'password123')
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Student Dashboard', res_login.data)

    def test_03_examiner_registration_approval_flow(self):
        # Register examiner (should start as pending)
        res = self.client.post('/register/examiner', data=dict(
            full_name='Dr. Test Examiner',
            department='Computer Science',
            username='examiner_test',
            email='testexaminer@emp.edu',
            phone='8888888888',
            password='password123',
            confirm_password='password123'
        ), follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'requires Admin approval', res.data)

        # Try to login before approval -> should be blocked
        res_fail = self.login('examiner_test', 'password123')
        self.assertIn(b'pending Admin approval', res_fail.data)

        # Admin logs in and approves examiner
        self.login('admin', 'admin123')
        with self.app.app_context():
            examiner = User.query.filter_by(username='examiner_test').first()
            examiner_id = examiner.id

        res_approve = self.client.post(f'/admin/examiners/{examiner_id}/status/approve', follow_redirects=True)
        self.assertEqual(res_approve.status_code, 200)
        self.logout()

        # Examiner logs in after approval
        res_success = self.login('examiner_test', 'password123')
        self.assertIn(b'Examiner Dashboard', res_success.data)

    def test_04_full_examination_and_booking_workflow(self):
        # 1. Admin creates course & exam with rubrics
        self.login('admin', 'admin123')
        self.client.post('/admin/courses/create', data=dict(
            course_code='CS101',
            course_name='Modern Application Development 1',
            description='Flask and SQLite',
            status='Active'
        ), follow_redirects=True)

        today = date.today()
        self.client.post('/admin/exams/create', data=dict(
            course_id=1,
            exam_name='MAD 1 End Term Demo',
            exam_type='Project Demo',
            duration=30,
            max_marks=100,
            slot_creation_start_date=(today - timedelta(days=2)).strftime('%Y-%m-%d'),
            slot_creation_end_date=(today + timedelta(days=5)).strftime('%Y-%m-%d'),
            slot_booking_start_date=(today - timedelta(days=1)).strftime('%Y-%m-%d'),
            slot_booking_end_date=(today + timedelta(days=5)).strftime('%Y-%m-%d'),
            status='Booking Open',
            instructions='Demo on local Flask server.'
        ), follow_redirects=True)

        # Add rubric
        self.client.post('/admin/exams/1/rubrics/create', data=dict(
            criterion_name='Implementation',
            max_marks=50,
            weightage=1.0,
            description='Working core features'
        ), follow_redirects=True)
        self.client.post('/admin/exams/1/rubrics/create', data=dict(
            criterion_name='Viva Q&A',
            max_marks=50,
            weightage=1.0,
            description='Understanding demonstrated'
        ), follow_redirects=True)

        # Approve examiner
        with self.app.app_context():
            ex = User(username='fac1', email='fac1@emp.edu', role='examiner', status='active', full_name='Faculty One')
            ex.set_password('facpass')
            st = User(username='stu1', email='stu1@emp.edu', role='student', status='active', full_name='Student One', roll_no='21F001')
            st.set_password('stupass')
            db.session.add_all([ex, st])
            db.session.commit()

        self.logout()

        # 2. Examiner creates slot
        self.login('fac1', 'facpass')
        res_slot = self.client.post('/examiner/slots/create', data=dict(
            examination_id=1,
            date=(today + timedelta(days=2)).strftime('%Y-%m-%d'),
            start_time='10:00',
            end_time='10:30',
            max_capacity=1,
            room_link='Room 101'
        ), follow_redirects=True)
        self.assertIn(b'slot created successfully', res_slot.data.lower())
        self.logout()

        # 3. Student books the slot
        self.login('stu1', 'stupass')
        res_book = self.client.post('/student/book/1', follow_redirects=True)
        self.assertIn(b'successfully booked slot', res_book.data.lower())

        # Prevent duplicate booking test
        res_dup = self.client.post('/student/book/1', follow_redirects=True)
        self.assertIn(b'already booked', res_dup.data.lower())
        self.logout()

        # 4. Examiner evaluates the booked student
        self.login('fac1', 'facpass')
        res_eval = self.client.post('/examiner/evaluate/1', data={
            'rubric_1': '45',
            'rubric_remark_1': 'Excellent implementation',
            'rubric_2': '48',
            'rubric_remark_2': 'Very clear conceptual understanding',
            'remarks': 'Outstanding performance in all aspects.'
        }, follow_redirects=True)
        self.assertIn(b'evaluation submitted', res_eval.data.lower())
        self.logout()

        # 5. Student checks published result and scorecard
        self.login('stu1', 'stupass')
        res_scorecard = self.client.get('/student/results/1/scorecard')
        self.assertEqual(res_scorecard.status_code, 200)
        self.assertIn(b'Official Student Examination Scorecard', res_scorecard.data)
        self.assertIn(b'93.0', res_scorecard.data)  # 45 + 48
        self.logout()

    def test_05_admin_reschedule_and_reassign(self):
        # Setup course, exam, slots, booking
        with self.app.app_context():
            c = Course(course_code='CS202', course_name='Software Engineering')
            db.session.add(c)
            db.session.commit()

            today = date.today()
            exm = Examination(
                course_id=c.id, exam_name='SE Demo', exam_type='Practical',
                duration=30, max_marks=50,
                slot_creation_start_date=today, slot_creation_end_date=today + timedelta(days=5),
                slot_booking_start_date=today, slot_booking_end_date=today + timedelta(days=5),
                status='Booking Open'
            )
            db.session.add(exm)
            db.session.commit()

            ex1 = User(username='fac_a', email='faca@emp.edu', role='examiner', status='active', full_name='Faculty A')
            ex1.set_password('pass')
            ex2 = User(username='fac_b', email='facb@emp.edu', role='examiner', status='active', full_name='Faculty B')
            ex2.set_password('pass')
            st = User(username='stu_a', email='stua@emp.edu', role='student', status='active', full_name='Student A', roll_no='21F999')
            st.set_password('pass')
            db.session.add_all([ex1, ex2, st])
            db.session.commit()

            slot1 = Slot(examination_id=exm.id, examiner_id=ex1.id, date=today + timedelta(days=1), start_time=time(9, 0), end_time=time(9, 30), max_capacity=2, booked_seats=1, status='Available')
            slot2 = Slot(examination_id=exm.id, examiner_id=ex2.id, date=today + timedelta(days=2), start_time=time(14, 0), end_time=time(14, 30), max_capacity=2, booked_seats=0, status='Available')
            db.session.add_all([slot1, slot2])
            db.session.commit()

            b = Booking(student_id=st.id, slot_id=slot1.id, status='Booked')
            db.session.add(b)
            db.session.commit()
            booking_id = b.id
            slot1_id = slot1.id
            slot2_id = slot2.id
            ex2_id = ex2.id

        # Admin logs in
        self.login('admin', 'admin123')

        # Admin reassigns slot1 examiner to Faculty B
        res_reassign = self.client.post(f'/admin/slots/{slot1_id}/reassign', data=dict(examiner_id=ex2_id), follow_redirects=True)
        self.assertIn(b'reassigned to examiner', res_reassign.data.lower())

        # Admin reschedules booking to slot2
        res_resched = self.client.post(f'/admin/bookings/{booking_id}/reschedule', data=dict(new_slot_id=slot2_id), follow_redirects=True)
        self.assertIn(b'rescheduled successfully', res_resched.data.lower())

        # Verify state in DB
        with self.app.app_context():
            updated_booking = db.session.get(Booking, booking_id)
            self.assertEqual(updated_booking.slot_id, slot2_id)
            updated_slot1 = db.session.get(Slot, slot1_id)
            self.assertEqual(updated_slot1.booked_seats, 0)
            updated_slot2 = db.session.get(Slot, slot2_id)
            self.assertEqual(updated_slot2.booked_seats, 1)

    def test_06_student_cancellation_and_search(self):
        with self.app.app_context():
            c = Course(course_code='CS303', course_name='Web Programming')
            db.session.add(c)
            db.session.commit()

            today = date.today()
            exm = Examination(
                course_id=c.id, exam_name='Web Lab Viva', exam_type='Viva',
                duration=20, max_marks=25,
                slot_creation_start_date=today, slot_creation_end_date=today + timedelta(days=5),
                slot_booking_start_date=today, slot_booking_end_date=today + timedelta(days=5),
                status='Booking Open'
            )
            ex = User(username='fac_web', email='facweb@emp.edu', role='examiner', status='active', full_name='Prof. Web')
            ex.set_password('pass')
            st = User(username='stu_web', email='stuweb@emp.edu', role='student', status='active', full_name='Rohit Gupta', roll_no='21F7777')
            st.set_password('pass')
            db.session.add_all([exm, ex, st])
            db.session.commit()

            slot = Slot(examination_id=exm.id, examiner_id=ex.id, date=today + timedelta(days=1), start_time=time(15, 0), end_time=time(15, 30), max_capacity=1, booked_seats=1, status='Full')
            db.session.add(slot)
            db.session.commit()

            b = Booking(student_id=st.id, slot_id=slot.id, status='Booked')
            db.session.add(b)
            db.session.commit()
            booking_id = b.id
            slot_id = slot.id

        # Student logs in and cancels booking
        self.login('stu_web', 'pass')
        res_cancel = self.client.post(f'/student/bookings/cancel/{booking_id}', follow_redirects=True)
        self.assertIn(b'has been cancelled', res_cancel.data.lower())

        with self.app.app_context():
            slot_updated = db.session.get(Slot, slot_id)
            self.assertEqual(slot_updated.booked_seats, 0)
            self.assertEqual(slot_updated.status, 'Available')
        self.logout()

        # Admin search
        self.login('admin', 'admin123')
        res_search = self.client.get('/admin/search?q=Rohit', follow_redirects=True)
        self.assertIn(b'Rohit Gupta', res_search.data)
        self.logout()

if __name__ == '__main__':
    unittest.main()
