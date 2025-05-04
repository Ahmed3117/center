from rest_framework import serializers
from accounts.models import Student, Year, TypeEducation, Teacher
from about.models import AboutPage, Feature
from courses.models import Course, CourseGroup, CourseGroupSubscription, CourseGroupTime
from django.contrib.auth.models import User

from dashboard.models import RequestLog

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
        fields = ['id', 'user', 'username', 'name','order', 'specialization', 'education_language_type','promo_video','promo_video_link', 'description', 'image', 'created_at', 'updated_at']
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
    username = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'user', 'name', 'parent_phone', 'type_education', 'year',
            'division', 'government', 'code', 'by_code', 'active', 'block',
            'points', 'jwt_token', 'is_admin', 'updated', 'created',
            'username', 
        ]

    def get_username(self, obj):
        return obj.user.username if obj.user else None




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
    confirmed_subscriptions = serializers.IntegerField(read_only=True)
    unconfirmed_subscriptions = serializers.IntegerField(read_only=True)
    available_capacity = serializers.IntegerField(read_only=True)
    has_seats = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CourseGroup
        fields = [
            'id', 'course', 'teacher', 'capacity', 'is_active', 'image',
            'times', 'confirmed_subscriptions', 'unconfirmed_subscriptions',
            'available_capacity', 'has_seats', 'created_at', 'updated_at'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    course = CourseSerializer()
    course_group = CourseGroupWithTimesSerializer()
    
    class Meta:
        model = CourseGroupSubscription
        fields = '__all__'


class AdminStudentCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    class Meta:
        model = Student
        fields = [
            'username', 'password', 'email', 'first_name', 'last_name',
            'name', 'parent_phone', 'type_education', 'year',
            'division', 'government', 'code', 'by_code', 'active', 'block',
        ]
        extra_kwargs = {
            'code': {'required': False},
            'by_code': {'required': False}
        }

    def create(self, validated_data):
        user_data = {
            'username': validated_data.pop('username'),
            'password': validated_data.pop('password'),
            'email': validated_data.pop('email', ''),
            'first_name': validated_data.pop('first_name', ''),
            'last_name': validated_data.pop('last_name', '')
        }
        user = User.objects.create_user(**user_data)
        student = Student.objects.create(user=user, **validated_data)
        return student

    def update(self, instance, validated_data):
        user = instance.user

        # Update user fields if provided
        user_fields = ['username', 'email', 'first_name', 'last_name']
        for field in user_fields:
            if field in validated_data:
                setattr(user, field, validated_data.pop(field))

        # Handle password separately
        if 'password' in validated_data:
            user.set_password(validated_data.pop('password'))

        user.save()

        # Update student fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class AdminCreateSubscriptionSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )


class AdminTeacherCreateUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    class Meta:
        model = Teacher
        fields = [
            'username', 'password', 'email', 'first_name', 'last_name',
            'name', 'order', 'specialization','education_language_type', 'description',
            'promo_video', 'promo_video_link', 'image'
        ]

    def validate(self, data):
        username = data.get('username')
        instance = self.instance  # teacher instance
        if username and instance:
            current_user = instance.user
            if username != current_user.username:
                if User.objects.filter(username=username).exclude(pk=current_user.pk).exists():
                    raise serializers.ValidationError({'username': 'A user with that username already exists.'})
        return data

    def create(self, validated_data):
        user_data = {
            'username': validated_data.pop('username'),
            'password': validated_data.pop('password'),
            'email': validated_data.pop('email', ''),
            'first_name': validated_data.pop('first_name', ''),
            'last_name': validated_data.pop('last_name', '')
        }
        user = User.objects.create_user(**user_data)
        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher

    def update(self, instance, validated_data):
        user = instance.user

        if 'username' in validated_data:
            user.username = validated_data.pop('username')

        for field in ['email', 'first_name', 'last_name']:
            if field in validated_data:
                setattr(user, field, validated_data.pop(field))

        if 'password' in validated_data:
            user.set_password(validated_data.pop('password'))

        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def update(self, instance, validated_data):
        if 'username' in validated_data and validated_data['username'] != instance.username:
            if User.objects.filter(username=validated_data['username']).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError({'username': 'A user with that username already exists.'})
            instance.username = validated_data['username']

        for field in ['email', 'first_name', 'last_name']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        instance.save()
        return instance





class CourseGroupSerializer(serializers.ModelSerializer):
    times = CourseGroupTimeSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    teacher_education_language_type = serializers.CharField(source='teacher.education_language_type', read_only=True)
    confirmed_subscriptions = serializers.SerializerMethodField()
    available_capacity = serializers.SerializerMethodField()
    teacher_image = serializers.SerializerMethodField()

    def get_teacher_image(self, obj):
        request = self.context.get('request')
        if obj.teacher.image:
            return request.build_absolute_uri(obj.teacher.image.url)
        return None
    
    class Meta:
        model = CourseGroup
        fields = [
            'id', 'capacity', 'is_active', 'image', 
            'teacher', 'teacher_name','teacher_education_language_type','teacher_image', 'times',
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


class BulkDeclineSubscriptionSerializer(serializers.Serializer):
    subscriptions = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            allow_empty=False
        ),
        min_length=1
    )

    def validate_subscriptions(self, value):
        for sub in value:
            if 'subscription_id' not in sub:
                raise serializers.ValidationError("Each item must contain a 'subscription_id'")
            if 'decline_note' not in sub:
                sub['decline_note'] = ""  # Default empty note if not provided
        return value



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class RequestLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = RequestLog
        fields = '__all__'

