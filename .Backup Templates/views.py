from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
from .models import Course, Student, Professor, Admin, Profile
from .forms import CourseForm, StudentForm, ProfessorForm, AdminForm
from .decorators import student_required, professor_required, admin_required

# User Authentication Views
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = request.POST.get('role')
            if role == 'student':
                Student.objects.create(user=user, first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'])
            elif role == 'professor':
                Professor.objects.create(user=user, first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'])
            elif role == 'admin':
                Admin.objects.create(user=user, first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'])
            Profile.objects.create(user=user, user_type=role)
            return redirect('login')
    else:
        form = UserCreationForm()
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
    return redirect('login')  # Ensure there is always a return value

def home_view(request):
    return render(request, 'home.html')

# Course Management Views
@admin_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'registration/course_list.html', {'courses': courses})

@admin_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'registration/course_form.html', {'form': form})

@admin_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'registration/course_form.html', {'form': form})

@admin_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        return redirect('course_list')
    return render(request, 'registration/course_confirm_delete.html', {'course': course})

# Student Management Views
@student_required
def student_list(request):
    if request.method == "GET":
        students = Student.objects.all()
        return render(request, 'registration/student_list.html', {'students': students})

@student_required
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')  # Redirect to student list after successful creation
        else:
            return JsonResponse(form.errors, status=400)
    else:
        form = StudentForm()
        return render(request, 'registration/student_form.html', {'form': form})

@student_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'registration/student_detail.html', {"student": student})

@student_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
        else:
            return JsonResponse(form.errors, status=400)
    else:
        form = StudentForm(instance=student)
    return render(request, 'registration/student_form.html', {'form': form})

@student_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        return redirect('student_list')
    return render(request, 'registration/student_confirm_delete.html', {'student': student})

# Professor Management Views
@professor_required
def professor_list(request):
    if request.method == "GET":
        professors = Professor.objects.all()
        return render(request, 'registration/professor_list.html', {'professors': professors})

@professor_required
def professor_create(request):
    if request.method == "POST":
        form = ProfessorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('professor_list')
        else:
            return JsonResponse(form.errors, status=400)
    else:
        form = ProfessorForm()
        return render(request, 'registration/professor_form.html', {'form': form})

@professor_required
def professor_update(request, pk):
    professor = get_object_or_404(Professor, pk=pk)
    if request.method == "POST":
        form = ProfessorForm(request.POST, instance=professor)
        if form.is_valid():
            form.save()
            return redirect('professor_list')
        else:
            return JsonResponse(form.errors, status=400)
    else:
        form = ProfessorForm(instance=professor)
    return render(request, 'registration/professor_form.html', {'form': form})

@professor_required
def professor_delete(request, pk):
    professor = get_object_or_404(Professor, pk=pk)
    if request.method == "POST":
        professor.delete()
        return redirect('professor_list')
    return render(request, 'registration/professor_confirm_delete.html', {'professor': professor})

# Admin Management Views
@admin_required
def admin_list(request):
    if request.method == "GET":
        admins = Admin.objects.all()
        return render(request, 'registration/admin_list.html', {'admins': admins})

@admin_required
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

@admin_required
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

@admin_required
def admin_delete(request, pk):
    admin = get_object_or_404(Admin, pk=pk)
    if request.method == "POST":
        admin.delete()
        return redirect('admin_list')
    return render(request, 'registration/admin_confirm_delete.html', {'admin': admin})
