from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm
from django.http import JsonResponse
from .models import Course, Student, Professor, Admin, Profile, Enrollment, Assignment, Announcement, Cart, Message, Submission, UserAssignmentCompletion, Grade, Module, Major
from .forms import CourseForm, MajorChangeForm, StudentForm, ProfessorForm, AdminForm, GradeForm, ProfileForm, UserRegistrationForm, StudentRegistrationForm, ProfessorRegistrationForm, AssignmentForm, AnnouncementForm, ModuleForm, MajorForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, date, time
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    role = form.cleaned_data.get('role')
                    major = form.cleaned_data.get('major')
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
                            email=user.email,
                            major=major
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
    search_query = request.GET.get('search', '')
    courses = None  # Initialize as None to indicate no search results initially
    student = get_object_or_404(Student, user=request.user)  # Get the student object

    # Only perform search if there is a search query
    if search_query:
        courses = Course.objects.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(days__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(professor__first_name__icontains=search_query) |
            Q(professor__last_name__icontains=search_query)
        )

    # Fetch enrolled courses for the student if courses exist
    enrolled_courses = Enrollment.objects.filter(student=student).values_list('course', flat=True) if courses else []

    # Fetch courses in the student's cart
    cart_courses = Cart.objects.filter(student=student).values_list('course', flat=True) if courses else []

    context = {
        'courses': courses,
        'enrolled_courses': enrolled_courses,
        'cart_courses': cart_courses,  # Ensure this is passed to the template
        'search_query': search_query,
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
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            student.user = request.user
            student.save()
            form.save_m2m()
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'registration/student_form.html', {'form': form})

def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'registration/student_detail.html', {"student": student})

def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_detail', pk=pk)
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

def assign_grade(request, course_id, assignment_id, student_id):
    enrollment = get_object_or_404(Enrollment, course_id=course_id, student_id=student_id)
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            return redirect('professor_assignment_details', course_id=course_id, assignment_id=assignment_id)
    else:
        form = GradeForm(instance=enrollment)
    
    context = {
        'form': form,
        'course_id': course_id,
        'assignment_id': assignment_id,
        'student': enrollment.student,
    }
    return render(request, 'assign_grade.html', context)

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
            messages.success(request, "Course updated successfully.")
            return redirect('course_list')  # Redirect after successful save
        else:
            messages.error(request, "Error updating course. Please check your input.")
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

def forgot_password_view(request):
    form = PasswordResetForm()
    return render(request, 'forgot_password.html')


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






def get_semester_dates(semester, year):
    return {
        'fall': {'start': date(year, 8, 26), 'end': date(year, 12, 14)},
        'spring': {'start': date(year, 1, 10), 'end': date(year, 4, 25)},
        'summer': {'start': date(year, 5, 15), 'end': date(year, 8, 10)},
    }[semester]


def get_events_by_date(courses, start_date, end_date):
    assignments = Assignment.objects.filter(course__in=courses, due_date__range=(start_date, end_date)).order_by('due_date')
    announcements = Announcement.objects.filter(course__in=courses, posted_at__date__range=(start_date, end_date)).order_by('posted_at')
    return assignments, announcements


def group_events_by_date(assignments, announcements, start_date, end_date):
    days = {}
    # Generate a dictionary with all dates in the range as keys
    for x in range((end_date - start_date).days + 1):
        current_day = (start_date + timedelta(days=x)).strftime("%Y-%m-%d")
        days[current_day] = {'assignments': [], 'announcements': []}

    # Populate the dictionary with assignments and announcements
    for assignment in assignments:
        day_key = assignment.due_date.strftime("%Y-%m-%d")
        days[day_key]['assignments'].append({
            'title': assignment.title,
            'course_name': assignment.course.name,
            'due_date': assignment.due_date
        })

    for announcement in announcements:
        day_key = announcement.posted_at.strftime("%Y-%m-%d")
        days[day_key]['announcements'].append({
            'title': announcement.title,
            'details': announcement.details,
            'course_name': announcement.course.name,
            'date_posted': announcement.posted_at
        })

    return days


