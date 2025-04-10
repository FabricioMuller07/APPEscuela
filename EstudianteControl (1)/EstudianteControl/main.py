import streamlit as st
import pandas as pd
from data_manager import DataManager
from components import (
    render_student_form,
    render_attendance_section,
    render_behavior_section,
    render_assignments_section,
    render_notes_section,
    render_class_overview
)

# Initialize session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

def main():
    st.set_page_config(
        page_title="Sistema de Gestión Estudiantil",
        page_icon="📚",
        layout="wide"
    )

    st.title("Sistema de Gestión Estudiantil")

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navegación",
        ["Gestión de Alumnos", "Vista General", "Exportar Datos"]
    )

    if page == "Gestión de Alumnos":
        manage_students()
    elif page == "Vista General":
        class_overview()
    else:
        export_data()

def manage_students():
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Información del Curso")

        # Add new course section
        with st.expander("Agregar Nuevo Curso"):
            new_course = st.text_input("Nombre del Nuevo Curso", key="new_course_input")
            if st.button("Agregar Curso"):
                if new_course:
                    if st.session_state.data_manager.add_course(new_course):
                        st.success(f"Curso {new_course} agregado exitosamente")
                        st.rerun()  # Rerun to update the course list
                    else:
                        st.error("Error al agregar el curso")
                else:
                    st.warning("Por favor ingrese un nombre para el curso")

        # Course selection
        courses = st.session_state.data_manager.get_courses()
        if not courses:
            st.info("No hay cursos disponibles. Por favor, agregue un curso nuevo.")
            course = None
        else:
            course = st.selectbox(
                "Seleccionar Curso",
                options=courses,
                key="course_select"
            )

    with col2:
        if course:
            students = st.session_state.data_manager.get_students(course)
            selected_student = st.selectbox(
                "Seleccionar Alumno",
                options=["-Nuevo Alumno-"] + students
            )

            if selected_student == "-Nuevo Alumno-":
                render_student_form(course)
            else:
                student_data = st.session_state.data_manager.get_student_data(course, selected_student)

                tabs = st.tabs(["Asistencia", "Conducta", "Trabajos", "Notas"])

                with tabs[0]:
                    render_attendance_section(course, selected_student)

                with tabs[1]:
                    render_behavior_section(course, selected_student)

                with tabs[2]:
                    render_assignments_section(course, selected_student)

                with tabs[3]:
                    render_notes_section(course, selected_student)

def class_overview():
    st.subheader("Vista General del Curso")
    courses = st.session_state.data_manager.get_courses()
    if not courses:
        st.info("No hay cursos disponibles. Por favor, agregue un curso en la sección de Gestión de Alumnos.")
        return

    course = st.selectbox(
        "Seleccionar Curso",
        options=courses
    )

    if course:
        render_class_overview(course)

def export_data():
    st.subheader("Exportar Datos")
    courses = st.session_state.data_manager.get_courses()
    if not courses:
        st.info("No hay cursos disponibles para exportar.")
        return

    course = st.selectbox(
        "Seleccionar Curso para Exportar",
        options=courses
    )

    if course and st.button("Exportar a CSV"):
        csv_data = st.session_state.data_manager.export_to_csv(course)
        st.download_button(
            label="Descargar CSV",
            data=csv_data,
            file_name=f"{course}_datos.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()