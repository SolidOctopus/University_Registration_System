from django.contrib import admin
from .models import Student, Professor, Admin, Course, Major

class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email']
    filter_horizontal = ('courses',)

admin.site.register(Student)
admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Admin)
admin.site.register(Course)
admin.site.register(Major)

