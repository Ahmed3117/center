from django.contrib import admin
from .models import  TypeEducation, Student, Teacher



@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'points', 'division', 'government', 'active', 'block', 'is_admin', 'created')
    list_filter = ('active', 'block', 'is_admin', 'year', 'type_education')
    search_fields = ('name', 'code', 'government', 'parent_phone')
    ordering = ('created',)
    readonly_fields = ('created', 'updated')
    fieldsets = (
        (None, {'fields': ('user', 'name', 'parent_phone', 'type_education', 'year', 'division', 'government')}),
        ('Status', {'fields': ('active', 'block', 'is_admin', 'by_code', 'code')}),
        ('Security', {'fields': ('jwt_token',)}),
        ('Points', {'fields': ('points',)}),
    )

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization','order', 'created_at', 'updated_at')
    search_fields = ('name', 'specialization')
    ordering = ('order','created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'name', 'specialization', 'description','promo_video_link','order')}),
        ('Media', {'fields': ('promo_video', 'image')}),
    )







