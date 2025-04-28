from rest_framework import serializers
from accounts.models import Student, Year, TypeEducation, Teacher
from about.models import AboutPage, Feature
from courses.models import Course, CourseGroup, CourseGroupSubscription, CourseGroupTime
from django.contrib.auth.models import User

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


class AdminStudentCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    
    class Meta:
        model = Student
        fields = [
            'username', 'password', 'email', 'first_name', 'last_name',
            'name', 'parent_phone', 'type_education', 'year', 
            'division', 'government', 'code', 'by_code'
        ]
        extra_kwargs = {
            'code': {'required': False},
            'by_code': {'required': False}
        }

    def create(self, validated_data):
        # Extract user data
        user_data = {
            'username': validated_data.pop('username'),
            'password': validated_data.pop('password'),
            'email': validated_data.pop('email', ''),
            'first_name': validated_data.pop('first_name', ''),
            'last_name': validated_data.pop('last_name', '')
        }
        
        # Create user
        user = User.objects.create_user(
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        
        # Create student
        student = Student.objects.create(
            user=user,
            **validated_data
        )
        
        return student


class AdminCreateSubscriptionSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )



class CourseGroupSerializer(serializers.ModelSerializer):
    times = CourseGroupTimeSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    confirmed_subscriptions = serializers.SerializerMethodField()
    available_capacity = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseGroup
        fields = [
            'id', 'capacity', 'is_active', 'image', 
            'teacher', 'teacher_name', 'times',
            'confirmed_subscriptions', 'available_capacity'
        ]
    
    def get_confirmed_subscriptions(self, obj):
        return obj.coursegroupsubscription_set.filter(is_confirmed=True).count()
    
    def get_available_capacity(self, obj):
        return obj.capacity - self.get_confirmed_subscriptions(obj)


class CourseSerializerDetail(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    year_name = serializers.CharField(source='year.name', read_only=True)
    type_education_name = serializers.CharField(source='type_education.name', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'year', 'year_name', 
            'type_education', 'type_education_name', 'groups'
        ]
    
    def get_groups(self, obj):
        groups = obj.coursegroup_set.all()
        request = self.context.get('request')
        
        # Apply additional filtering if needed
        if request and request.query_params.get('is_active') == 'true':
            groups = groups.filter(is_active=True)
            
        return CourseGroupSerializer(groups, many=True, context=self.context).data
