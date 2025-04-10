from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from accounts.models import Year, TypeEducation, Teacher
from about.models import AboutPage, Feature
from .serializers import (
    YearSerializer, 
    TypeEducationSerializer, 
    TeacherSerializer,
    AboutPageSerializer,
    FeatureSerializer
)

# Create your views here.

# Year views
class YearListCreateView(generics.ListCreateAPIView):
    """List all years or create a new year"""
    queryset = Year.objects.all()
    serializer_class = YearSerializer
    permission_classes = [permissions.IsAuthenticated]

class YearRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a year instance"""
    queryset = Year.objects.all()
    serializer_class = YearSerializer
    permission_classes = [permissions.IsAuthenticated]

# TypeEducation views
class TypeEducationListCreateView(generics.ListCreateAPIView):
    """List all education types or create a new education type"""
    queryset = TypeEducation.objects.all()
    serializer_class = TypeEducationSerializer
    permission_classes = [permissions.IsAuthenticated]

class TypeEducationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an education type instance"""
    queryset = TypeEducation.objects.all()
    serializer_class = TypeEducationSerializer
    permission_classes = [permissions.IsAuthenticated]

# Teacher views
class TeacherListCreateView(generics.ListCreateAPIView):
    """List all teachers or create a new teacher"""
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]

class TeacherRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a teacher instance"""
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]

# AboutPage views with special handling to ensure only one object exists
class AboutPageView(generics.GenericAPIView):
    """Handle the about page content (ensuring only one instance exists)"""
    serializer_class = AboutPageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Get the about page content"""
        try:
            about_page = AboutPage.objects.first()
            if about_page:
                serializer = self.get_serializer(about_page)
                return Response(serializer.data)
            return Response({"detail": "No about page content found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, *args, **kwargs):
        """Create or update the about page content"""
        existing_about_page = AboutPage.objects.first()
        
        if existing_about_page:
            # Update existing instance
            serializer = self.get_serializer(existing_about_page, data=request.data)
        else:
            # Create new instance
            serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        """Update the about page content"""
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Delete the about page content"""
        about_page = AboutPage.objects.first()
        if about_page:
            about_page.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "No about page content found."}, status=status.HTTP_404_NOT_FOUND)

# Feature views
class FeatureListCreateView(generics.ListCreateAPIView):
    """List all features or create a new feature"""
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    permission_classes = [permissions.IsAuthenticated]

class FeatureRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a feature instance"""
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    permission_classes = [permissions.IsAuthenticated]
