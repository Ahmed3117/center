from rest_framework import serializers
from accounts.models import Student, Year, TypeEducation, Teacher
from about.models import AboutPage, Feature
from courses.models import Course, CourseGroup, CourseGroupSubscription, CourseGroupTime

class YearSerializer(serializers.ModelSerializer):
    """Serializer for the Year model"""
    
    class Meta:
        model = Year
        fields = ['id', 'name', 'created', 'updated']
        read_only_fields = ['created', 'updated']

class TypeEducationSerializer(serializers.ModelSerializer):
    """Serializer for the TypeEducation model"""
    
    class Meta:
        model = TypeEducation
        fields = ['id', 'name', 'created', 'updated']
        read_only_fields = ['created', 'updated']

class TeacherSerializer(serializers.ModelSerializer):
    """Serializer for the Teacher model in the dashboard"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['id', 'user', 'username', 'name', 'specialization','promo_video', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class AboutPageSerializer(serializers.ModelSerializer):
    """Serializer for the AboutPage model"""
    
    class Meta:
        model = AboutPage
        fields = ['id', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class FeatureSerializer(serializers.ModelSerializer):
    """Serializer for the Feature model"""
    
    class Meta:
        model = Feature
        fields = ['id', 'title', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] 



class StudentSerializer(serializers.ModelSerializer):
    year = YearSerializer()
    type_education = TypeEducationSerializer()
    
    class Meta:
        model = Student
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    year = YearSerializer()
    type_education = TypeEducationSerializer()
    teachers = TeacherSerializer(many=True)
    groups_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Course
        fields = '__all__'

class CourseGroupTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseGroupTime
        fields = ['id', 'day', 'time']


class CourseGroupWithTimesSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    teacher = TeacherSerializer()
    times = CourseGroupTimeSerializer(many=True)
    
    class Meta:
        model = CourseGroup
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    course = CourseSerializer()
    course_group = CourseGroupWithTimesSerializer()
    
    class Meta:
        model = CourseGroupSubscription
        fields = '__all__'





