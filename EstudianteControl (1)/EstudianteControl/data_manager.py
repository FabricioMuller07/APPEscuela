import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import QueuePool
import os
import urllib.parse

Base = declarative_base()

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    students = relationship("Student", back_populates="course", cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'))
    course = relationship("Course", back_populates="students")
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    behaviors = relationship("Behavior", back_populates="student", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="student", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="student", cascade="all, delete-orphan")

class Attendance(Base):
    __tablename__ = 'attendances'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'))
    student = relationship("Student", back_populates="attendances")

class Behavior(Base):
    __tablename__ = 'behaviors'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    score = Column(Integer, nullable=False)
    description = Column(Text)
    student_id = Column(Integer, ForeignKey('students.id'))
    student = relationship("Student", back_populates="behaviors")

class Assignment(Base):
    __tablename__ = 'assignments'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    title = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'))
    student = relationship("Student", back_populates="assignments")

class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    content = Column(Text, nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'))
    student = relationship("Student", back_populates="notes")

class DataManager:
    def __init__(self):
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not found")

        try:
            print(f"Inicializando conexión a la base de datos...")
            # Usar directamente la URL de la base de datos proporcionada por Replit
            self.engine = create_engine(
                database_url,
                echo=True,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_pre_ping=True,
                pool_recycle=1800
            )

            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            print("Conexión a la base de datos establecida exitosamente")
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            raise

    def add_course(self, course_name):
        try:
            print(f"Intentando agregar curso: {course_name}")
            existing_course = self.session.query(Course).filter_by(name=course_name).first()
            if existing_course:
                print(f"El curso {course_name} ya existe")
                return False

            course = Course(name=course_name)
            self.session.add(course)
            print(f"Curso agregado a la sesión: {course_name}")
            try:
                self.session.commit()
                print(f"Curso {course_name} agregado exitosamente")
                return True
            except Exception as commit_error:
                print(f"Error al hacer commit del curso: {str(commit_error)}")
                self.session.rollback()
                return False
        except Exception as e:
            print(f"Error al agregar curso: {str(e)}")
            self.session.rollback()
            return False

    def get_courses(self):
        try:
            print("Obteniendo lista de cursos...")
            courses = self.session.query(Course).all()
            course_names = [course.name for course in courses]
            print(f"Cursos encontrados: {course_names}")
            return course_names
        except Exception as e:
            print(f"Error al obtener cursos: {str(e)}")
            return []

    def add_student(self, course, student_data):
        try:
            course_obj = self.session.query(Course).filter_by(name=course).first()
            if not course_obj:
                return False

            student = Student(
                first_name=student_data['nombre'],
                last_name=student_data['apellido'],
                course=course_obj
            )
            self.session.add(student)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error al agregar estudiante: {str(e)}")
            return False

    def get_students(self, course):
        course_obj = self.session.query(Course).filter_by(name=course).first()
        if not course_obj:
            return []
        return [f"{student.last_name}, {student.first_name}" for student in course_obj.students]

    def get_student_data(self, course, student_name):
        last_name, first_name = student_name.split(", ")
        student = self.session.query(Student).join(Course).filter(
            Course.name == course,
            Student.last_name == last_name,
            Student.first_name == first_name
        ).first()

        if not student:
            return {
                'attendance': [],
                'behavior': [],
                'assignments': [],
                'notes': []
            }

        return {
            'attendance': [{'date': str(a.date), 'status': a.status} for a in student.attendances],
            'behavior': [{'date': str(b.date), 'score': b.score, 'description': b.description} for b in student.behaviors],
            'assignments': [{'date': str(a.date), 'title': a.title, 'status': a.status} for a in student.assignments],
            'notes': [{'date': str(n.date), 'note': n.content} for n in student.notes]
        }

    def add_attendance(self, course, student_name, status, date):
        last_name, first_name = student_name.split(", ")
        student = self.session.query(Student).join(Course).filter(
            Course.name == course,
            Student.last_name == last_name,
            Student.first_name == first_name
        ).first()

        if student:
            attendance = Attendance(
                student=student,
                date=datetime.strptime(date, '%Y-%m-%d').date(),
                status=status
            )
            self.session.add(attendance)
            self.session.commit()

    def add_behavior_note(self, course, student_name, score, description):
        last_name, first_name = student_name.split(", ")
        student = self.session.query(Student).join(Course).filter(
            Course.name == course,
            Student.last_name == last_name,
            Student.first_name == first_name
        ).first()

        if student:
            behavior = Behavior(
                student=student,
                date=datetime.now().date(),
                score=score,
                description=description
            )
            self.session.add(behavior)
            self.session.commit()

    def add_assignment(self, course, student_name, title, status, date):
        last_name, first_name = student_name.split(", ")
        student = self.session.query(Student).join(Course).filter(
            Course.name == course,
            Student.last_name == last_name,
            Student.first_name == first_name
        ).first()

        if student:
            assignment = Assignment(
                student=student,
                date=datetime.strptime(date, '%Y-%m-%d').date(),
                title=title,
                status=status
            )
            self.session.add(assignment)
            self.session.commit()

    def add_note(self, course, student_name, note):
        last_name, first_name = student_name.split(", ")
        student = self.session.query(Student).join(Course).filter(
            Course.name == course,
            Student.last_name == last_name,
            Student.first_name == first_name
        ).first()

        if student:
            note_obj = Note(
                student=student,
                date=datetime.now().date(),
                content=note
            )
            self.session.add(note_obj)
            self.session.commit()

    def export_to_csv(self, course):
        course_obj = self.session.query(Course).filter_by(name=course).first()
        if not course_obj:
            return None

        records = []
        for student in course_obj.students:
            attendance_rate = len([a for a in student.attendances if a.status == 'Presente']) / len(student.attendances) if student.attendances else 0
            behavior_avg = sum(b.score for b in student.behaviors) / len(student.behaviors) if student.behaviors else 0
            assignments_completed = len([a for a in student.assignments if a.status == 'Entregado'])

            records.append({
                'Alumno': f"{student.last_name}, {student.first_name}",
                'Asistencia (%)': round(attendance_rate * 100, 2),
                'Promedio Conducta': round(behavior_avg, 2),
                'Trabajos Entregados': assignments_completed,
                'Total Trabajos': len(student.assignments)
            })

        df = pd.DataFrame(records)
        return df.to_csv(index=False)