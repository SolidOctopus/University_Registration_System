from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField(default='2024-01-01')
    end_date = models.DateField(default='2024-01-01')
    days = models.CharField(max_length=50, default='Monday')
    start_time = models.TimeField(default='09:00:00')
    end_time = models.TimeField(default='17:00:00')
    session_type = models.CharField(max_length=50, default='Regular')
    location = models.CharField(max_length=50, default='Campus')
    available_seats = models.IntegerField(default=0, null=True, blank=True)
    capacity = models.IntegerField(default=10)
    credits = models.IntegerField(default=3)
    professor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='courses', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  
            self.available_seats = self.capacity
        super(Course, self).save(*args, **kwargs)

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

    def delete(self, *args, **kwargs):
        enrollments = Enrollment.objects.filter(student=self)
        for enrollment in enrollments:
            course = enrollment.course
            course.available_seats += 1
            course.save()
        super(Student, self).delete(*args, **kwargs)

    def __str__(self):
        return self.first_name + " " + self.last_name

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
        return self.first_name + " " + self.last_name

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    ROLE_CHOICES = [
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='admin')

    def __str__(self):
        return self.first_name + " " + self.last_name

class Enrollment(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(auto_now_add=True)
    grade = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.name}"

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dark_mode = models.BooleanField(default=False)
    font_size = models.CharField(max_length=10, default='medium')
    ui_preset = models.CharField(max_length=20, default='classic')
    
    def __str__(self):
        return self.user.username