def group_events_by_week(events_by_date):
    weeks = {}
    for day_key, events in events_by_date.items():
        # Parse the date and calculate the start of the week (Monday)
        day_date = date.fromisoformat(day_key)
        week_start = day_date - timedelta(days=day_date.weekday())
        week_end = week_start + timedelta(days=6)
        week_key = f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"

        if week_key not in weeks:
            weeks[week_key] = {'assignments': [], 'announcements': []}

        # Append assignments and announcements to the corresponding week
        weeks[week_key]['assignments'].extend(events['assignments'])
        weeks[week_key]['announcements'].extend(events['announcements'])

    return weeks



def merge_empty_and_non_empty(events_by_date, empty_ranges):
    # Create a merged dictionary that includes both empty ranges and non-empty days, excluding individual empty days within grouped ranges.
    merged_events = {}

    # Generate a set of all days within grouped empty ranges for easier exclusion
    excluded_days = set()
    for start, end in empty_ranges:
        try:
            # Parse only the start and end dates correctly
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)
            for day_offset in range((end_date - start_date).days + 1):
                excluded_days.add((start_date + timedelta(days=day_offset)).strftime("%Y-%m-%d"))
        except ValueError:
            continue  # Skip if there's any issue parsing the date

    # Create merged events without including the excluded individual empty days
    for key in sorted(events_by_date.keys() | set([f"{start} to {end}" for start, end in empty_ranges])):
        if key in excluded_days:
            continue  # Skip individual empty days that are part of a grouped range
        if key in events_by_date:
            merged_events[key] = events_by_date[key]
        else:
            merged_events[key] = {'assignments': [], 'announcements': []}

    return merged_events

def get_grouped_empty_week_ranges(events_by_week):
    grouped_empty_weeks = []
    start_empty_week = None
    sorted_weeks = sorted(events_by_week.keys())  # Ensure weeks are sorted chronologically

    for index, week_key in enumerate(sorted_weeks):
        if not events_by_week[week_key]['assignments'] and not events_by_week[week_key]['announcements']:
            if start_empty_week is None:
                start_empty_week = week_key  # Start tracking an empty week range
        else:
            if start_empty_week:
                # Close the empty week range and reset start_empty_week
                grouped_empty_weeks.append((start_empty_week.split(" to ")[0], sorted_weeks[index - 1].split(" to ")[1]))
                start_empty_week = None

    # Handle the case where the last week range is empty
    if start_empty_week:
        grouped_empty_weeks.append((start_empty_week.split(" to ")[0], sorted_weeks[-1].split(" to ")[1]))

    return grouped_empty_weeks

def get_grouped_empty_ranges(events_by_date):
    grouped_empty_days = []
    start_empty_date = None
    sorted_days = sorted(events_by_date.keys())  # Ensure days are sorted chronologically

    for index, day_key in enumerate(sorted_days):
        is_empty = not events_by_date[day_key]['assignments'] and not events_by_date[day_key]['announcements']
        next_day_is_empty = index + 1 < len(sorted_days) and not events_by_date[sorted_days[index + 1]]['assignments'] and not events_by_date[sorted_days[index + 1]]['announcements']

        if is_empty:
            if start_empty_date is None:
                start_empty_date = day_key  # Start tracking an empty range
            # If the next day is not empty, we have reached the end of an empty range
            if not next_day_is_empty:
                if start_empty_date != day_key:
                    grouped_empty_days.append((start_empty_date, day_key))  # Add the empty range
                start_empty_date = None  # Reset the start_empty_date
        else:
            if start_empty_date and start_empty_date != day_key:
                grouped_empty_days.append((start_empty_date, sorted_days[index - 1]))  # Close the empty range
                start_empty_date = None

    # Handle the case where the last date range is empty
    if start_empty_date:
        grouped_empty_days.append((start_empty_date, sorted_days[-1]))

    return grouped_empty_days



