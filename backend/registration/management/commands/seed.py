import random
from django.core.management.base import BaseCommand
from registration.models import Course, Student, Enrollment

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.seed_courses()
        self.seed_students()
        self.seed_enrollments()
        self.stdout.write(self.style.SUCCESS('Database has been seeded!'))

    def seed_courses(self):
        Course.objects.all().delete()
        courses = [
            ('Mathematics', 'An introductory course to Mathematics', 'MWF 9:00-10:00', 30),
            ('Physics', 'An introductory course to Physics', 'TTh 10:00-11:30', 25),
            ('Chemistry', 'An introductory course to Chemistry', 'MWF 11:00-12:00', 20),
            ('Biology', 'An introductory course to Biology', 'TTh 1:00-2:30', 35),
        ]
        for name, description, schedule, capacity in courses:
            Course.objects.create(name=name, description=description, schedule=schedule, capacity=capacity)

    def seed_students(self):
        Student.objects.all().delete()
        students = [
            ('John', 'Doe', 'john.doe@example.com'),
            ('Jane', 'Doe', 'jane.doe@example.com'),
            ('Alice', 'Smith', 'alice.smith@example.com'),
            ('Bob', 'Brown', 'bob.brown@example.com'),
        ]
        for first_name, last_name, email in students:
            Student.objects.create(first_name=first_name, last_name=last_name, email=email)

    def seed_enrollments(self):
        Enrollment.objects.all().delete()
        students = Student.objects.all()
        courses = Course.objects.all()
        for student in students:
            enrolled_courses = random.sample(list(courses), 2)  # Enroll each student in 2 random courses
            for course in enrolled_courses:
                Enrollment.objects.create(student=student, course=course)
