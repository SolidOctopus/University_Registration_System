from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    register_view, login_view, logout_view, home_view,
    course_list, course_create, course_edit, course_delete, enroll_in_course, view_enrollments, 
    assign_grade, student_list, student_create, student_update, student_delete, student_detail,
    professor_list, professor_create, professor_update, professor_delete, enroll_course,
    admin_list, admin_create, admin_update, admin_delete,  available_courses, student_schedule,
    edit_course,  manage_classes, course_students, view_students, view_profile, edit_profile,
    drop_class, assign_professor, course_detail, view_user_profile, student_register, professor_register, 
    settings_view, dashboard_view, course_overview, class_detail, get_assignments, professor_info, course_syllabus,
    course_modules, course_assignments, course_announcements, course_grades, 
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('home/', home_view, name='home'),  
    path('courses/', course_list, name='course_list'),
    path('courses/create/', course_create, name='course_create'),
    path('courses/edit/<int:pk>/', course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', course_delete, name='course_delete'),
    path('courses/<int:course_id>/enroll/', enroll_in_course, name='enroll_in_course'),
    path('students/', student_list, name='student_list'),
    path('students/create/', student_create, name='student_create'),
    path('students/<int:pk>/update/', student_update, name='student_update'),
    path('students/<int:pk>/delete/', student_delete, name='student_delete'),
    path('students/<int:pk>/', student_detail, name='student_detail'),
    path('professors/', professor_list, name='professor_list'),
    path('professors/create/', professor_create, name='professor_create'),
    path('professor/<int:pk>/edit/', professor_update, name='edit_professor'),
    path('professors/<int:pk>/update/', professor_update, name='professor_update'),
    path('professors/<int:pk>/delete/', professor_delete, name='professor_delete'),
    path('enrollments/<int:enrollment_id>/assign_grade/', assign_grade, name='assign_grade'),
    path('enrollments/', view_enrollments, name='view_enrollments'),
    path('admins/', admin_list, name='admin_list'),
    path('admins/create/', admin_create, name='admin_create'),
    path('admins/<int:pk>/update/', admin_update, name='admin_update'),
    path('admins/<int:pk>/delete/', admin_delete, name='admin_delete'),
    path('available-courses/', available_courses, name='available_courses'),
    path('my-schedule/', student_schedule, name='student_schedule'),
    path('enroll-course/<int:pk>/', enroll_course, name='enroll_course'),
    path('edit-course/<int:course_id>/', edit_course, name='edit_course'),
    path('manage-classes/', manage_classes, name='manage_classes'),
    path('manage-classes/<int:course_id>/', course_students, name='course_students'),
    path('assign-grade/<int:enrollment_id>/', assign_grade, name='assign_grade'),
    path('courses/<int:course_id>/students/', view_students, name='view_students'),
    path('profile/', view_profile, name='view_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('drop-class/<int:enrollment_id>/',drop_class, name='drop_class'),
    path('courses/<int:course_id>/assign_professor/', assign_professor, name='assign_professor'),
    path('courses/<int:pk>/', course_detail, name='course_detail'),
    path('profile/<int:pk>/', view_user_profile, name='view_user_profile'),
    path('register/student/', student_register, name='student_register'),  
    path('register/professor/', professor_register, name='professor_register'),  
    path('settings/', settings_view, name='settings'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('course/<int:course_id>/overview/', course_overview, name='course_overview'),
    path('class/<int:class_id>/', class_detail, name='class_detail'),
    path('get-assignments/', get_assignments, name='get_assignments'),
    path('course/<int:course_id>/professor/',professor_info, name='professor_info'),
    path('course/<int:course_id>/syllabus/',course_syllabus, name='course_syllabus'),
    path('course/<int:course_id>/modules/',course_modules, name='course_modules'),
    path('course/<int:course_id>/assignments/',course_assignments, name='course_assignments'),
    path('course/<int:course_id>/announcements/',course_announcements, name='course_announcements'),
    path('course/<int:course_id>/grades/',course_grades, name='course_grades'),





]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


