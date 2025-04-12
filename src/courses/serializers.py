from rest_framework import serializers

from accounts.serializers import TeacherSerializer
from accounts.models import Student, Teacher
from dashboard.serializers import TypeEducationSerializer, YearSerializer
from .models import Course, CourseGroup, CourseGroupSubscription, CourseGroupTime

class CourseGroupTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseGroupTime
        fields = ['id', 'day', 'time']

class CourseGroupSerializer(serializers.ModelSerializer):
    times = CourseGroupTimeSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    teacher_promo_video = serializers.CharField(source='teacher.promo_video', read_only=True)
    year_name = serializers.CharField(source='course.year.name', read_only=True)
    course_name = serializers.CharField(source='course.title', read_only=True)
    confirmed_subscriptions = serializers.SerializerMethodField()
    available_capacity = serializers.SerializerMethodField()
    has_seats = serializers.SerializerMethodField()
    subscription_status = serializers.SerializerMethodField()  # New field
    
    class Meta:
        model = CourseGroup
        fields = [
            'id', 
            'course', 
            'teacher', 
            'image', 
            'teacher_name', 
            'teacher_promo_video', 
            'year_name', 
            'course_name', 
            'capacity',
            'is_active',
            'times',
            'confirmed_subscriptions',
            'available_capacity',
            'has_seats',
            'subscription_status'  # Added new field
        ]
    
    def get_subscription_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                student = Student.objects.get(user=request.user)
                subscription = CourseGroupSubscription.objects.filter(
                    student=student,
                    course_group=obj
                ).first()
                
                if not subscription:
                    return "new"
                elif subscription.is_confirmed:
                    return "subscribed"
                else:
                    return "pending"
            except (Student.DoesNotExist, AttributeError):
                return "new"
        return "new"
    
    def get_confirmed_subscriptions(self, obj):
        return obj.confirmed_subscriptions_count()
    
    def get_available_capacity(self, obj):
        return obj.available_capacity()
    
    def get_has_seats(self, obj):
        return obj.has_seats()

class CourseSerializer(serializers.ModelSerializer):
    groups = CourseGroupSerializer(many=True, read_only=True)
    teachers = TeacherSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'year', 'teachers', 'type_education', 'groups']

class SubscribeToGroupsSerializer(serializers.Serializer):
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )

    def validate_group_ids(self, value):
        # Check if all group IDs exist
        existing_ids = set(CourseGroup.objects.filter(
            id__in=value
        ).values_list('id', flat=True))
        
        invalid_ids = set(value) - existing_ids
        if invalid_ids:
            raise serializers.ValidationError(
                f"Invalid group IDs: {invalid_ids}"
            )
        return value

class CourseGroupSubscriptionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    group_info = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CourseGroupSubscription
        fields = [
            'id', 
            'course', 
            'course_title',
            'course_group',
            'group_info',
            'is_confirmed',
            'confirmed_at'
        ]
    
    def get_group_info(self, obj):
        return {
            'teacher': obj.course_group.teacher.name,
            'times': list(obj.course_group.times.values('day', 'time'))
        }


class TeacherCourseGroupSerializer(serializers.ModelSerializer):
    times = CourseGroupTimeSerializer(many=True, read_only=True)
    subscription_count = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = CourseGroup
        fields = [
            'id', 'capacity', 'is_active', 'times',
            'subscription_count', 'available_seats'
        ]

    def get_subscription_count(self, obj):
        return obj.coursegroupsubscription_set.count()

    def get_available_seats(self, obj):
        return obj.capacity - obj.coursegroupsubscription_set.count()

class TeacherCourseSerializer(serializers.ModelSerializer):
    year = YearSerializer()
    type_education = TypeEducationSerializer()
    groups = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'year', 'type_education', 'groups'
        ]

    def get_groups(self, obj):
        teacher = self.context['teacher']
        groups = obj.coursegroup_set.filter(teacher=teacher)
        return CourseGroupSerializer(groups, many=True).data

class TeacherFullDataSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            'id', 'name', 'image', 'specialization',
            'description', 'promo_video', 'courses'
        ]

    def get_courses(self, obj):
        request = self.context.get('request')
        student = None
        
        # Get the student if authenticated
        if request and request.user.is_authenticated:
            try:
                student = Student.objects.get(user=request.user)
            except Student.DoesNotExist:
                pass
        
        # Filter courses by student's year if available
        courses = Course.objects.filter(coursegroup__teacher=obj).distinct()
        if student and student.year:
            courses = courses.filter(year=student.year)
        
        return TeacherCourseSerializer(
            courses, 
            many=True,
            context={'teacher': obj, 'request': request}
        ).data