def format_events_for_template(events_dict):
    formatted_list = []
    for key, value in events_dict.items():
        formatted_list.append({
            'day': key,  # For daily assignments, use the date as 'day'
            'week': key,  # For weekly assignments, use the week range as 'week'
            'assignments': value['assignments'],
            'announcements': value['announcements']
        })
    return formatted_list


def dashboard_view(request):
    student = request.user.student
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    courses = [enrollment.course for enrollment in enrollments]

    if not courses:
        messages.info(request, "You are not enrolled in any courses.")
        return render(request, 'dashboard.html')

    semester = courses[0].semester
    today = date.today()
    start_date, end_date = get_semester_dates(semester, today.year).values()

    # Get events and group them by date and week
    assignments, announcements = get_events_by_date(courses, start_date, end_date)
    daily_assignments = group_events_by_date(assignments, announcements, start_date, end_date)
    weekly_assignments = group_events_by_week(daily_assignments)

    # Group empty ranges for daily and weekly views
    grouped_empty_days = get_grouped_empty_ranges(daily_assignments)
    grouped_empty_weeks = get_grouped_empty_week_ranges(weekly_assignments)  # Use the new function

    # Merge grouped empty ranges with existing events in the correct order
    merged_daily_assignments = merge_empty_and_non_empty(daily_assignments, grouped_empty_days)
    merged_weekly_assignments = merge_empty_and_non_empty(weekly_assignments, grouped_empty_weeks)

    # Format for template compatibility
    daily_assignments_list = format_events_for_template(merged_daily_assignments)
    weekly_assignments_list = format_events_for_template(merged_weekly_assignments)

    context = {
        'daily_assignments': daily_assignments_list,
        'weekly_assignments': weekly_assignments_list,
        'grouped_empty_days': grouped_empty_days,
        'grouped_empty_weeks': grouped_empty_weeks,
        'courses': courses,
        'semester': semester,
        'today': today.strftime('%Y-%m-%d'),
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

def create_assignment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    assignments = Assignment.objects.filter(course=course)

    if request.method == 'POST' and 'add_assignment' in request.POST:
        assignment_form = AssignmentForm(request.POST)
        if assignment_form.is_valid():
            assignment = assignment_form.save(commit=False)
            assignment.course = course
            # Set default times if not provided
            assignment.start_time = assignment.start_time or time(0, 0)  # 12:00 AM
            assignment.due_time = assignment.due_time or time(23, 59)  # 11:59 PM
            assignment.save()
            # Check and close the assignment if the late period is exceeded
            assignment.check_and_close_assignment()
            return redirect('course_assignments', course_id=course.id)  # Prevent duplicate submissions on refresh
    else:
        assignment_form = AssignmentForm(initial={'start_time': time(0, 0), 'due_time': time(23, 59)})

    context = {
        'course': course,
        'assignments': assignments,
        'assignment_form': assignment_form,
    }
    return render(request, 'create_assignment.html', context)

@login_required
def create_announcement(request, course_id):
    # Fetch the course object
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        # If the form is submitted, process the data
        announcement_form = AnnouncementForm(request.POST)
        if announcement_form.is_valid():
            # Save the announcement and associate it with the course
            announcement = announcement_form.save(commit=False)
            announcement.course = course
            announcement.save()

            # Redirect to the course_announcements page after successful creation
            return redirect('course_announcements', course_id=course.id)
    else:
        # If it's a GET request, initialize an empty form
        announcement_form = AnnouncementForm()

    # Render the create_announcement template with the form
    context = {
        'course': course,
        'announcement_form': announcement_form,
    }
    return render(request, 'create_announcement.html', context)

@login_required
def get_assignments(request):
    student = request.user.student
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    assignments = Assignment.objects.filter(
        course__in=[enrollment.course for enrollment in enrollments]
    ).order_by('due_date')

    # Create a dictionary to store assignments grouped by week
    weeks = {}
    today = datetime.now().date()
    start_date = today - timedelta(days=today.weekday())  # Start from the beginning of this week
    end_date = start_date + timedelta(days=7 * 6)  # Up to 6 weeks in the future

    # Initialize all weeks in the date range with "Nothing Planned Yet"
    current_week_start = start_date
    while current_week_start <= end_date:
        week_key = current_week_start.strftime("%B %d, %Y") + " to " + (current_week_start + timedelta(days=6)).strftime("%B %d, %Y")
        weeks[week_key] = []
        current_week_start += timedelta(days=7)

    # Group assignments into weeks
    for assignment in assignments:
        week_start = assignment.due_date - timedelta(days=assignment.due_date.weekday())  # Get start of the week for the due date
        week_key = week_start.strftime("%B %d, %Y") + " to " + (week_start + timedelta(days=6)).strftime("%B %d, %Y")
        if week_key in weeks:
            weeks[week_key].append(assignment)
        else:
            weeks[week_key] = [assignment]

    # Prepare the JSON response with weekly grouping
    response = []
    for week, assignments in weeks.items():
        response.append({
            'week': week,
            'assignments': [{'title': assignment.title, 'due_date': assignment.due_date.strftime('%Y-%m-%d')} for assignment in assignments],
        })

    return JsonResponse(response, safe=False)

def professor_info(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    professor = course.professor.professor
    can_edit = (request.user == professor.user)
    
    if request.method == 'POST' and can_edit:
        # Update office hours (course-specific)
        office_hours = request.POST.get('office_hours', '').strip()
        course.office_hours = office_hours if office_hours else 'Not specified'
        course.save()
        
        # Update biography (profile-specific)
        bio = request.POST.get('bio', '').strip()
        profile = professor.user.profile
        profile.bio = bio if bio else 'No biography available'
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('professor_info', course_id=course_id)

    context = {
        'course': course,
        'professor': professor,
        'can_edit': can_edit,
    }
    return render(request, 'professor_info.html', context)

def course_syllabus(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    can_edit = request.user == course.professor
    
    # Load syllabus data from course.description (stored as JSON)
    try:
        syllabus_data = json.loads(course.description) if course.description else {}
    except:
        syllabus_data = {}
    
    if request.method == 'POST' and can_edit:
        syllabus_data = {
            'description': request.POST.get('description', ''),
            'objectives': request.POST.get('objectives', ''),
            'grading_policy': request.POST.get('grading_policy', '')
        }
        course.description = json.dumps(syllabus_data)
        course.save()
        return redirect('course_syllabus', course_id=course.id)
    
    context = {
        'course': course,
        'syllabus_data': syllabus_data,
        'can_edit': can_edit
    }
    return render(request, 'course_syllabus.html', context)

def course_modules(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'course_modules.html', {'course': course})

def course_assignments(request, course_id):
    # Fetch the course object using the course_id
    course = get_object_or_404(Course, id=course_id)
    
    # Fetch all assignments for the course
    assignments = Assignment.objects.filter(course=course)
    current_date = timezone.now().date()

    # Precompute completion status for the current user
    for assignment in assignments:
        assignment.is_completed_for_user = UserAssignmentCompletion.objects.filter(
            user=request.user,
            assignment=assignment,
            is_completed=True
        ).exists()

    context = {
        'course': course,  # Pass the course object to the template
        'assignments': assignments,
        'current_date': current_date,
    }
    return render(request, 'course_assignments.html', context)

def course_announcements(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    announcements = course.announcement_set.all()
    return render(request, 'course_announcements.html', {'course': course, 'announcements': announcements})


def course_grades_students(request, course_id):
    # Fetch the course
    course = get_object_or_404(Course, id=course_id)

    # Fetch grades for the logged-in student
    grades = Grade.objects.filter(course=course, student=request.user)

    # Render the student-specific grades template
    return render(request, 'course_grades_students.html', {
        'course': course,
        'grades': grades
    })

def course_grades_professors(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    assignments = Assignment.objects.filter(course=course)
    
    # Get selected assignment
    selected_assignment = None
    assignment_id = request.GET.get('assignment')
    if assignment_id:
        selected_assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Handle grade submission
    if request.method == 'POST' and selected_assignment:
        try:
            with transaction.atomic():
                for enrollment in Enrollment.objects.filter(course=course):
                    student = enrollment.student
                    grade_key = f'grade_{student.user.id}'
                    numerical_grade = request.POST.get(grade_key)
                    
                    if numerical_grade and numerical_grade.strip():
                        try:
                            numerical_grade = float(numerical_grade)
                            if 0 <= numerical_grade <= 100:
                                Grade.objects.update_or_create(
                                    student=student.user,
                                    assignment=selected_assignment,
                                    course=course,
                                    defaults={
                                        'numerical_grade': numerical_grade,
                                        # letter_grade will be auto-set in save()
                                    }
                                )
                        except ValueError:
                            pass  # Ignore invalid grade entries
                
                messages.success(request, 'Grades saved successfully!')
                return redirect('course_grades_professors', course_id=course.id)
        except Exception as e:
            messages.error(request, f'Error saving grades: {str(e)}')
    
    # Prepare enrollment data with submission status
    enrollments = []
    for enrollment in Enrollment.objects.filter(course=course).select_related('student'):
        student_data = {
            'user': enrollment.student.user,
            'has_submitted': Submission.objects.filter(
                assignment=selected_assignment,
                student=enrollment.student
            ).exists() if selected_assignment else False,
            'grades': Grade.objects.filter(
                student=enrollment.student.user,
                course=course,
                assignment=selected_assignment
            ).first() if selected_assignment else None
        }
        enrollments.append({
            'student': student_data,
            'enrollment': enrollment
        })
    
    context = {
        'course': course,
        'assignments': assignments,
        'selected_assignment': selected_assignment,
        'enrollments': enrollments,
    }
    return render(request, 'course_grades_professors.html', context)

def shopping_cart_view(request):
    # Get the current student's cart items
    student = request.user.student  # Retrieve the student object
    cart_items = Cart.objects.filter(student=student).select_related('course')  # Use Cart model

    context = {
        'cart_items': cart_items,  # Pass the cart items to the template
    }
    return render(request, 'shopping_cart.html', context)


def my_requirements_view(request):
    return render(request, 'my_requirements.html')

def financials_view(request):
    return render(request, 'financials.html')

def add_to_cart(request, course_id):
    if request.method == 'POST':
        course = Course.objects.get(pk=course_id)
        student = request.user.student  # Get the student object

        # Create or get Cart object based on the student and course
        cart_item, created = Cart.objects.get_or_create(student=student, course=course)
        
        if created:
            message = 'Course successfully added to your cart.'
            success = True
        else:
            message = 'This course is already in your cart.'
            success = False

        # Return the updated cart count
        cart_count = Cart.objects.filter(student=student).count()

        return JsonResponse({'success': success, 'message': message, 'cart_count': cart_count})

def remove_from_cart(request, cart_id):
    if request.method == 'POST':
        # Retrieve the cart item using the ID
        cart_item = get_object_or_404(Cart, id=cart_id)
        
        # Delete the item from the cart
        cart_item.delete()
        
        # Return a success response
        return JsonResponse({'success': True})
    
    # If method is not POST, return an error response
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def enroll_all_courses(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        selected_courses_ids = request.POST.getlist('selected_courses')
        cart_items = Cart.objects.filter(student=student, course__pk__in=selected_courses_ids)
        
        success = True
        message_list = []
        
        for cart_item in cart_items:
            course = cart_item.course
            if course.available_seats > 0 and student.major not in course.majors.all():  # Updated this line
                major_names = ", ".join([major.name for major in course.majors.all()])
                messages.error(request, f'Sorry - only students with the {major_names} major(s) can enroll in this course.')
                message_list.append({'level': 'error', 'message': f'Sorry - only students with the {major_names} major(s) can enroll in this course.'})
                success = False
            elif course.available_seats > 0 and student.major in course.majors.all():  # Updated this line
                Enrollment.objects.create(student=student, course=course)
                course.available_seats -= 1
                course.save()
                cart_item.delete()
        
        if success:
            messages.success(request, 'You have successfully enrolled in the selected courses.')
            message_list.append({'level': 'success', 'message': 'You have successfully enrolled in the selected courses.'})
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': success,
                'messages': message_list
            })
            
        # If not AJAX, redirect as before
        if success:
            return redirect('student_schedule')
        return redirect('shopping_cart')
        
    return redirect('shopping_cart')

def get_cart_count(request):
    student = request.user.student  # Get the student object
    cart_count = Cart.objects.filter(student=student).count()  # Use Cart model
    return JsonResponse({'cart_count': cart_count})

def change_major(request):
    user = request.user 
    student = user.student  
    
    if request.method == 'POST':
        form = MajorChangeForm(request.POST)
        if form.is_valid():
            student.major = form.cleaned_data['major']
            student.save()
            return redirect('view_profile')

    else:
        form = MajorChangeForm()

    return render(request, 'registration/change_major.html', {'form': form})

@login_required
def message_list(request):
    other_user = None
    other_user_id = request.GET.get('user')
    messages = None

    if other_user_id:
        other_user = get_object_or_404(User, id=other_user_id)
        # Mark messages as read
        Message.objects.filter(receiver=request.user, sender=other_user).update(is_read=True)
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=other_user)) | 
            (Q(receiver=request.user) & Q(sender=other_user))
        ).order_by('timestamp')

    # Get all users who are either students or professors (exclude admins)
    all_users = User.objects.filter(profile__role__in=['student', 'professor']).exclude(id=request.user.id)
    
    # Get all users who have interacted with the current user
    interacted_users = User.objects.filter(
        Q(pk__in=Message.objects.filter(sender=request.user).values('receiver')) | 
        Q(pk__in=Message.objects.filter(receiver=request.user).values('sender'))
    ).exclude(id=request.user.id).distinct()

    # Fetch the last message and unread message count for each user
    for user in interacted_users:
        user.last_message = Message.objects.filter(
            (Q(sender=user, receiver=request.user) | Q(sender=request.user, receiver=user))
        ).order_by('-timestamp').first()  # Attach directly to user

        user.unread_count = Message.objects.filter(sender=user, receiver=request.user, is_read=False).count()


    return render(request, 'message_list.html', {
        'messages': messages,
        'users': interacted_users,
        'other_user': other_user,
        'all_users': all_users,
    })

@login_required
def send_message(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=recipient, content=content)
        return redirect(f'/messages/?user={recipient_id}')

    return JsonResponse({'status': 'Message sent'})

@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    replies = message.replies.all()
    return render(request, 'message_detail.html', {'message': message, 'replies': replies})

@login_required
def start_new_conversation(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        receiver = get_object_or_404(User, id=receiver_id)
        Message.objects.create(sender=request.user, receiver=receiver, content='New conversation started.')
        return redirect(f'/messages/?user={receiver_id}')


@login_required
def delete_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) | 
        (Q(receiver=request.user) & Q(sender=other_user))
    ).delete()
    return redirect('message_list')

