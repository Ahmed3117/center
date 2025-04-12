from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Prefetch
from rest_framework.permissions import IsAuthenticated
from accounts.models import Student, Teacher
from .models import Course, CourseGroup, CourseGroupSubscription
from .serializers import (
    CourseSerializer, 
    CourseGroupSerializer,
    CourseGroupSubscriptionSerializer,
    SubscribeToGroupsSerializer,
    TeacherFullDataSerializer
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
        teacher_id = self.kwargs['teacher_id']
        queryset = CourseGroup.objects.filter(
            course_id=course_id,
            teacher_id=teacher_id
        ).annotate(
            confirmed_subs=Count(
                'coursegroupsubscription',
                filter=Q(coursegroupsubscription__is_confirmed=True)
            )
        )
        
        # Filter by is_active if provided
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        # Filter by has_seats if provided
        has_seats = self.request.query_params.get('has_seats', None)
        if has_seats is not None:
            if has_seats.lower() == 'true':
                queryset = queryset.filter(capacity__gt=F('confirmed_subs'))
            elif has_seats.lower() == 'false':
                queryset = queryset.filter(capacity__lte=F('confirmed_subs'))
            
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class SubscribeToGroupsView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscribeToGroupsSerializer
    
    def create(self, request, *args, **kwargs):
        student = get_object_or_404(Student, user=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        group_ids = serializer.validated_data['group_ids']
        results = {
            'created': [],
            'skipped': []
        }
        
        for group_id in group_ids:
            group = get_object_or_404(CourseGroup, id=group_id)
            
            # Check if subscription already exists
            existing_sub = CourseGroupSubscription.objects.filter(
                student=student,
                course_group=group
            ).first()
            
            if existing_sub:
                results['skipped'].append({
                    'group_id': group_id,
                    'reason': 'Already subscribed',
                    'existing_subscription_id': existing_sub.id,
                    'status': 'subscribed' if existing_sub.is_confirmed else 'pending'
                })
                continue

            if not group.has_seats():
                results['skipped'].append({
                    'group_id': group_id,
                    'reason': 'No available seats'
                })
                continue
                
            subscription = CourseGroupSubscription.objects.create(
                student=student,
                course=group.course,
                course_group=group,
                is_confirmed=False  # Default to pending
            )
            
            results['created'].append({
                'group_id': group_id,
                'subscription_id': subscription.id,
                'status': 'pending'
            })
        
        return Response({
            'message': 'Subscription processed',
            'results': results
        }, status=status.HTTP_201_CREATED)

class GetTeacherFullDataView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeacherFullDataSerializer
    queryset = Teacher.objects.all()
    lookup_field = 'id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        
        return Teacher.objects.prefetch_related(
            Prefetch(
                'coursegroup_set',
                queryset=CourseGroup.objects.select_related('course').prefetch_related('times')
            ),
            Prefetch(
                'coursegroup_set__course',
                queryset=Course.objects.select_related('year', 'type_education')
            )
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