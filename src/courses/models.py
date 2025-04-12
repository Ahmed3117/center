from django.db import models
from accounts.models import Year, TypeEducation, Student, Teacher
from django.utils import timezone

class Course(models.Model):
    title = models.CharField(max_length=100)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    type_education = models.ForeignKey(TypeEducation, on_delete=models.CASCADE)
    teachers = models.ManyToManyField(Teacher)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.year.name}"

class CourseGroup(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)  # New field
    image = models.ImageField(upload_to='course_groups/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - Group {self.id} (Teacher: {self.teacher.name})"

    def confirmed_subscriptions_count(self):
        return self.coursegroupsubscription_set.filter(is_confirmed=True).count()

    def available_capacity(self):
        return self.capacity - self.confirmed_subscriptions_count()

    def has_seats(self):
        return self.available_capacity() > 0

class CourseGroupTime(models.Model):
    DAY_CHOICES = [
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
    ]
    
    course_group = models.ForeignKey(CourseGroup, on_delete=models.CASCADE, related_name='times')
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    time = models.TimeField()
    
    def __str__(self):
        return f"{self.get_day_display()} at {self.time.strftime('%H:%M')}"

class CourseGroupSubscription(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_group = models.ForeignKey(CourseGroup, on_delete=models.CASCADE)
    # join_time = models.DateTimeField(null=True, blank=True, default=None)
    is_confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.student.name} in {self.course_group}"