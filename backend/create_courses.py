# create_courses.py
'''TO USE:
python manage.py shell

from create_courses import create_courses
create_courses()

'''

from registration.models import Course, Major
from datetime import date, time

def create_courses():
    # Fetch existing majors (assuming they were created using create_majors.py)
    computer_science = Major.objects.get(name="Computer Science")
    mathematics = Major.objects.get(name="Mathematics")
    english = Major.objects.get(name="English")
    physics = Major.objects.get(name="Physics")
    biology = Major.objects.get(name="Biology")
    chemistry = Major.objects.get(name="Chemistry")
    history = Major.objects.get(name="History")
    psychology = Major.objects.get(name="Psychology")
    economics = Major.objects.get(name="Economics")
    art = Major.objects.get(name="Art")

    # Define a list of courses with their details
    courses = [
        {
            "course_code": "CS101",
            "name": "Introduction to Computer Science",
            "description": "Fundamentals of programming and computer science.",
            "start_date": date(2023, 9, 1),
            "end_date": date(2023, 12, 15),
            "days": "MWF",
            "start_time": time(9, 0),
            "end_time": time(10, 0),
            "session_type": "Regular",
            "location": "Room 101",
            "available_seats": 30,
            "capacity": 30,
            "credits": 3,
            "semester": "fall",
            "majors": [computer_science],
        },
        {
            "course_code": "MATH201",
            "name": "Calculus I",
            "description": "Introduction to differential and integral calculus.",
            "start_date": date(2023, 9, 1),
            "end_date": date(2023, 12, 15),
            "days": "TTh",
            "start_time": time(10, 0),
            "end_time": time(11, 30),
            "session_type": "Regular",
            "location": "Room 202",
            "available_seats": 25,
            "capacity": 25,
            "credits": 4,
            "semester": "fall",
            "majors": [mathematics],
        },
        {
            "course_code": "ENG101",
            "name": "Introduction to Literature",
            "description": "Study of classic and contemporary literature.",
            "start_date": date(2023, 9, 1),
            "end_date": date(2023, 12, 15),
            "days": "MWF",
            "start_time": time(11, 0),
            "end_time": time(12, 0),
            "session_type": "Regular",
            "location": "Room 303",
            "available_seats": 20,
            "capacity": 20,
            "credits": 3,
            "semester": "fall",
            "majors": [english],
        },
        {
            "course_code": "PHYS101",
            "name": "Introduction to Physics",
            "description": "Fundamentals of classical mechanics and thermodynamics.",
            "start_date": date(2023, 9, 1),
            "end_date": date(2023, 12, 15),
            "days": "TTh",
            "start_time": time(13, 0),
            "end_time": time(14, 30),
            "session_type": "Regular",
            "location": "Room 404",
            "available_seats": 30,
            "capacity": 30,
            "credits": 4,
            "semester": "fall",
            "majors": [physics],
        },
        {
            "course_code": "BIO101",
            "name": "Introduction to Biology",
            "description": "Study of living organisms and their interactions.",
            "start_date": date(2023, 9, 1),
            "end_date": date(2023, 12, 15),
            "days": "MWF",
            "start_time": time(14, 0),
            "end_time": time(15, 0),
            "session_type": "Regular",
            "location": "Room 505",
            "available_seats": 25,
            "capacity": 25,
            "credits": 3,
            "semester": "fall",
            "majors": [biology],
        },
    ]

    # Create or update courses
    for course_data in courses:
        course, created = Course.objects.get_or_create(
            course_code=course_data["course_code"],
            defaults={
                "name": course_data["name"],
                "description": course_data["description"],
                "start_date": course_data["start_date"],
                "end_date": course_data["end_date"],
                "days": course_data["days"],
                "start_time": course_data["start_time"],
                "end_time": course_data["end_time"],
                "session_type": course_data["session_type"],
                "location": course_data["location"],
                "available_seats": course_data["available_seats"],
                "capacity": course_data["capacity"],
                "credits": course_data["credits"],
                "semester": course_data["semester"],
            }
        )

        # Add majors to the course
        for major in course_data["majors"]:
            course.majors.add(major)

        if created:
            print(f"Created course: {course.name}")
        else:
            print(f"Course already exists: {course.name}")

# Call the function
create_courses()