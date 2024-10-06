from django.contrib.auth.models import User
from registration.models import Student, Professor, Admin

# Common password for all users
password = 'defaultpassword123'

# Create Students
def create_students():
    for i in range(1, 11):  # Creating 10 students
        username = f'student{i}'
        first_name = 'Student'
        last_name = str(i)
        email = f'student{i}@university.edu'
        id_number = f'STUD00{i}'

        # Create User instance
        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)

        # Create Student instance
        Student.objects.create(user=user, id_number=id_number)

    print("Students created successfully!")


# Create Professors
def create_professors():
    for i in range(1, 6):  # Creating 5 professors
        username = f'professor{i}'
        first_name = 'Professor'
        last_name = str(i)
        email = f'professor{i}@university.edu'
        id_number = f'PROF00{i}'

        # Create User instance
        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)

        # Create Professor instance
        Professor.objects.create(user=user, id_number=id_number)

    print("Professors created successfully!")


# Create Admins
def create_admins():
    for i in range(1, 4):  # Creating 3 admins
        username = f'admin{i}'
        first_name = 'Admin'
        last_name = str(i)
        email = f'admin{i}@university.edu'
        id_number = f'ADMIN00{i}'

        # Create User instance
        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)

        # Create Admin instance
        Admin.objects.create(user=user, id_number=id_number)

    print("Admins created successfully!")


# Call all creation functions
create_students()
create_professors()
create_admins()