@login_required
def assignment_details(request, course_id, assignment_id):
    # Fetch the assignment object
    assignment = get_object_or_404(Assignment, id=assignment_id, course_id=course_id)
    
    # Check if the assignment is completed for the current user
    is_completed_for_user = UserAssignmentCompletion.objects.filter(
        user=request.user,
        assignment=assignment,
        is_completed=True
    ).exists()

    context = {
        'assignment': assignment,
        'is_completed_for_user': is_completed_for_user,  # Pass the completion status to the template
    }
    return render(request, 'assignment_details.html', context)

@login_required
def edit_assignment(request, course_id, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, course_id=course_id)

    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            # Check and close the assignment if the late period is exceeded
            assignment.check_and_close_assignment()
            return redirect('course_assignments', course_id=course_id)
    else:
        form = AssignmentForm(instance=assignment)

    # Debugging: Print context variables
    print(f"Course ID: {course_id}, Assignment ID: {assignment.id}")

    return render(request, 'edit_assignment.html', {
        'form': form,
        'course_id': course_id,  # Pass course_id to the template
        'assignment': assignment,  # Pass assignment to the template
    })

@login_required
def close_assignment(request, course_id, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, course_id=course_id)
    assignment.is_closed = not assignment.is_closed  # Toggle the is_closed status
    assignment.save()
    return redirect('edit_assignment', course_id=course_id, assignment_id=assignment_id)

