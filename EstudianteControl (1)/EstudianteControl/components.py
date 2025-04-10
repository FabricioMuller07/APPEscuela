import streamlit as st
from datetime import datetime
import plotly.express as px
import pandas as pd

def render_student_form(course):
    st.subheader("Agregar Nuevo Alumno")
    
    with st.form("new_student_form"):
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        
        if st.form_submit_button("Agregar Alumno"):
            if nombre and apellido:
                student_data = {
                    'nombre': nombre,
                    'apellido': apellido
                }
                if st.session_state.data_manager.add_student(course, student_data):
                    st.success("Alumno agregado exitosamente")
                else:
                    st.error("Error al agregar el alumno")
            else:
                st.error("Por favor complete todos los campos")

def render_attendance_section(course, student):
    st.subheader("Registro de Asistencia")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        date = st.date_input("Fecha", datetime.now())
        status = st.selectbox(
            "Estado",
            ["Presente", "Ausente", "Tardanza"]
        )
        
        if st.button("Registrar Asistencia"):
            st.session_state.data_manager.add_attendance(
                course, student, status, date.strftime('%Y-%m-%d')
            )
            st.success("Asistencia registrada")
    
    with col2:
        attendance_data = st.session_state.data_manager.get_student_data(course, student)['attendance']
        if attendance_data:
            df = pd.DataFrame(attendance_data)
            fig = px.pie(
                df,
                names='status',
                title='Distribución de Asistencia'
            )
            st.plotly_chart(fig)

def render_behavior_section(course, student):
    st.subheader("Notas de Conducta")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        score = st.slider("Calificación", 1, 10, 7)
        description = st.text_area("Descripción")
        
        if st.button("Registrar Nota de Conducta"):
            st.session_state.data_manager.add_behavior_note(
                course, student, score, description
            )
            st.success("Nota de conducta registrada")
    
    with col2:
        behavior_data = st.session_state.data_manager.get_student_data(course, student)['behavior']
        if behavior_data:
            df = pd.DataFrame(behavior_data)
            fig = px.line(
                df,
                x='date',
                y='score',
                title='Evolución de Conducta'
            )
            st.plotly_chart(fig)

def render_assignments_section(course, student):
    st.subheader("Trabajos")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        title = st.text_input("Título del Trabajo")
        status = st.selectbox(
            "Estado",
            ["Entregado", "Pendiente", "Atrasado"]
        )
        date = st.date_input("Fecha de Entrega", datetime.now())
        
        if st.button("Registrar Trabajo"):
            st.session_state.data_manager.add_assignment(
                course, student, title, status, date.strftime('%Y-%m-%d')
            )
            st.success("Trabajo registrado")
    
    with col2:
        assignments_data = st.session_state.data_manager.get_student_data(course, student)['assignments']
        if assignments_data:
            df = pd.DataFrame(assignments_data)
            fig = px.bar(
                df,
                x='status',
                title='Estado de Trabajos'
            )
            st.plotly_chart(fig)

def render_notes_section(course, student):
    st.subheader("Notas y Descargos")
    
    note = st.text_area("Nueva Nota")
    if st.button("Agregar Nota"):
        st.session_state.data_manager.add_note(course, student, note)
        st.success("Nota agregada")
    
    notes_data = st.session_state.data_manager.get_student_data(course, student)['notes']
    if notes_data:
        for note in notes_data:
            st.text(f"{note['date']}: {note['note']}")

def render_class_overview(course):
    students_data = []
    
    for student in st.session_state.data_manager.get_students(course):
        data = st.session_state.data_manager.get_student_data(course, student)
        
        attendance_rate = sum(1 for a in data['attendance'] if a['status'] == 'Presente') / len(data['attendance']) if data['attendance'] else 0
        behavior_avg = sum(b['score'] for b in data['behavior']) / len(data['behavior']) if data['behavior'] else 0
        assignments_completed = sum(1 for a in data['assignments'] if a['status'] == 'Entregado')
        
        students_data.append({
            'Alumno': student,
            'Asistencia (%)': round(attendance_rate * 100, 2),
            'Promedio Conducta': round(behavior_avg, 2),
            'Trabajos Entregados': assignments_completed,
            'Total Trabajos': len(data['assignments'])
        })
    
    if students_data:
        df = pd.DataFrame(students_data)
        st.dataframe(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                df,
                x='Alumno',
                y='Asistencia (%)',
                title='Asistencia por Alumno'
            )
            st.plotly_chart(fig)
        
        with col2:
            fig = px.bar(
                df,
                x='Alumno',
                y='Promedio Conducta',
                title='Promedio de Conducta por Alumno'
            )
            st.plotly_chart(fig)
