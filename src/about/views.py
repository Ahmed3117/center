from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AboutPage, Feature
from accounts.models import Teacher
from .serializers import (
    AboutPagePublicSerializer, 
    FeaturePublicSerializer, 
    TeacherPublicSerializer, 
    AboutPageWithFeaturesSerializer
)

# Create your views here.

class AboutPageWithFeaturesView(APIView):
    """Public API view to get the AboutPage data with all Features"""
    permission_classes = []  # Public endpoint, no authentication required
    
    def get(self, request, *args, **kwargs):
        about_page = AboutPage.objects.first()
        if not about_page:
            return Response(
                {"detail": "No about page content found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AboutPageWithFeaturesSerializer(about_page)
        return Response(serializer.data)

class TeachersPublicView(generics.ListAPIView):
    """Public API view to list all teachers"""
    queryset = Teacher.objects.all()
    serializer_class = TeacherPublicSerializer
    permission_classes = []  # Public endpoint, no authentication required

