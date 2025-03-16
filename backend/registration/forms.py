from django import forms
from django.contrib.auth.models import User
from .models import Profile, Student, Professor, Admin, Enrollment, Course, Assignment, Announcement, Message, Major
from django.contrib.auth.forms import UserCreationForm
import re

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'course_code',  # Make sure this matches the model
            'name',
            'description',
            'start_date',
            'end_date',
            'days',
            'start_time',
            'end_time',
            'session_type',
            'location',
            'available_seats',
            'capacity',
            'credits',
            'semester',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class GradeForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['grade']
        widgets = {
            'grade': forms.TextInput(attrs={'max_length': 4}),
        }


class StudentForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(queryset=Course.objects.none(), widget=forms.CheckboxSelectMultiple, required=False)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    major = forms.ModelChoiceField(queryset=Major.objects.all(), required=False)


    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password', 'courses', 'profile_picture', 'major']

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['courses'].queryset = Course.objects.filter(enrollment__student=self.instance)

    def save(self, commit=True):
        student = super(StudentForm, self).save(commit=False)
        user = student.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            student.save()
            self.save_m2m()
        return student

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

class ProfessorForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = Professor
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super(ProfessorForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        professor = super(ProfessorForm, self).save(commit=False)
        user = professor.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            professor.save()
            self.save_m2m()
        return professor

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

class AdminForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['first_name', 'last_name', 'email']

class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('professor', 'Professor'),
        ('admin', 'Admin'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    id_number = forms.CharField(max_length=20)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'id_number', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if username and User.objects.filter(username=username).exists():
            self.add_error('username', 'This username is already taken. Please choose another one.')

        if password1:
            if not password2:
                self.add_error('password2', 'You must confirm your password.')
            if password1 != password2:
                self.add_error('password2', 'Passwords do not match.')
            if len(password1) < 8:
                self.add_error('password1', 'Password must be at least 8 characters long.')
            if not re.search(r'\d', password1):
                self.add_error('password1', 'Password must contain at least one digit.')
            if not re.search(r'[A-Z]', password1):
                self.add_error('password1', 'Password must contain at least one uppercase letter.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            role = self.cleaned_data['role']
            id_number = self.cleaned_data['id_number']
            first_name = self.cleaned_data['first_name']
            last_name = self.cleaned_data['last_name']
            Profile.objects.create(user=user, id_number=id_number, first_name=first_name, last_name=last_name, role=role)
            if role == 'student':
                Student.objects.create(user=user, first_name=first_name, last_name=last_name, email=user.email)
            elif role == 'professor':
                Professor.objects.create(user=user, first_name=first_name, last_name=last_name, email=user.email)
            elif role == 'admin':
                Admin.objects.create(user=user, first_name=first_name, last_name=last_name, email=user.email)
        return user

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'course']

class ProfileForm(forms.ModelForm):
    username = forms.CharField(required=False)
    password1 = forms.CharField(widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(), required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'profile_picture', 'bio']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if username and self.instance.user.username != username:
            if User.objects.filter(username=username).exists():
                self.add_error('username', 'This username is already taken. Please choose another one.')

        if password1:
            if not password2:
                self.add_error('password2', 'You must confirm your password.')
            if password1 != password2:
                self.add_error('password2', 'Passwords do not match.')
            if len(password1) < 8:
                self.add_error('password1', 'Password must be at least 8 characters long.')
            if not re.search(r'\d', password1):
                self.add_error('password1', 'Password must contain at least one digit.')
            if not re.search(r'[A-Z]', password1):
                self.add_error('password1', 'Password must contain at least one uppercase letter.')

        return cleaned_data
    
class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label="First name")
    last_name = forms.CharField(max_length=30, label="Last name")
    email = forms.EmailField(max_length=254, label="Email address")
    id_number = forms.CharField(max_length=20, label="ID number")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'id_number', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(user=user, role='student', first_name=user.first_name, last_name=user.last_name, email=user.email, id_number=self.cleaned_data['id_number'])
            Student.objects.create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email)
        return user
    
class ProfessorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label="First name")
    last_name = forms.CharField(max_length=30, label="Last name")
    email = forms.EmailField(max_length=254, label="Email address")
    id_number = forms.CharField(max_length=20, label="ID number")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'id_number', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(user=user, role='professor', first_name=user.first_name, last_name=user.last_name, email=user.email, id_number=self.cleaned_data['id_number'])
            Professor.objects.create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email)
        return user
    
class AssignmentForm(forms.ModelForm):
    EXTRA_TIME_CHOICES = [
        (2, "2 days"),
        (3, "3 days"),
        (5, "5 days"),
        (7, "7 days"),
        (-1, "Unlimited time"),
        (0, "None"),
    ]

    extra_time_period = forms.ChoiceField(
        choices=EXTRA_TIME_CHOICES,
        initial=2,  # Default to 2 days
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Set an extra time period for late submissions."
    )

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'start_date', 'start_time', 'due_date', 'due_time', 'extra_time_period']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'due_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'details', 'start_date', 'start_time', 'due_date', 'due_time']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'due_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'content']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['receiver'].queryset = User.objects.filter(profile__role__in=['student', 'professor'])
        self.fields['receiver'].label_from_instance = lambda obj: f"{obj.profile.role.capitalize()} - {obj.username}"

class NewConversationForm(forms.Form):
    receiver = forms.ModelChoiceField(queryset=User.objects.all())



