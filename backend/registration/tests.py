from django.test import TestCase, Client, override_settings
from django.urls import reverse
from registration.models import Course, Student

@override_settings(CSRF_COOKIE_SECURE=False)
class CourseTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            name='Mathematics',
            description='An introductory course to Mathematics',
            schedule='MWF 9:00-10:00',
            capacity=30
        )

    def test_course_list_view(self):
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mathematics')

    def test_course_create_view(self):
        data = {
            'name': 'Physics',
            'description': 'An introductory course to Physics',
            'schedule': 'TTh 10:00-11:30',
            'capacity': 25
        }
        response = self.client.post(reverse('course_create'), data)
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Course.objects.count(), 2)

@override_settings(CSRF_COOKIE_SECURE=False)
class StudentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com'
        )

    def test_student_list_view(self):
        url = reverse('student_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')

    def test_student_create_view(self):
        url = reverse('student_create')
        course = Course.objects.create(
            name='Test Course',
            description='A test course',
            schedule='MWF 10:00-11:00',
            capacity=30
        )
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'courses': [course.id]  
        }
        response = self.client.post(url, data)
        if response.status_code != 302:
            print(response.content)  
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Student.objects.count(), 2)
