from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import Student
from .models import Course, CourseGroup, CourseGroupSubscription
from .serializers import (
    CourseSerializer, 
    CourseGroupSerializer,
    CourseGroupSubscriptionSerializer,
    SubscribeToGroupsSerializer
)
from django.shortcuts import get_object_or_404
from django.db.models import Count, F, Q

class StudentCoursesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer
    
    def get_queryset(self):
        student = get_object_or_404(Student, user=self.request.user)
        return Course.objects.filter(year=student.year)

class CourseGroupsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseGroupSerializer
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        queryset = CourseGroup.objects.filter(course_id=course_id)
        
        # Filter by is_active if provided
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        # Filter by has_seats if provided
        has_seats = self.request.query_params.get('has_seats', None)
        if has_seats is not None:
            # Annotate with confirmed subscriptions count
            queryset = queryset.annotate(
                confirmed_subs=Count(
                    'coursegroupsubscription',
                    filter=Q(coursegroupsubscription__is_confirmed=True)
                )
            )
            if has_seats.lower() == 'true':
                queryset = queryset.filter(capacity__gt=F('confirmed_subs'))
            elif has_seats.lower() == 'false':
                queryset = queryset.filter(capacity__lte=F('confirmed_subs'))
            
        return queryset

class SubscribeToGroupsView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscribeToGroupsSerializer
    
    def create(self, request, *args, **kwargs):
        student = get_object_or_404(Student, user=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        group_ids = serializer.validated_data['group_ids']
        subscriptions = []
        
        for group_id in group_ids:
            group = get_object_or_404(CourseGroup, id=group_id)
            
            # Check if subscription already exists
            if CourseGroupSubscription.objects.filter(
                student=student, 
                course_group=group
            ).exists():
                continue
                
            subscription = CourseGroupSubscription(
                student=student,
                course=group.course,
                course_group=group,
                join_time=None  # will be set by model's save method
            )
            subscriptions.append(subscription)
        
        # Bulk create subscriptions
        CourseGroupSubscription.objects.bulk_create(subscriptions)
        
        return Response(
            {"message": "Subscriptions created successfully"},
            status=status.HTTP_201_CREATED
        )

class StudentSubscriptionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseGroupSubscriptionSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get counts before pagination
        confirmed_count = queryset.filter(is_confirmed=True).count()
        unconfirmed_count = queryset.filter(is_confirmed=False).count()
        
        # Paginate the queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'results': serializer.data,
                'counts': {
                    'confirmed': confirmed_count,
                    'unconfirmed': unconfirmed_count,
                    'total': confirmed_count + unconfirmed_count
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'counts': {
                'confirmed': confirmed_count,
                'unconfirmed': unconfirmed_count,
                'total': confirmed_count + unconfirmed_count
            }
        })
    
    def get_queryset(self):
        student = get_object_or_404(Student, user=self.request.user)
        queryset = CourseGroupSubscription.objects.filter(student=student)
        
        is_confirmed = self.request.query_params.get('is_confirmed', None)
        if is_confirmed is not None:
            queryset = queryset.filter(is_confirmed=is_confirmed.lower() == 'true')
            
        return queryset