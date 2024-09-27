from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from .models import Course, Student, Professor, Admin, Profile, Enrollment, Assignment, Announcement
from .forms import CourseForm, StudentForm, ProfessorForm, AdminForm, GradeForm, ProfileForm, UserRegistrationForm, StudentRegistrationForm, ProfessorRegistrationForm, AssignmentForm, AnnouncementForm 
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    role = form.cleaned_data.get('role')
                    id_number = form.cleaned_data.get('id_number')
                    user.first_name = form.cleaned_data.get('first_name')
                    user.last_name = form.cleaned_data.get('last_name')
                    user.save()

                    Profile.objects.create(
                        user=user,
                        id_number=id_number,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        role=role,
                        email=user.email,
                    )

                    if role == 'student':
                        Student.objects.create(
                            user=user,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            email=user.email
                        )
                    elif role == 'professor':
                        Professor.objects.create(
                            user=user,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            email=user.email
                        )
                    elif role == 'admin':
                        Admin.objects.create(
                            user=user,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            email=user.email
                        )

                    login(request, user)
                    messages.success(request, 'Your account has been created successfully!')
                    return redirect('home')
            except IntegrityError:
                form.add_error('username', 'This username is already taken. Please choose another one.')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('login')  

def home_view(request):
    user_role = request.user.profile.role  
    return render(request, 'home.html', {'user_role': user_role})

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'registration/course_list.html', {'courses': courses})

def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'registration/course_form.html', {'form': form})

def enroll_in_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(Student, user=request.user)

    if course.available_seats <= 0:
        messages.error(request, 'No available seats in this course.')
        return redirect('available_courses')
    
    try:
        Enrollment.objects.create(student=student, course=course)
        course.available_seats -= 1
        course.save()
        messages.success(request, f'You have successfully enrolled in {course.name}.')
    except IntegrityError:
        messages.error(request, f'You are already enrolled in {course.name}.')
    
    return redirect('student_schedule')

def view_enrollments(request):
    student = request.user.student
    enrollments = Enrollment.objects.filter(student=student)
    return render(request, 'registration/view_enrollments.html', {'enrollments': enrollments})

def available_courses(request):
    student = request.user.student  # Assuming the user is logged in as a student
    courses = Course.objects.all()  # Fetch all available courses
    enrolled_courses = Enrollment.objects.filter(student=student).values_list('course', flat=True)
    
    context = {
        'courses': courses,
        'enrolled_courses': enrolled_courses,
    }
    return render(request, 'available_courses.html', context)

def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    student = request.user.student
    Enrollment.objects.create(student=student, course=course)
    return redirect('student_schedule')

def student_list(request):
    query = request.GET.get('q', '')
    if query:
        students = Student.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(user__profile__id_number__icontains=query)
        )
    else:
        students = Student.objects.all()
    
    return render(request, 'registration/student_list.html', {'students': students, 'query': query})

def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.user = request.user
            student.save()
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'registration/student_form.html', {'form': form})

def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'registration/student_detail.html', {"student": student})

def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            student = form.save(commit=False)
            user = student.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            student.save()
            form.save_m2m()
            return redirect('student_list')
        else:
            return JsonResponse(form.errors, status=400)
    else:
        form = StudentForm(instance=student)
    return render(request, 'registration/student_form.html', {'form': form})

def student_schedule(request):
    student_instance = get_object_or_404(Student, user=request.user)
    enrollments = Enrollment.objects.filter(student=student_instance)
    return render(request, 'registration/student_schedule.html', {'enrollments': enrollments})

def professor_list(request):
    query = request.GET.get('q', '')
    if query:
        professors = Professor.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(user__profile__id_number__icontains=query)
        )
    else:
        professors = Professor.objects.all()
    
    return render(request, 'registration/professor_list.html', {'professors': professors, 'query': query})

def professor_schedule(request):
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'registration/professor_schedule.html', {'courses': courses})

def professor_create(request):
    if request.method == "POST":
        form = ProfessorForm(request.POST)
        if form.is_valid():
            professor = form.save(commit=False)
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email']
            )
            professor = form.save(commit=False)
            professor.user = user
            professor.save()
            return redirect('professor_list')
        else:
            return JsonResponse(form.errors, status=400)
    else:
        form = ProfessorForm()
    return render(request, 'registration/professor_form.html', {'form': form})

def professor_update(request, pk):
    professor = get_object_or_404(Professor, pk=pk)
    if request.method == 'POST':
        form = ProfessorForm(request.POST, request.FILES, instance=professor)
        if form.is_valid():
            professor = form.save(commit=False)
            user = professor.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            professor.save()
            return redirect('professor_list')
    else:
        form = ProfessorForm(instance=professor)
    return render(request, 'registration/professor_form.html', {'form': form})

def professor_delete(request, pk):
    professor = get_object_or_404(Professor, pk=pk)
    if request.method == "POST":
        user = professor.user
        professor.delete()
        user.delete()  
        return redirect('professor_list')
    return render(request, 'registration/professor_confirm_delete.html', {'professor': professor})