@login_required
def complete_assignment(request, course_id, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, course_id=course_id)
    assignment.is_completed = True
    assignment.save()
    return redirect('course_assignments', course_id=course_id)

@login_required
def submit_assignment(request, course_id, assignment_id):
    if request.method == 'POST':
        # Fetch the assignment object
        assignment = get_object_or_404(Assignment, id=assignment_id, course_id=course_id)
        user = request.user

        # Ensure the user is a student
        if user.profile.role != 'student':
            messages.error(request, "Only students can submit assignments.")
            return redirect('course_assignments', course_id=course_id)

        # Create or update the UserAssignmentCompletion record
        completion, created = UserAssignmentCompletion.objects.get_or_create(
            user=user,
            assignment=assignment,
            defaults={'is_completed': True}  # Mark as completed by default
        )
        if not created:
            completion.is_completed = True
            completion.save()

        # Create the submission record
        Submission.objects.create(
            assignment=assignment,
            student=user.student,
            content=request.POST.get('content')  # Assuming content is submitted via a form
        )

        # Notify the user of successful submission
        messages.success(request, "Assignment submitted successfully!")
        return redirect('course_assignments', course_id=course_id)

    # If the request method is not POST, redirect to the assignment details page
    return redirect('course_assignments', course_id=course_id)

