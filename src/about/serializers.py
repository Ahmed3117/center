from rest_framework import serializers
from .models import AboutPage, Feature
from accounts.models import Teacher

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
        fields = ['id', 'title', 'description', 'image'] 
        read_only_fields = ['created_at', 'updated_at']

class AboutPagePublicSerializer(serializers.ModelSerializer):
    """Serializer for the public AboutPage endpoint"""
    
    class Meta:
        model = AboutPage
        fields = ['id', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class FeaturePublicSerializer(serializers.ModelSerializer):
    """Serializer for the public Feature endpoint"""
    
    class Meta:
        model = Feature
        fields = ['id', 'title', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class TeacherPublicSerializer(serializers.ModelSerializer):
    """Serializer for the public Teacher endpoint"""
    
    class Meta:
        model = Teacher
        fields = ['id', 'name', 'specialization', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AboutPageWithFeaturesSerializer(serializers.ModelSerializer):
    """Serializer for the AboutPage with Features included"""
    features = FeaturePublicSerializer(source='feature_set', many=True, read_only=True)
    
    class Meta:
        model = AboutPage
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'features']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def to_representation(self, instance):
        """Custom representation to include all features even if not directly related"""
        ret = super().to_representation(instance)
        ret['features'] = FeaturePublicSerializer(Feature.objects.all(), many=True).data
        return ret