def manage_grades(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollments = Enrollment.objects.filter(course=course)
    if request.method == 'POST':
        formset = [GradeForm(request.POST, instance=enrollment) for enrollment in enrollments]
        if all([form.is_valid() for form in formset]):
            for form in formset:
                form.save()
            return redirect('course_list')
    else:
        formset = [GradeForm(instance=enrollment) for enrollment in enrollments]
    return render(request, 'registration/manage_grades.html', {'course': course, 'formset': formset})

def manage_classes(request):
    professor = request.user
    classes = Course.objects.filter(professor=professor)
    return render(request, 'manage_classes.html', {'classes': classes})

def course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course)
    return render(request, 'registration/course_students.html', {'course': course, 'enrollments': enrollments})

def assign_grade(request, enrollment_id):

    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    student_name = f"{enrollment.student.user.first_name} {enrollment.student.user.last_name}"  

    if request.method == 'POST':
        form = GradeForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade assigned successfully.')
            return redirect('view_students', course_id=enrollment.course.id)
    else:
        form = GradeForm(instance=enrollment)

    return render(request, 'registration/assign_grade.html', {'form': form, 'student_name': student_name})

def view_students(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    query = request.GET.get('q', '')
    if query:
        enrollments = Enrollment.objects.filter(
            Q(course=course),
            Q(student__first_name__icontains=query) | 
            Q(student__last_name__icontains=query) | 
            Q(student__email__icontains=query) | 
            Q(student__user__profile__id_number__icontains=query)
        )
    else:
        enrollments = Enrollment.objects.filter(course=course)
    return render(request, 'registration/view_students.html', {'course': course, 'enrollments': enrollments, 'query': query})

def admin_list(request):
    query = request.GET.get('q', '')
    if query:
        admins = Admin.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(user__profile__id_number__icontains=query)
        )
    else:
        admins = Admin.objects.all()
    
    return render(request, 'registration/admin_list.html', {'admins': admins, 'query': query})

def admin_create(request):
    if request.method == "POST":
        form = AdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_list')
        else:
            return JsonResponse(form.errors, status=400)
    else:
        form = AdminForm()
        return render(request, 'registration/admin_form.html', {'form': form})

def admin_update(request, pk):
    admin = get_object_or_404(Admin, pk=pk)
    if request.method == "POST":
        form = AdminForm(request.POST, instance=admin)
        if form.is_valid():
            form.save()
            return redirect('admin_list')
        else:
            return JsonResponse(form.errors, status=400)
    else:
        form = AdminForm(instance=admin)
    return render(request, 'registration/admin_form.html', {'form': form})

def admin_delete(request, pk):
    admin = get_object_or_404(Admin, pk=pk)
    if request.method == "POST":
        admin.delete()
        return redirect('admin_list')
    return render(request, 'registration/admin_confirm_delete.html', {'admin': admin})

def professor_update(request, pk):
    professor = get_object_or_404(Professor, pk=pk)
    if request.method == 'POST':
        form = ProfessorForm(request.POST, instance=professor)
        if form.is_valid():
            form.save()
            return redirect('professor_list')
    else:
        form = ProfessorForm(instance=professor)
    return render(request, 'registration/professor_form.html', {'form': form})

def view_profile(request):
    try:
        user_profile = request.user.profile
    except Profile.DoesNotExist:
        user_profile = Profile.objects.create(user=request.user)
    
    return render(request, 'registration/profile.html', {'user_profile': user_profile})

def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user.profile)
        if form.is_valid():
            try:
                profile = form.save(commit=False)
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.email = form.cleaned_data.get('email')
                
                if username:
                    user.username = username
                if password:
                    user.set_password(password)
                    update_session_auth_hash(request, user)
                
                user.save()
                profile.save()
                messages.success(request, 'Your profile was successfully updated!')
                return redirect('view_profile')
            except IntegrityError:
                form.add_error('username', 'This username is already taken. Please choose another one.')
    else:
        initial = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        form = ProfileForm(instance=user.profile, initial=initial)

    return render(request, 'registration/edit_profile.html', {'form': form})

def delete_profile_picture(request):
    user_profile = request.user.profile
    user_profile.profile_picture.delete()
    user_profile.save()
    return redirect('edit_profile')

