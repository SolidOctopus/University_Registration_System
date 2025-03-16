from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

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

    def __str__(self):
        return self.name
    
class Major(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
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

class Assignment(models.Model):
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
        help_text="Extra time (in days) for late submissions. Set to 0 for no extra time, or -1 for unlimited time."
    )

    def __str__(self):
        return self.title

    def days_left(self):
        if self.extra_time_period == -1:  # Unlimited time
            return "UNLIMITED TIME"
        elif self.extra_time_period > 0:  # Extra time allowed
            late_due_date = self.due_date + timezone.timedelta(days=self.extra_time_period)
            now = timezone.now().date()  # Get today's date
            days_left = (late_due_date - now).days

            # If the due date is today, show "1 DAY LEFT" instead of "0 DAY(S) LEFT"
            if days_left == 0:
                return "1 DAY LEFT"
            elif days_left > 0:
                return f"{days_left} DAY(S) LEFT"
            else:
                return "CLOSED"
        else:  # No extra time
            if timezone.now().date() > self.due_date:
                return "CLOSED"
            else:
                return "NO EXTRA TIME"

    def check_and_close_assignment(self):
        """
        Automatically close the assignment if the late submission period has passed.
        """
        if self.extra_time_period == -1:  # Unlimited time, never close automatically
            return
        elif self.extra_time_period > 0:  # Extra time allowed
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


