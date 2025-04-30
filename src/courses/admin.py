from django.contrib import admin
from .models import Course, CourseGroup, CourseGroupTime, CourseGroupSubscription

class CourseGroupTimeInline(admin.TabularInline):
    model = CourseGroupTime
    extra = 1
    fields = ('day', 'time')
    ordering = ('day', 'time')

class CourseGroupInline(admin.TabularInline):
    model = CourseGroup
    extra = 1
    show_change_link = True
    fields = ('teacher', 'capacity', 'times_count')
    readonly_fields = ('times_count',)

    def times_count(self, obj):
        return obj.times.count()
    times_count.short_description = "Time Slots"

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'type_education', 'teachers_list', 'groups_count')
    list_filter = ('year', 'type_education')
    search_fields = ('title',)
    filter_horizontal = ('teachers',)
    inlines = [CourseGroupInline]

    def teachers_list(self, obj):
        return ", ".join([t.name for t in obj.teachers.all()])
    teachers_list.short_description = "Teachers"

    def groups_count(self, obj):
        return obj.coursegroup_set.count()
    groups_count.short_description = "Groups"

@admin.register(CourseGroup)
class CourseGroupAdmin(admin.ModelAdmin):
    list_display = (
        'course', 
        'teacher', 
        'capacity', 
        'confirmed_subscriptions_count',
        'available_capacity',
        'has_seats',
        'is_active',
        'times_count'
    )
    list_filter = ('course', 'teacher', 'is_active')
    search_fields = ('course__title', 'teacher__name')
    inlines = [CourseGroupTimeInline]
    list_editable = ('is_active',)

    def confirmed_subscriptions_count(self, obj):
        return obj.confirmed_subscriptions_count()
    confirmed_subscriptions_count.short_description = "Confirmed Subs"

    def available_capacity(self, obj):
        return obj.available_capacity()
    available_capacity.short_description = "Available"

    def has_seats(self, obj):
        return obj.has_seats()
    has_seats.boolean = True
    has_seats.short_description = "Has Seats"
    def times_count(self, obj):
        return obj.times.count()
    times_count.short_description = "Time Slots"

@admin.register(CourseGroupTime)
class CourseGroupTimeAdmin(admin.ModelAdmin):
    list_display = ('course_group', 'day', 'time')
    list_filter = ('day', 'course_group__course', 'course_group__teacher')
    search_fields = ('course_group__course__title', 'course_group__teacher__name')
    ordering = ('course_group', 'day', 'time')



@admin.register(CourseGroupSubscription)
class CourseGroupSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'teacher', 'group_times', 'status', 'is_confirmed' ,'is_declined','confirmed_at', 'declined_at')
    list_filter = ('is_confirmed', 'is_declined', 'course', 'course_group__teacher')
    search_fields = ('student__name', 'course__title', 'decline_note')
    readonly_fields = ('created_at', 'confirmed_at', 'declined_at')
    date_hierarchy = 'confirmed_at'
    list_editable = ('is_confirmed', 'is_declined')

    def teacher(self, obj):
        return obj.course_group.teacher
    teacher.short_description = "Teacher"
    teacher.admin_order_field = 'course_group__teacher'

    def group_times(self, obj):
        times = obj.course_group.times.all().order_by('day', 'time')
        return ", ".join([f"{t.get_day_display()} {t.time.strftime('%H:%M')}" for t in times])
    group_times.short_description = "Group Times"

    def status(self, obj):
        if obj.is_confirmed:
            return "✅ Confirmed"
        elif obj.is_declined:
            return "❌ Declined"
        return "⏳ Pending"
    status.short_description = "Status"

    fieldsets = (
        (None, {
            'fields': ('student', 'course', 'course_group')
        }),
        ('Status', {
            'fields': (
                'is_confirmed', 
                'confirmed_at',
                'is_declined',
                'decline_note',
                'declined_at'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    actions = [
        'confirm_subscriptions',
        'unconfirm_subscriptions',
        'decline_subscriptions',
        'clear_decline_status'
    ]

    def confirm_subscriptions(self, request, queryset):
        updated = queryset.filter(is_confirmed=False).update(
            is_confirmed=True,
            confirmed_at=timezone.now(),
            is_declined=False,
            decline_note=None,
            declined_at=None
        )
        self.message_user(request, f"{updated} subscription(s) successfully confirmed.")
    confirm_subscriptions.short_description = "✅ Confirm selected subscriptions"

    def unconfirm_subscriptions(self, request, queryset):
        updated = queryset.filter(is_confirmed=True).update(
            is_confirmed=False,
            confirmed_at=None
        )
        self.message_user(request, f"{updated} subscription(s) marked as unconfirmed.")
    unconfirm_subscriptions.short_description = "⏳ Unconfirm selected subscriptions"

    def decline_subscriptions(self, request, queryset):
        default_note = "Declined by admin"
        updated = queryset.filter(is_confirmed=False).update(
            is_declined=True,
            decline_note=default_note,
            declined_at=timezone.now()
        )
        self.message_user(request, f"{updated} subscription(s) declined with default note.")
    decline_subscriptions.short_description = "❌ Decline selected subscriptions"

    def clear_decline_status(self, request, queryset):
        updated = queryset.filter(is_declined=True).update(
            is_declined=False,
            decline_note=None,
            declined_at=None
        )
        self.message_user(request, f"{updated} subscription(s) had decline status cleared.")
    clear_decline_status.short_description = "🔄 Clear decline status"

    def save_model(self, request, obj, form, change):
        # Ensure the model's save() method is called to handle timestamps
        super().save_model(request, obj, form, change)







