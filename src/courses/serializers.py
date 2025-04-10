from rest_framework import serializers
from .models import Course, CourseGroup, CourseGroupSubscription, CourseGroupTime

class CourseGroupTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseGroupTime
        fields = ['id', 'day', 'time']

class CourseGroupSerializer(serializers.ModelSerializer):
    times = CourseGroupTimeSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    confirmed_subscriptions = serializers.SerializerMethodField()
    available_capacity = serializers.SerializerMethodField()
    has_seats = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseGroup
        fields = [
            'id', 
            'course', 
            'teacher', 
            'teacher_name', 
            'capacity',
            'is_active',
            'times',
            'confirmed_subscriptions',
            'available_capacity',
            'has_seats'
        ]
    
    def get_confirmed_subscriptions(self, obj):
        return obj.confirmed_subscriptions_count()
    
    def get_available_capacity(self, obj):
        return obj.available_capacity()
    
    def get_has_seats(self, obj):
        return obj.has_seats()

class CourseSerializer(serializers.ModelSerializer):
    groups = CourseGroupSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'year', 'teachers','type_education', 'groups']

class SubscribeToGroupsSerializer(serializers.Serializer):
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )

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
            'join_time',
            'is_confirmed',
            'confirmed_at'
        ]
    
    def get_group_info(self, obj):
        return {
            'teacher': obj.course_group.teacher.name,
            'times': list(obj.course_group.times.values('day', 'time'))
        }