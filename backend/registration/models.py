from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

class Major(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Course(models.Model):
    SEMESTER_CHOICES = [
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ]
    course_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.CharField(max_length=50, default='Monday')
    start_time = models.TimeField(default='09:00:00')
    end_time = models.TimeField(default='17:00:00')
    session_type = models.CharField(max_length=50, default='Regular')
    location = models.CharField(max_length=50, default='Campus')
    available_seats = models.IntegerField(default=0, null=True, blank=True)
    capacity = models.IntegerField(default=10)
    credits = models.IntegerField(default=3)
    professor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='courses', null=True, blank=True)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default='fall')
    majors = models.ManyToManyField(Major, related_name='courses')
    office_hours = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return self.name
    
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    courses = models.ManyToManyField(Course, through='Enrollment')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    id_number = models.CharField(max_length=20, default='default_id')
    major = models.ForeignKey('Major', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')



    def delete(self, *args, **kwargs):
        enrollments = Enrollment.objects.filter(student=self)
        for enrollment in enrollments:
            course = enrollment.course
            course.available_seats += 1
            course.save()
        super(Student, self).delete(*args, **kwargs)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} (Student)'
    
class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    courses = models.ManyToManyField(Course, blank=True, related_name='professors')
    id_number = models.CharField(max_length=20, default='default_id')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    ROLE_CHOICES = [
        ('professor', 'Professor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='professor')

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} (Professor)'

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=20, default='default_id')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    ROLE_CHOICES = [
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='admin')

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} (Admin)'

class Enrollment(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(auto_now_add=True)
    grade = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.user.username} enrolled in {self.course.name}"

class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('professor', 'Professor'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Fixed: 'User' instead of 'user', and 'on_delete'
    id_number = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')  # Fixed: '=' instead of '-'
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField()
    bio = models.TextField(blank=True, default='')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, default='')
    dark_mode = models.BooleanField(default=False)
    font_size = models.CharField(max_length=10, default='medium')
    ui_preset = models.CharField(max_length=20, default='classic')

    def __str__(self):
        return self.user.username
        
    @property
    def student(self):
        return getattr(self.user, 'student', None)


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Assignment(models.Model):

    ASSIGNMENT_TYPES = [
        ('assignment', 'Assignment'),
        ('homework', 'Homework'),
        ('project', 'Project'), 
        ('exam', 'Exam'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    due_date = models.DateField()
    due_time = models.TimeField(null=True, blank=True)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)  # Use string reference
    is_closed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    extra_time_period = models.IntegerField(
        default=2,  # Default to 2 days
        help_text="Extra time (in days) for late submissions. Set to 0 for no extra time."
    )
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='assignment_modules', null=True, blank=True)
    assignment_type = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_TYPES,
        default='assignment'
    )

    def get_type_display(self):
        """Returns the human-readable type name"""
        return dict(self.ASSIGNMENT_TYPES).get(self.assignment_type, self.assignment_type)

    def __str__(self):
        return self.title

    def days_left(self):
        now = timezone.now().date()  # Get today's date

        if self.extra_time_period > 0:  # Extra time allowed
            late_due_date = self.due_date + timezone.timedelta(days=self.extra_time_period)
            days_left = (late_due_date - now).days

            # Only show days left if the assignment is late or reopened
            if now > self.due_date:  # Assignment is late
                if days_left == 0:
                    return "1 DAY LEFT"
                elif days_left > 0:
                    return f"{days_left} DAY(S) LEFT"
                else:
                    return "CLOSED"
            else:
                return None  # Don't show days left if not late
        else:  # No extra time
            if now > self.due_date:
                return "CLOSED"
            else:
                return None  # Don't show days left if not late

    def check_and_close_assignment(self):
        """
        Automatically close the assignment if the late submission period has passed.
        """
        if self.extra_time_period > 0:  # Extra time allowed
            late_due_date = self.due_date + timezone.timedelta(days=self.extra_time_period)
            if timezone.now().date() > late_due_date:
                self.is_closed = True
                self.save()
        else:  # No extra time
            if timezone.now().date() > self.due_date:
                self.is_closed = True
                self.save()

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Submission for {self.assignment.title} by {self.student.user.username}"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    details = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    due_time = models.TimeField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='announcement_modules', null=True, blank=True)

    def __str__(self):
        return self.title
    
class Cart(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username}'s Cart: {self.course.name}"

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # For read receipts
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

class MajorRequirement(models.Model):
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='required_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='required_for_majors')
    
    class Meta:
        unique_together = ('major', 'course')

class UserAssignmentCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_assignments')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='user_completions')
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'assignment')  # Ensure each user can only have one completion record per assignment

    def __str__(self):
        return f"{self.user.username} - {self.assignment.title} (Completed: {self.is_completed})"
    
class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    numerical_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    letter_grade = models.CharField(max_length=2, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)  # Default but not auto_now_add
    updated_at = models.DateTimeField(auto_now=True)         # Still auto_now


    def save(self, *args, **kwargs):
        if self.numerical_grade is not None:
            self.letter_grade = self.numerical_to_letter_grade(self.numerical_grade)
        super().save(*args, **kwargs)

    @staticmethod
    def numerical_to_letter_grade(score):
        if score is None:
            return None
        try:
            score = float(score)
        except (ValueError, TypeError):
            return None
            
        if score >= 97: return 'A+'
        elif score >= 93: return 'A'
        elif score >= 90: return 'A-'
        elif score >= 87: return 'B+'
        elif score >= 83: return 'B'
        elif score >= 80: return 'B-'
        elif score >= 77: return 'C+'
        elif score >= 73: return 'C'
        elif score >= 70: return 'C-'
        elif score >= 67: return 'D+'
        elif score >= 63: return 'D'
        elif score >= 60: return 'D-'
        else: return 'F'