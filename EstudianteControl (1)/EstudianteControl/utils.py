from datetime import datetime

def validate_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None

def calculate_attendance_percentage(attendance_list):
    if not attendance_list:
        return 0
    present_count = sum(1 for a in attendance_list if a['status'] == 'Presente')
    return (present_count / len(attendance_list)) * 100

def calculate_behavior_average(behavior_list):
    if not behavior_list:
        return 0
    return sum(b['score'] for b in behavior_list) / len(behavior_list)

def calculate_assignment_completion(assignments_list):
    if not assignments_list:
        return 0, 0
    completed = sum(1 for a in assignments_list if a['status'] == 'Entregado')
    return completed, len(assignments_list)
