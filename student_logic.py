""" STUDENT MANAGEMENT SYSTEM """

from functools import reduce

students = []
SUBJECTS = ("Maths", "Science", "English")
total_students_added = 0


# validation

def validate_name(name):
    cleaned = name.strip()
    if cleaned == "":
        return None
    if not cleaned.replace(" ", "").isalpha():
        return None
    return cleaned.title()


def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 75:
        return "A"
    elif percentage >= 60:
        return "B"
    elif percentage >= 40:
        return "C"
    else:
        return "F"


def _recalculate(student):
    marks = student["marks"]
    total = sum(marks.values())
    average = total / len(SUBJECTS)
    percentage = (total / (len(SUBJECTS) * 100)) * 100
    student["total"] = total
    student["average"] = round(average, 2)
    student["percentage"] = round(percentage, 2)
    student["grade"] = calculate_grade(percentage)
    return student


# core operations 

def find_student(roll):
    for s in students:
        if s["roll"] == roll:
            return s
    return None


def add_student(name, city, roll, marks):

    global total_students_added

    valid_name = validate_name(name)
    if valid_name is None:
        return False, "Invalid name! Use letters and spaces only."

    if not isinstance(roll, int):
        return False, "Roll number must be an integer."

    if find_student(roll) is not None:
        return False, "A student with this roll number already exists!"

    for subject in SUBJECTS:
        if subject not in marks:
            return False, f"Missing marks for {subject}."
        mark = marks[subject]
        if not isinstance(mark, int) or mark < 0 or mark > 100:
            return False, f"Marks for {subject} must be an integer between 0 and 100."

    student = {
        "roll": roll,
        "name": valid_name,
        "city": city.strip().title(),
        "marks": dict(marks),
    }
    _recalculate(student)
    students.append(student)
    total_students_added += 1
    return True, f"Student '{valid_name}' added successfully!"


def update_student(roll, new_name=None, new_city=None, new_marks=None):

    target = find_student(roll)
    if target is None:
        return False, "No student found with that roll number."

    if new_name:
        valid_name = validate_name(new_name)
        if valid_name:
            target["name"] = valid_name
        else:
            return False, "Invalid name format. Name not changed."

    if new_city:
        target["city"] = new_city.strip().title()

    if new_marks:
        for subject, mark in new_marks.items():
            if subject not in SUBJECTS:
                continue
            if not isinstance(mark, int) or mark < 0 or mark > 100:
                return False, f"Marks for {subject} out of range. Update aborted."
            target["marks"][subject] = mark

    _recalculate(target)
    return True, "Student record updated successfully!"


def delete_student(roll):
    target = find_student(roll)
    if target is None:
        return False, "No student found with that roll number."
    students.remove(target)
    return True, f"Student '{target['name']}' (Roll {roll}) deleted."


def get_all_students():
    return list(students)


def get_passed_students():
    return list(filter(lambda s: s["grade"] != "F", students))


def get_sorted_students():
    return sorted(students, key=lambda s: s["total"], reverse=True)


def get_class_average():
  
    if not students:
        return None
    percentages = list(map(lambda s: round((s["total"] / (len(SUBJECTS) * 100)) * 100, 2),
                            students))
    grand_total = reduce(lambda acc, s: acc + s["total"], students, 0)
    class_average = grand_total / len(students)
    return grand_total, round(class_average, 2), list(zip(students, percentages))


def get_unique_cities():
    return {s["city"] for s in students}
