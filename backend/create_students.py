'''TO USE:
python manage.py shell

from create_students import create_students
create_students()

'''

from django.contrib.auth.models import User
from registration.models import Profile, Student
import random

def create_students():
    base_password = "Wakanda45@"
    for i in range(1, 9):
        first_name = "Student"
        last_name = str(i)
        username = f"Student{i}"
        email = f"Student{i}@gmail.com"
        id_number = str(random.randint(100000, 999999))  # Random 6-digit number
        
        # Create the user
        user = User.objects.create_user(
            username=username,
            password=base_password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        
        # Create the profile
        profile = Profile.objects.create(
            user=user,
            id_number=id_number,
            role="student",
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        
        # Create the student
        student = Student.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        
        print(f"Created {username} with ID {id_number}")

# Call the function
create_students()