@login_required
def delete_assignment(request, course_id, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, course_id=course_id)
    assignment.delete()
    return redirect('course_assignments', course_id=course_id)

@login_required
def reopen_assignment(request, course_id, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, course_id=course_id)
    
    # Set the due date to 1 day from now
    assignment.due_date = timezone.now().date() + timezone.timedelta(days=1)
    assignment.extra_time_period = 1  # Set extra time to 1 day
    assignment.is_closed = False
    assignment.save()
    
    return redirect('assignment_details', course_id=course_id, assignment_id=assignment_id)

def professor_assignment_details(request, course_id, assignment_id):
    # Fetch the assignment and course
    assignment = get_object_or_404(Assignment, id=assignment_id, course_id=course_id)
    course = assignment.course

    # Fetch all students enrolled in the course
    enrollments = Enrollment.objects.filter(course=course).select_related('student')

    # Fetch submissions for the assignment
    submissions = Submission.objects.filter(assignment=assignment).select_related('student')

    # Create a list of students with their submission status and grade
    students = []
    for enrollment in enrollments:
        student = enrollment.student
        submission = submissions.filter(student=student).first()
        students.append({
            'student': student,
            'submission': submission,
            'grade': enrollment.grade,  # Grade from the Enrollment model
        })

    context = {
        'course': course,
        'assignment': assignment,
        'students': students,
    }
    return render(request, 'professor_assignment_details.html', context)

