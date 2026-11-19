# Examination Management Portal (EMP)

An Examination Management Portal web application developed for **Modern Application Development 1 (MAD 1)**. The portal provides role-based interfaces for **Admin**, **Examiners (Faculty)**, and **Students** to manage course examinations, timelines, evaluation rubrics, slot bookings, and student performance records.

---

## 🛠️ Frameworks & Technologies Used

- **Back-end:** Python, Flask 3.x
- **Front-end:** Jinja2 Templating, HTML5, CSS3, Bootstrap 5 (Responsive UI)
- **Database:** SQLite (Relational ORM via Flask-SQLAlchemy)
- **Authentication:** Password hashing via Werkzeug (`generate_password_hash`, `check_password_hash`) and secure session-based RBAC

> **Note:** As specified in project guidelines, no core logic depends on client-side JavaScript. All actions are handled securely on the server via standard HTTP requests and Flask controllers.

---

## 👥 Roles & Key Features

### 1. Administrator (Pre-existing Superuser)
- **Pre-existing in database:** No registration allowed for Admin.
- **Dashboard Metrics:** Real-time counts of courses, examinations, examiners, students, slots, and bookings.
- **Course Management:** Create, edit, and delete academic courses.
- **Examination Management:** Create examinations, define duration, maximum marks, and configure timelines (slot creation period and student booking period).
- **Rubric Management:** Add and manage evaluation criteria, maximum marks, weightage, and guidelines for each exam.
- **Examiner Management:** Review self-registered examiners, approve pending requests, or deactivate accounts.
- **Slot Oversight & Reassignment:** View all examiner slots and reassign examiners in exceptional situations.
- **Booking Oversight & Rescheduling:** View all student bookings and reschedule bookings to alternative available slots.
- **Unified Search:** Search across students, examiners, examinations, and booking IDs.

### 2. Examiner (Faculty)
- **Self-Registration:** Registration requires Administrator approval before dashboard access.
- **Dashboard Metrics:** Assigned exams, created slots, number of booked students, and pending evaluations.
- **Slot Creation:** Create exam slots with date, time window, capacity, and venue/meeting link (only during active slot creation periods).
- **Slot Modification:** Edit or delete created slots before any student booking is made.
- **Student Evaluation:** View booked students for their slots and grade them using the defined examination rubrics. Enter individual rubric marks, criterion notes, and overall feedback.
- **Result Submission:** Submit final marks which are published to students.

### 3. Student
- **Self-Registration & Login:** Direct registration with roll number, program, and contact details.
- **Dashboard:** Upcoming exam bookings, examinations open for booking, and published scorecards.
- **Examination Search & Filter:** Filter exams by course or search by title.
- **Slot Booking:** Browse available slots and book a slot.
  - Automatically enforces maximum capacity and prevents overbooking.
  - Automatically prevents duplicate bookings for the same examination.
  - Validates that bookings occur within the configured booking window.
- **Booking Management:** Cancel bookings before the specified deadline.
- **Detailed Scorecard:** View official scorecard with rubric-by-rubric breakdown, percentages, examiner remarks, and print/PDF support.
- **Profile Management:** Update personal details, contact number, and password.

---

## 🗄️ Database Architecture & ER Design

The database is built programmatically using SQLite and SQLAlchemy:

1. **`users` Table:**
   - `id`, `username`, `email`, `password_hash`, `role` (`admin`, `examiner`, `student`), `status` (`active`, `pending`, `deactivated`), `full_name`, `phone`, `department`, `roll_no`, `created_at`.
2. **`courses` Table:**
   - `id`, `course_code` (unique), `course_name`, `description`, `status` (`Active`, `Inactive`), `created_at`.
3. **`examinations` Table:**
   - `id`, `course_id` (FK), `exam_name`, `exam_type` (`Viva`, `Practical`, `Project Demo`, `Assessment`), `duration`, `max_marks`, `slot_creation_start_date`, `slot_creation_end_date`, `slot_booking_start_date`, `slot_booking_end_date`, `status`, `instructions`.
4. **`rubrics` Table:**
   - `id`, `examination_id` (FK), `criterion_name`, `max_marks`, `weightage`, `description`.
5. **`slots` Table:**
   - `id`, `examination_id` (FK), `examiner_id` (FK), `date`, `start_time`, `end_time`, `max_capacity`, `booked_seats`, `status` (`Available`, `Full`, `Cancelled`), `room_link`.
6. **`bookings` Table:**
   - `id`, `student_id` (FK), `slot_id` (FK), `booking_date`, `status` (`Booked`, `Cancelled`, `Completed`).
7. **`evaluations` Table:**
   - `id`, `booking_id` (FK, unique), `student_id` (FK), `examiner_id` (FK), `examination_id` (FK), `total_marks`, `remarks`, `evaluated_at`, `is_published`.
8. **`evaluation_scores` Table:**
   - `id`, `evaluation_id` (FK), `rubric_id` (FK), `marks_obtained`, `criterion_remarks`.

---

## 🚀 Setup & Local Execution Guide

### Prerequisites
- Python 3.9+ (Python 3.10, 3.11, 3.12, 3.13 supported)
- pip

### 1. Clone the Repository
```bash
git clone https://github.com/Ankit-Panday258/Mad_1.git
cd Mad_1
```

### 2. (Optional) Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database & Populate Demo Data
The database is created programmatically. You can load sample demo data (courses, examinations with rubrics, examiners, and sample bookings) by running:
```bash
python3 seed_data.py
```

### 5. Run the Application
```bash
python3 app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### 6. Run Automated Tests
To run all test cases covering authentication, role permissions, slot creation, bookings, evaluations, rescheduling, and cancellation:
```bash
python3 test_app.py
```

---

## 🔑 Demo & Viva Credentials

| Role | Username | Password | Status / Notes |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Pre-existing superuser |
| **Examiner** | `ramesh_faculty` | `examiner123` | Approved Faculty (Computer Science) |
| **Examiner (Pending)** | `priya_faculty` | `examiner123` | Pending Admin Approval (for demoing approval flow) |
| **Student** | `rahul_student` | `student123` | Student with completed exam & scorecard |
| **Student (New)** | `sneha_student` | `student123` | Student ready to book new exam slots |
