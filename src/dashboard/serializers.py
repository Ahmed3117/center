from rest_framework import serializers
from accounts.models import Year, TypeEducation, Teacher
from about.models import AboutPage, Feature

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
        fields = ['id', 'user', 'username', 'name', 'specialization', 'description', 'image', 'created_at', 'updated_at']
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