def drop_class(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    course = enrollment.course

    if enrollment.student.user == request.user:
        enrollment.delete()
        course.available_seats += 1
        course.save()
        messages.success(request, f'You have successfully dropped {course.name}.')
    else:
        messages.error(request, 'You do not have permission to drop this class.')

    return redirect('student_schedule')

def assign_professor(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    query = request.GET.get('q', '')
    if query:
        professors = Professor.objects.filter(
            Q(user__first_name__icontains=query) | 
            Q(user__last_name__icontains=query) | 
            Q(user__email__icontains=query) | 
            Q(user__profile__id_number__icontains=query)
        )
    else:
        professors = Professor.objects.all()
    
    if request.method == 'POST':
        professor_id = request.POST.get('professor_id')
        if professor_id:
            professor = get_object_or_404(Professor, id=professor_id)
            course.professor = professor.user
            course.save()
            professor.courses.add(course)
            professor.save()
            
            for prof in Professor.objects.exclude(id=professor.id):
                if course in prof.courses.all():
                    prof.courses.remove(course)
                    prof.save()

            return redirect('course_list')

    return render(request, 'registration/assign_professor.html', {'course': course, 'professors': professors, 'query': query})

def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            if request.user.is_staff:  
                return redirect('course_list')
            elif hasattr(request.user, 'professor'):  
                return redirect('manage_classes')
    else:
        form = CourseForm(instance=course)
    return render(request, 'registration/edit_course.html', {'form': form})

def edit_course(request, course_id): 
    course = get_object_or_404(Course, pk=course_id)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('manage_classes')
    else:
        form = CourseForm(instance=course)
    return render(request, 'registration/edit_course.html', {'form': form, 'course': course})

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    query = request.GET.get('q', '')
    if query:
        course == course,
        enrollments = Enrollment.objects.filter(
                Q(student__first_name__icontains=query) | 
                Q(student__last_name__icontains=query) | 
                Q(student__email__icontains=query) | 
                Q(student__user__profile__id_number__icontains=query)
        )
    else:
        enrollments = Enrollment.objects.filter(course=course)
    
    students = [(enrollment.student, enrollment.grade) for enrollment in enrollments]
    return render(request, 'registration/course_detail.html', {'course': course, 'students': students, 'query': query})

def admin_list(request):
    query = request.GET.get('q', '')
    if query:
        admins = Admin.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(user__profile__id_number__icontains=query)
        )
    else:
        admins = Admin.objects.all()
    
    return render(request, 'registration/admin_list.html', {'admins': admins, 'query': query})

def view_user_profile(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if not hasattr(student.user, 'profile'):
        Profile.objects.create(user=student.user)
    return render(request, 'registration/view_user_profile.html', {'user': student.user})

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  
            return redirect('student_list')  
    else:
        form = StudentRegistrationForm()
    return render(request, 'registration/student_register.html', {'form': form})

def professor_register(request):
    if request.method == 'POST':
        form = ProfessorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  
            return redirect('professor_list')  
    else:
        form = ProfessorRegistrationForm()
    return render(request, 'registration/professor_register.html', {'form': form})

def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        course.delete()
        return redirect('course_list')
    
    return render(request, 'registration/course_confirm_delete.html', {'course': course})

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        user = student.user
        student.delete()
        user.delete()
        return redirect('student_list')
    return render(request, 'registration/student_confirm_delete.html', {'student': student})


def settings_view(request):
    user = request.user
    if request.method == 'POST':
        dark_mode = request.POST.get('dark_mode') == 'on'
        font_size = request.POST.get('font_size', 'medium')
        ui_preset = request.POST.get('ui_preset', 'classic')

        # Save user preferences to their profile
        user.profile.dark_mode = dark_mode
        user.profile.font_size = font_size
        user.profile.ui_preset = ui_preset
        user.profile.save()

        return redirect('settings')

    # Pass existing settings to the template to pre-fill the form
    context = {
        'settings': user.profile
    }
    return render(request, 'registration/settings.html', context)

def dashboard_view(request):
    student = request.user.student  # Assuming you have a Student model linked to the user
    courses = Enrollment.objects.filter(student=student).select_related('course')
    
    context = {
        'courses': [enrollment.course for enrollment in courses],
    }
    return render(request, 'dashboard.html', context)

def course_overview(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    assignments = Assignment.objects.filter(course=course)
    announcements = Announcement.objects.filter(course=course)
    # You can add other models (like exams, messages, grades) here.

    context = {
        'course': course,
        'assignments': assignments,
        'announcements': announcements,
    }
    return render(request, 'course_overview.html', context)

def class_detail(request, class_id):
    course = Course.objects.get(id=class_id)
    
    if request.method == 'POST':
        if 'add_assignment' in request.POST:
            assignment_form = AssignmentForm(request.POST)
            if assignment_form.is_valid():
                assignment = assignment_form.save(commit=False)
                assignment.course = course
                assignment.save()
        elif 'add_announcement' in request.POST:
            announcement_form = AnnouncementForm(request.POST)
            if announcement_form.is_valid():
                announcement = announcement_form.save(commit=False)
                announcement.course = course
                announcement.save()

    assignment_form = AssignmentForm()
    announcement_form = AnnouncementForm()
    assignments = Assignment.objects.filter(course=course)
    announcements = Announcement.objects.filter(course=course)
    
    context = {
        'course': course,
        'assignments': assignments,
        'announcements': announcements,
        'assignment_form': assignment_form,
        'announcement_form': announcement_form
    }
    return render(request, 'class_detail.html', context)

def get_assignments(request):
    assignments = Assignment.objects.filter(course__enrollment__student__user=request.user)
    events = []
    for assignment in assignments:
        events.append({
            'title': assignment.title,
            'start': assignment.due_date.strftime('%Y-%m-%d'),
        })
    return JsonResponse(events, safe=False)
