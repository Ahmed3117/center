from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'created_at', 'updated_at')
    search_fields = ('name', 'specialization')
    list_filter = ('specialization', 'created_at')

