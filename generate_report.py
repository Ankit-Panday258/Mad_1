import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        print(f"TOTAL_PAGES_IN_PDF: {num_pages}")
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#555555"))
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Examination Management Portal (EMP) — MAD 1 Project Report")
            self.setStrokeColor(colors.HexColor("#dddddd"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "IIT Madras BS Degree — Modern Application Development 1")
        self.setStrokeColor(colors.HexColor("#dddddd"))
        self.setLineWidth(0.5)
        self.line(54, 52, 558, 52)
        self.restoreState()

def build_pdf(filename="Project_Report_EMP.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0d6efd'),
        alignment=1, # Center
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#495057'),
        alignment=1,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#0d6efd'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SubSectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#212529'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#212529'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=14,
        spaceAfter=3
    )

    table_text = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#212529')
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=table_text,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )

    story = []

    # ================= PAGE 1 =================
    story.append(Paragraph("EXAMINATION MANAGEMENT PORTAL (EMP)", title_style))
    story.append(Paragraph("Course Project Report — Modern Application Development 1 (MAD 1)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0d6efd'), spaceAfter=12))

    # Student Details Table
    story.append(Paragraph("1. Student & Project Details", h1_style))
    student_data = [
        [Paragraph("Student Name:", table_header), Paragraph("Ankit Pandey", table_text),
         Paragraph("Roll Number:", table_header), Paragraph("21f1002580", table_text)],
        [Paragraph("Email ID:", table_header), Paragraph("ankitsilao258@gmail.com", table_text),
         Paragraph("Degree Program:", table_header), Paragraph("BS in Data Science & Applications", table_text)],
        [Paragraph("Course Code:", table_header), Paragraph("MAD 1 (CS101)", table_text),
         Paragraph("GitHub Repository:", table_header), Paragraph("https://github.com/Ankit-Panday258/Mad_1", table_text)],
        [Paragraph("Demo Video Link:", table_header), Paragraph("https://drive.google.com/file/d/demo-video-link/view", table_text),
         Paragraph("Development Stack:", table_header), Paragraph("Flask, SQLite, Jinja2, Bootstrap 5", table_text)]
    ]
    t_student = Table(student_data, colWidths=[100, 152, 95, 157])
    t_student.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#0d6efd')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ced4da')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_student)
    story.append(Spacer(1, 10))

    # Problem Statement & Approach
    story.append(Paragraph("2. Problem Statement & Objectives", h1_style))
    story.append(Paragraph(
        "Educational institutions manage high volumes of semester assessments, vivas, and project demonstrations. "
        "Manual tracking via spreadsheets leads to scheduling conflicts, lack of visibility, and grading discrepancies. "
        "The objective of this project is to develop a role-based <b>Examination Management Portal (EMP)</b> enabling "
        "<b>Administrators</b>, <b>Examiners</b>, and <b>Students</b> to seamlessly coordinate courses, examinations, "
        "evaluation rubrics, slot bookings, and official scorecards.",
        body_style
    ))

    story.append(Paragraph("3. Architectural Approach & Implementation Strategy", h1_style))
    story.append(Paragraph(
        "The application is engineered strictly following the <b>Model-View-Controller (MVC)</b> architecture using Flask. "
        "In compliance with project specifications, <b>no client-side JavaScript is utilized for core business logic</b>. "
        "All data validation, capacity constraints, status checks, and access restrictions are enforced securely on the backend:",
        body_style
    ))
    story.append(Paragraph("• <b>Modular Role-Based Access Control (RBAC):</b> Session-authenticated roles (Admin, Examiner, Student) protected by clean route decorators.", bullet_style))
    story.append(Paragraph("• <b>Programmatic Database Lifecycle:</b> SQLite schema created and initialized via SQLAlchemy ORM without manual DB GUI intervention.", bullet_style))
    story.append(Paragraph("• <b>Server-Side Form Processing & Flashes:</b> HTTP POST requests handle state transitions, atomic updates, and user alerts.", bullet_style))
    story.append(Paragraph("• <b>Strict Business Constraints:</b> Automatic slot capacity enforcement, duplicate booking prevention, and rubric-tied evaluation checks.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("4. Frameworks & Libraries Used", h1_style))
    tech_data = [
        [Paragraph("Technology / Library", table_header), Paragraph("Version", table_header), Paragraph("Role / Usage in Application", table_header)],
        [Paragraph("Python", table_text), Paragraph("3.13 / 3.9+", table_text), Paragraph("Core programming language for application backend", table_text)],
        [Paragraph("Flask", table_text), Paragraph("3.1.1", table_text), Paragraph("WSGI web framework, routing, request/session handling", table_text)],
        [Paragraph("Flask-SQLAlchemy", table_text), Paragraph("3.1.1", table_text), Paragraph("Object Relational Mapping (ORM) and SQLite DB interface", table_text)],
        [Paragraph("SQLite", table_text), Paragraph("3.x", table_text), Paragraph("Mandatory embedded relational database engine", table_text)],
        [Paragraph("Werkzeug", table_text), Paragraph("3.0+", table_text), Paragraph("Security module for PBKDF2-SHA256 password hashing", table_text)],
        [Paragraph("Jinja2", table_text), Paragraph("3.1+", table_text), Paragraph("Server-side templating engine for dynamic HTML rendering", table_text)],
        [Paragraph("Bootstrap", table_text), Paragraph("5.3.0", table_text), Paragraph("Responsive CSS framework for plain, accessible UI", table_text)]
    ]
    t_tech = Table(tech_data, colWidths=[120, 74, 310])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#212529')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_tech)

    # Section 5 without forced pagebreak
    story.append(Spacer(1, 10))
    story.append(Paragraph("5. Database Schema & Entity-Relationship (ER) Architecture", h1_style))
    story.append(Paragraph(
        "The relational database contains 8 normalized tables designed in SQLite using SQLAlchemy ORM. "
        "Foreign key constraints maintain referential integrity across examinations, examiner slots, bookings, and rubric scores.",
        body_style
    ))

    schema_data = [
        [Paragraph("Table Name", table_header), Paragraph("Primary Key", table_header), Paragraph("Foreign Keys", table_header), Paragraph("Key Attributes & Description", table_header)],
        [Paragraph("<b>users</b>", table_text), Paragraph("id", table_text), Paragraph("-", table_text),
         Paragraph("username, email, password_hash, role (admin/examiner/student), status (active/pending/deactivated), full_name, roll_no, department, phone", table_text)],
        [Paragraph("<b>courses</b>", table_text), Paragraph("id", table_text), Paragraph("-", table_text),
         Paragraph("course_code (unique), course_name, description, status (Active/Inactive), created_at", table_text)],
        [Paragraph("<b>examinations</b>", table_text), Paragraph("id", table_text), Paragraph("course_id -> courses.id", table_text),
         Paragraph("exam_name, exam_type, duration, max_marks, slot_creation_start/end, booking_start/end, status (Draft/Slot Creation/Booking Open/Closed/Completed)", table_text)],
        [Paragraph("<b>rubrics</b>", table_text), Paragraph("id", table_text), Paragraph("examination_id -> examinations.id", table_text),
         Paragraph("criterion_name, max_marks, weightage, description (defines evaluation criteria for each examination)", table_text)],
        [Paragraph("<b>slots</b>", table_text), Paragraph("id", table_text), Paragraph("examination_id, examiner_id", table_text),
         Paragraph("date, start_time, end_time, max_capacity, booked_seats, status (Available/Full/Cancelled), room_link", table_text)],
        [Paragraph("<b>bookings</b>", table_text), Paragraph("id", table_text), Paragraph("student_id, slot_id", table_text),
         Paragraph("booking_date, status (Booked/Cancelled/Completed). Connects student to a scheduled exam slot", table_text)],
        [Paragraph("<b>evaluations</b>", table_text), Paragraph("id", table_text), Paragraph("booking_id, student_id, examiner_id, examination_id", table_text),
         Paragraph("total_marks, remarks, evaluated_at, is_published. Stores examiner's cumulative grading", table_text)],
        [Paragraph("<b>evaluation_scores</b>", table_text), Paragraph("id", table_text), Paragraph("evaluation_id, rubric_id", table_text),
         Paragraph("marks_obtained, criterion_remarks. Stores granular scores mapped to individual rubric criteria", table_text)]
    ]
    t_schema = Table(schema_data, colWidths=[90, 60, 110, 244])
    t_schema.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ced4da')),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_schema)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Database Entity-Relationship (ER) Flow Diagram", h2_style))
    er_box_content = [
        [Paragraph("""
<b>[courses]</b> (1) ──── (N) <b>[examinations]</b> (1) ──── (N) <b>[rubrics]</b><br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│ (1)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼ (N)<br/>
<b>[users]</b> (Examiner) (1) ─── (N) <b>[slots]</b> (1) ──── (N) <b>[bookings]</b> ◄─── (N) <b>[users]</b> (Student)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│ (1:1)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>[evaluations]</b> (1) ──── (N) <b>[evaluation_scores]</b>
        """, body_style)]
    ]
    t_er = Table(er_box_content, colWidths=[504])
    t_er.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#6c757d')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_er)

    # Section 6
    story.append(Spacer(1, 10))
    story.append(Paragraph("6. Role-Based Modules & Key Functionalities", h1_style))
    
    story.append(Paragraph("A. Administrator Module (Superuser)", h2_style))
    story.append(Paragraph("• <b>Pre-existing Superuser:</b> Pre-configured account (admin/admin123) with highest permissions; admin self-registration is permanently disabled.", bullet_style))
    story.append(Paragraph("• <b>Dashboard Statistics:</b> Live counter cards display total courses, examinations, examiners, registered students, slots, and bookings.", bullet_style))
    story.append(Paragraph("• <b>Course & Exam Management:</b> Full CRUD operations for courses and examinations with configurable start/end dates for slot creation and booking.", bullet_style))
    story.append(Paragraph("• <b>Rubric Criteria Management:</b> Define and manage granular scoring criteria per examination with custom max marks, weights, and grading rubrics.", bullet_style))
    story.append(Paragraph("• <b>Examiner Onboarding & Control:</b> Approve pending examiner registration requests, or deactivate/reactivate faculty accounts.", bullet_style))
    story.append(Paragraph("• <b>Reassignment & Rescheduling:</b> Ability to change assigned examiners on slots and reschedule student bookings to alternative slots in exceptional scenarios.", bullet_style))
    story.append(Paragraph("• <b>Unified Search Engine:</b> Cross-entity searching across students (name, roll no), examiners, examinations, and booking IDs.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("B. Examiner Module (Faculty)", h2_style))
    story.append(Paragraph("• <b>Registration & Admin Approval:</b> Faculty self-registers and remains in 'pending' status until verified and approved by the Administrator.", bullet_style))
    story.append(Paragraph("• <b>Slot Creation Period Enforcement:</b> Examiners can create examination slots only when the exam status is 'Slot Creation' or within the active date window.", bullet_style))
    story.append(Paragraph("• <b>Slot Modification Safeguards:</b> Slots can only be updated or removed if no students have booked seats (booked_seats == 0).", bullet_style))
    story.append(Paragraph("• <b>Role-Secured Evaluation:</b> Examiners can view and evaluate only students booked into their own slots.", bullet_style))
    story.append(Paragraph("• <b>Rubrics-Based Grading:</b> System auto-renders evaluation forms containing the exam's rubrics; examiner inputs score per criterion, criterion notes, and cumulative remarks.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("C. Student Module", h2_style))
    story.append(Paragraph("• <b>Self-Registration & Dashboard:</b> Student registers with name, roll number, and department. Dashboard surfaces upcoming exams and published scorecards.", bullet_style))
    story.append(Paragraph("• <b>Exam Browsing & Filtering:</b> Search examinations by title and filter by academic course.", bullet_style))
    story.append(Paragraph("• <b>Overbooking & Duplicate Prevention:</b> Slot booking enforces max capacity (automatically marks status as 'Full' when capacity is reached) and prevents duplicate bookings for the same exam.", bullet_style))
    story.append(Paragraph("• <b>Cancellation:</b> Students can cancel their active booking before the exam booking deadline, which instantly restores slot seat availability.", bullet_style))
    story.append(Paragraph("• <b>Scorecard & Performance History:</b> Students can view evaluation results with rubric score breakdowns and examiner feedback in an accessible format.", bullet_style))

    # Section 7
    story.append(Spacer(1, 10))
    story.append(Paragraph("7. Application Web Routes & API Resources", h1_style))
    story.append(Paragraph(
        "The application utilizes REST-style Flask controller endpoints managing requests, view rendering, and state mutations:",
        body_style
    ))

    routes_data = [
        [Paragraph("Endpoint / Route", table_header), Paragraph("HTTP Method", table_header), Paragraph("Role Access", table_header), Paragraph("Functionality / Action", table_header)],
        [Paragraph("<code>/login</code>, <code>/logout</code>", table_text), Paragraph("GET, POST", table_text), Paragraph("Public / All", table_text), Paragraph("Role-based login and session termination", table_text)],
        [Paragraph("<code>/register/student</code>", table_text), Paragraph("GET, POST", table_text), Paragraph("Public", table_text), Paragraph("Student self-registration with roll number", table_text)],
        [Paragraph("<code>/register/examiner</code>", table_text), Paragraph("GET, POST", table_text), Paragraph("Public", table_text), Paragraph("Faculty registration (status set to pending)", table_text)],
        [Paragraph("<code>/admin/dashboard</code>", table_text), Paragraph("GET", table_text), Paragraph("Admin", table_text), Paragraph("Summary statistics and pending approvals", table_text)],
        [Paragraph("<code>/admin/courses/create</code>", table_text), Paragraph("GET, POST", table_text), Paragraph("Admin", table_text), Paragraph("Add new academic course with unique code", table_text)],
        [Paragraph("<code>/admin/exams/create</code>", table_text), Paragraph("GET, POST", table_text), Paragraph("Admin", table_text), Paragraph("Configure examination duration, marks & dates", table_text)],
        [Paragraph("<code>/admin/exams/&lt;id&gt;/rubrics</code>", table_text), Paragraph("GET, POST", table_text), Paragraph("Admin", table_text), Paragraph("Manage evaluation rubrics criteria", table_text)],
        [Paragraph("<code>/admin/examiners/&lt;id&gt;/status</code>", table_text), Paragraph("POST", table_text), Paragraph("Admin", table_text), Paragraph("Approve, deactivate, or reactivate examiner", table_text)],
        [Paragraph("<code>/admin/slots/&lt;id&gt;/reassign</code>", table_text), Paragraph("POST", table_text), Paragraph("Admin", table_text), Paragraph("Reassign examiner to a scheduled slot", table_text)],
        [Paragraph("<code>/admin/bookings/&lt;id&gt;/reschedule</code>", table_text), Paragraph("POST", table_text), Paragraph("Admin", table_text), Paragraph("Reschedule student booking to another slot", table_text)],
        [Paragraph("<code>/examiner/slots/create</code>", table_text), Paragraph("GET, POST", table_text), Paragraph("Examiner", table_text), Paragraph("Create exam slot during slot creation window", table_text)],
        [Paragraph("<code>/examiner/evaluate/&lt;booking_id&gt;</code>", table_text), Paragraph("GET, POST", table_text), Paragraph("Examiner", table_text), Paragraph("Submit rubrics grading, remarks & publish marks", table_text)],
        [Paragraph("<code>/student/book/&lt;slot_id&gt;</code>", table_text), Paragraph("POST", table_text), Paragraph("Student", table_text), Paragraph("Book slot with duplicate & capacity check", table_text)],
        [Paragraph("<code>/student/bookings/cancel/&lt;id&gt;</code>", table_text), Paragraph("POST", table_text), Paragraph("Student", table_text), Paragraph("Cancel booking before deadline & restore seat", table_text)],
        [Paragraph("<code>/student/results/&lt;id&gt;/scorecard</code>", table_text), Paragraph("GET", table_text), Paragraph("Student / Admin", table_text), Paragraph("View scorecard breakdown & feedback", table_text)]
    ]
    t_routes = Table(routes_data, colWidths=[150, 60, 84, 210])
    t_routes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#212529')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_routes)

    # Section 8
    story.append(Spacer(1, 10))
    story.append(Paragraph("8. Quality Assurance & Automated Testing Verification", h1_style))
    story.append(Paragraph(
        "A dedicated unit test suite (<code>test_app.py</code>) containing 8 automated test cases was implemented. "
        "The test suite verifies all critical paths in an isolated in-memory SQLite database environment:",
        body_style
    ))

    test_data = [
        [Paragraph("Test Identifier", table_header), Paragraph("Functional Scope Tested", table_header), Paragraph("Status", table_header)],
        [Paragraph("<code>test_01_admin_login</code>", table_text), Paragraph("Pre-existing superuser login and dashboard metrics verification", table_text), Paragraph("PASSED", table_text)],
        [Paragraph("<code>test_02_student_registration</code>", table_text), Paragraph("Student self-registration, validation, and dashboard access", table_text), Paragraph("PASSED", table_text)],
        [Paragraph("<code>test_03_examiner_approval</code>", table_text), Paragraph("Examiner registration (pending check), admin approval, and login", table_text), Paragraph("PASSED", table_text)],
        [Paragraph("<code>test_04_booking_and_evaluation</code>", table_text), Paragraph("Slot creation, student booking, duplicate check, rubrics evaluation", table_text), Paragraph("PASSED", table_text)],
        [Paragraph("<code>test_05_reschedule_and_reassign</code>", table_text), Paragraph("Admin slot examiner re-assignment and booking slot rescheduling", table_text), Paragraph("PASSED", table_text)],
        [Paragraph("<code>test_06_cancellation_and_search</code>", table_text), Paragraph("Student booking cancellation, seat restoration, and unified search", table_text), Paragraph("PASSED", table_text)],
        [Paragraph("<code>test_07_rbac_access_control</code>", table_text), Paragraph("Unauthenticated redirects and cross-role unauthorized access blocking", table_text), Paragraph("PASSED", table_text)],
        [Paragraph("<code>test_08_input_validations</code>", table_text), Paragraph("Password mismatch, password length, and duplicate user checks", table_text), Paragraph("PASSED", table_text)]
    ]
    t_tests = Table(test_data, colWidths=[150, 274, 80])
    t_tests.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#198754')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_tests)
    story.append(Spacer(1, 12))

    story.append(Paragraph("9. AI / LLM Declaration", h1_style))
    story.append(Paragraph(
        "In accordance with the IIT Madras BS Degree academic integrity guidelines for Course Projects, "
        "the following declaration outlines the extent of Generative AI / LLM usage:",
        body_style
    ))
    story.append(Paragraph("• <b>Tool Employed:</b> Google Antigravity (Gemini-powered coding assistant).", bullet_style))
    story.append(Paragraph("• <b>Scope of Assistance:</b> AI was utilized for setting up standard Flask application boilerplate, generating HTML/Bootstrap form templates, structuring SQLite model definitions, and formulating comprehensive unit tests in <code>test_app.py</code>.", bullet_style))
    story.append(Paragraph("• <b>Student Understanding & Verification:</b> The student has thoroughly inspected, understood, and tested every component of the code base. The student has full conceptual grasp of the relational database structure, Flask controller request cycles, Jinja2 template rendering, role authorization decorators, and business constraints.", bullet_style))
    story.append(Paragraph("• <b>Demonstration Readiness:</b> The student is prepared to explain the architecture, walk through the codebase, execute live demos, and answer all viva examination questions independently.", bullet_style))

    story.append(Spacer(1, 16))
    
    # Signature Box
    sig_data = [
        [Paragraph("<b>Student Signature:</b> Ankit Pandey", body_style),
         Paragraph("<b>Date of Submission:</b> 19 November 2026", body_style)]
    ]
    t_sig = Table(sig_data, colWidths=[252, 252])
    t_sig.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1, colors.HexColor('#0d6efd')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_sig)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report built successfully: {filename}")

if __name__ == '__main__':
    build_pdf('/Users/ankitpandey/Downloads/Mad_1/Project_Report_EMP.pdf')
