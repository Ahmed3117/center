from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from .models import  TypeEducation, Student, Teacher


def add_students_to_year_one_course_groups(modeladmin, request, queryset):
    """
    Custom admin action to add selected students to all course groups 
    related to courses with year ID = 1
    """
    from courses.models import CourseGroup, CourseGroupSubscription, Course
    
    # Get all course groups for courses with year ID = 1
    year_one_course_groups = CourseGroup.objects.filter(
        course__year_id=1,
        is_active=True
    ).select_related('course')
    
    if not year_one_course_groups.exists():
        messages.error(request, "No active course groups found for Year ID = 1")
        return
    
    students_count = queryset.count()
    course_groups_count = year_one_course_groups.count()
    
    if students_count == 0:
        messages.error(request, "No students selected")
        return
    
    created_subscriptions = 0
    existing_subscriptions = 0
    
    try:
        with transaction.atomic():
            for student in queryset:
                for course_group in year_one_course_groups:
                    # Check if subscription already exists
                    subscription, created = CourseGroupSubscription.objects.get_or_create(
                        student=student,
                        course=course_group.course,
                        course_group=course_group,
                        defaults={
                            'is_confirmed': True,  # Automatically confirm the subscriptions
                        }
                    )
                    
                    if created:
                        created_subscriptions += 1
                    else:
                        existing_subscriptions += 1
        
        success_message = f"Successfully processed {students_count} students for {course_groups_count} course groups. "
        success_message += f"Created {created_subscriptions} new subscriptions. "
        if existing_subscriptions > 0:
            success_message += f"{existing_subscriptions} subscriptions already existed."
        
        messages.success(request, success_message)
        
    except Exception as e:
        messages.error(request, f"Error occurred while adding students to course groups: {str(e)}")

add_students_to_year_one_course_groups.short_description = "Add selected students to all Year 1 course groups"


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'points', 'division', 'government', 'active', 'block', 'is_admin', 'created')
    list_filter = ('active', 'block', 'is_admin', 'year', 'type_education', 'by_code')
    search_fields = ('name', 'code', 'government', 'parent_phone')
    ordering = ('created',)
    readonly_fields = ('created', 'updated')
    actions = [add_students_to_year_one_course_groups]
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