def edit_announcement(request, course_id, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id, course_id=course_id)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            return redirect('course_announcements', course_id=course_id)
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'edit_announcement.html', {'form': form, 'course_id': course_id, 'announcement': announcement})

def delete_announcement(request, course_id, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id, course_id=course_id)
    announcement.delete()
    return redirect('course_announcements', course_id=course_id)

def announcement_detail(request, course_id, announcement_id):
    # Fetch the announcement object
    announcement = get_object_or_404(Announcement, id=announcement_id, course_id=course_id)
    
    # Render the announcement detail template
    return render(request, 'announcement_detail.html', {'announcement': announcement})

def course_modules(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.all()
    return render(request, 'course_modules.html', {'course': course, 'modules': modules})

@login_required
def create_module(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            
            # Handle selected assignments
            assignment_ids = request.POST.getlist('assignments')
            assignments = Assignment.objects.filter(id__in=assignment_ids)
            module.assignment_modules.set(assignments)
            
            # Handle selected announcements
            announcement_ids = request.POST.getlist('announcements')
            announcements = Announcement.objects.filter(id__in=announcement_ids)
            module.announcement_modules.set(announcements)
            
            messages.success(request, 'Module created successfully!')
            return redirect('course_modules', course_id=course.id)
    else:
        form = ModuleForm()
    
    # Get all assignments and announcements for this course
    course_assignments = Assignment.objects.filter(course=course)
    course_announcements = Announcement.objects.filter(course=course)
    
    context = {
        'form': form,
        'course': course,
        'course_assignments': course_assignments,
        'course_announcements': course_announcements,
    }
    return render(request, 'create_module.html', context)

def edit_module(request, course_id, module_id):
    module = get_object_or_404(Module, id=module_id)
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            module = form.save()
            
            # Get the actual Assignment objects from the IDs
            assignment_ids = request.POST.getlist('assignments')
            assignments = Assignment.objects.filter(id__in=assignment_ids)
            module.assignment_modules.set(assignments)
            
            # Get the actual Announcement objects from the IDs
            announcement_ids = request.POST.getlist('announcements')
            announcements = Announcement.objects.filter(id__in=announcement_ids)
            module.announcement_modules.set(announcements)
            
            return redirect('course_modules', course_id=course_id)
    
    form = ModuleForm(instance=module)
    course_assignments = Assignment.objects.filter(course=course)
    course_announcements = Announcement.objects.filter(course=course)
    
    return render(request, 'edit_module.html', {
        'form': form,
        'module': module,
        'course_assignments': course_assignments,
        'course_announcements': course_announcements,
        'course': course
    })

def delete_module(request, course_id, module_id):
    module = get_object_or_404(Module, id=module_id)
    module.delete()
    return redirect('course_modules', course_id=course_id)

def module_detail(request, course_id, module_id):
    course = get_object_or_404(Course, id=course_id)
    module = get_object_or_404(Module, id=module_id, course=course)
    current_date = timezone.now().date()
    
    context = {
        'course': course,
        'module': module,
        'current_date': current_date,
    }
    return render(request, 'module_detail.html', context)
def major_list(request):
    majors = Major.objects.all()
    return render(request, 'major_list.html', {'majors': majors})

def major_create(request):
    if request.method == 'POST':
        form = MajorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('major_list')
    else:
        form = MajorForm()
    return render(request, 'major_form.html', {'form': form})

def major_edit(request, pk):
    major = get_object_or_404(Major, pk=pk)
    if request.method == 'POST':
        form = MajorForm(request.POST, instance=major)
        if form.is_valid():
            form.save()
            return redirect('major_list')
    else:
        form = MajorForm(instance=major)
    return render(request, 'major_form.html', {'form': form})

def major_delete(request, pk):
    major = get_object_or_404(Major, pk=pk)
    if request.method == 'POST':
        major.delete()
        return redirect('major_list')
    return render(request, 'major_confirm_delete.html', {'major': major})

def major_detail(request, pk):
    major = get_object_or_404(Major, pk=pk)
    return render(request, 'major_detail.html', {'major': major})