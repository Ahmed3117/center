from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q
from .models import AboutPage, Feature, News
from accounts.models import Teacher
from .serializers import (
    AboutPagePublicSerializer, 
    FeaturePublicSerializer,
    NewsSerializer, 
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
    """Public API view to list all teachers with optional course filtering"""
    serializer_class = TeacherPublicSerializer
    permission_classes = [] 
    
    def get_queryset(self):
        queryset = Teacher.objects.all()
        
        # Filter by course if course_id parameter is provided
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course__id=course_id).distinct()
            
        return queryset


class ActiveNewsView(generics.ListAPIView):
    serializer_class = NewsSerializer

    def get_queryset(self):
        now = timezone.now()
        
        # Build the query for active news
        query = Q(is_active=True)
        
        # News that are currently active (now between from_date and to_date)
        current_news = query & Q(
            from_date__lte=now,
            to_date__gte=now
        )
        
        # News with no end date (to_date is null) and started or no start date
        ongoing_news = query & (
            Q(to_date__isnull=True) & 
            (Q(from_date__lte=now) | Q(from_date__isnull=True))
        )
        
        # News with no start date but future end date
        future_news = query & Q(
            from_date__isnull=True,
            to_date__gt=now
        )
        
        # Combine all conditions
        return News.objects.filter(current_news | ongoing_news | future_news).order_by('-created_at')




