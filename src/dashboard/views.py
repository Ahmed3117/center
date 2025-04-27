from django.shortcuts import render
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from accounts.models import Student, Year, TypeEducation, Teacher
from about.models import AboutPage, Feature
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Prefetch
from accounts.pagination import CustomPageNumberPagination
from accounts.serializers import StudentProfileSerializer
from courses.models import Course, CourseGroup, CourseGroupSubscription, CourseGroupTime
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.db.models import Q, Exists, OuterRef,Count
from django.utils import timezone


from .serializers import (
    CourseGroupWithTimesSerializer,
    CourseSerializer,
    StudentSerializer,
    SubscriptionSerializer,
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
    search_fields = ['name', 'specialization']
    filter_backends = [filters.SearchFilter]

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

# needed get endpoints

class DashboardStudentsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudentSerializer
    filterset_fields = ['year', 'type_education', 'active', 'block']
    
    def get_queryset(self):
        return Student.objects.select_related(
            'year', 'type_education', 'user'
        ).all()

class DashboardCoursesView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseSerializer
    
    def get_queryset(self):
        return Course.objects.select_related(
            'year', 'type_education'
        ).prefetch_related(
            'teachers'
        ).annotate(
            groups_count=Count('coursegroup')
        ).all()

class DashboardCourseGroupsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseGroupWithTimesSerializer
    filterset_fields = ['course', 'teacher', 'is_active']
    
    def get_queryset(self):
        return CourseGroup.objects.select_related(
            'course', 'teacher'
        ).prefetch_related(
            Prefetch('times', queryset=CourseGroupTime.objects.order_by('day', 'time'))
        ).all()

class DashboardSubscriptionsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionSerializer
    filterset_fields = ['student', 'course', 'course_group', 'is_confirmed']
    
    def get_queryset(self):
        return CourseGroupSubscription.objects.select_related(
            'student', 'student__year', 'student__type_education',
            'course', 'course__year', 'course__type_education',
            'course_group', 'course_group__teacher'
        ).prefetch_related(
            'course_group__times'
        ).all()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    
    stats = {
        'students': {
            'total': Student.objects.count(),
            'active': Student.objects.filter(active=True).count(),
            'blocked': Student.objects.filter(block=True).count(),
        },
        'teachers': {
            'total': Teacher.objects.count(),
        },
        'courses': {
            'total': Course.objects.count(),
            'by_type': list(Course.objects.values('type_education__name').annotate(count=Count('id')))
        },
        'groups': {
            'total': CourseGroup.objects.count(),
            'active': CourseGroup.objects.filter(is_active=True).count(),
        },
        'subscriptions': {
            'total': CourseGroupSubscription.objects.count(),
            'confirmed': CourseGroupSubscription.objects.filter(is_confirmed=True).count(),
            'pending': CourseGroupSubscription.objects.filter(is_confirmed=False).count(),
        }
    }
    return Response(stats)


################################ new #######################################

class ApplyStudentCodeView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        student_id = request.data.get('student_id')
        code = request.data.get('code')
        
        if not student_id or not code:
            return Response(
                {"error": "مطلوب إدخال رقم الطالب والكود"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            student = Student.objects.get(id=student_id)
            
            # Apply the code
            student.code = code
            student.by_code = True  # Mark that this student was registered by code
            student.save()
            
            return Response(
                {
                    "message": "تم تطبيق الكود بنجاح",
                    "student": {
                        "id": student.id,
                        "name": student.name,
                        "code": student.code,
                        "by_code": student.by_code
                    }
                },
                status=status.HTTP_200_OK
            )
            
        except Student.DoesNotExist:
            return Response(
                {"error": "الطالب غير موجود"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ConfirmSubscriptionsView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        subscription_ids = request.data.get('subscription_ids', [])
        
        if not subscription_ids:
            return Response(
                {"error": "لم يتم اختيار اشتراكات ليتم تفكيلها"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Get all existing subscriptions from the provided IDs
            existing_subscriptions = CourseGroupSubscription.objects.filter(
                id__in=subscription_ids
            )
            
            # Calculate not found subscriptions
            found_ids = set(existing_subscriptions.values_list('id', flat=True))
            not_found = len(subscription_ids) - len(found_ids)
            
            # Get unconfirmed subscriptions
            unconfirmed_subscriptions = existing_subscriptions.filter(
                is_confirmed=False
            )
            
            # Update unconfirmed subscriptions
            confirmed_count = unconfirmed_subscriptions.update(
                is_confirmed=True,
                confirmed_at=timezone.now()
            )
            
            # Calculate already confirmed
            already_confirmed = len(existing_subscriptions) - confirmed_count
            
            response_data = {
                "confirmed_count": confirmed_count,
                "already_confirmed": already_confirmed,
                "not_found": not_found,
                "message": (
                    f"تم تفعيل {confirmed_count} اشتراك. "
                    f"{already_confirmed} اشتراك مفعل مسبقاً. "
                    f"{not_found} اشتراك غير موجود"
                )
            }
            
            return Response(
                response_data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SubscriptionListView(APIView):
    # permission_classes = [IsAdminUser]
    pagination_class = CustomPageNumberPagination

    def get(self, request):
        # Get query parameters
        params = request.query_params
        
        # Base queryset - start with students who have subscriptions
        student_queryset = Student.objects.filter(
            coursegroupsubscription__isnull=False
        ).distinct().select_related(
            'year'
        ).prefetch_related(
            'coursegroupsubscription_set',
            'coursegroupsubscription_set__course',
            'coursegroupsubscription_set__course_group',
            'coursegroupsubscription_set__course_group__teacher',
            'coursegroupsubscription_set__course_group__times'
        )

        # Apply filters
        if 'course_id' in params:
            student_queryset = student_queryset.filter(
                coursegroupsubscription__course_id=params['course_id']
            )
        if 'group_id' in params:
            student_queryset = student_queryset.filter(
                coursegroupsubscription__course_group_id=params['group_id']
            )
        if 'government' in params:
            student_queryset = student_queryset.filter(
                government=params['government']
            )
        if 'year_id' in params:
            student_queryset = student_queryset.filter(
                year_id=params['year_id']
            )
        if 'is_confirmed' in params:
            student_queryset = student_queryset.filter(
                coursegroupsubscription__is_confirmed=params['is_confirmed'].lower() == 'true'
            )
        if 'has_unconfirmed_subscriptions' in params:
            if params['has_unconfirmed_subscriptions'].lower() == 'true':
                # Filter for students with at least one unconfirmed subscription
                student_queryset = student_queryset.filter(
                    Exists(
                        CourseGroupSubscription.objects.filter(
                            student_id=OuterRef('id'),
                            is_confirmed=False
                        )
                    )
                )
            else:
                # Filter for students with NO unconfirmed subscriptions
                student_queryset = student_queryset.exclude(
                    Exists(
                        CourseGroupSubscription.objects.filter(
                            student_id=OuterRef('id'),
                            is_confirmed=False
                        )
                    )
                )

        # Search
        search_term = params.get('search', '').strip()
        if search_term:
            student_queryset = student_queryset.filter(
                Q(name__icontains=search_term) |
                Q(parent_phone__icontains=search_term) |
                Q(code__icontains=search_term) |
                Q(coursegroupsubscription__course__title__icontains=search_term) |
                Q(coursegroupsubscription__course_group__teacher__name__icontains=search_term)
            ).distinct()

        # Build response data
        students_data = []
        for student in student_queryset:
            # Get all subscriptions for this student
            subscriptions = student.coursegroupsubscription_set.all()
            
            # Split into confirmed/unconfirmed
            confirmed_subs = [sub for sub in subscriptions if sub.is_confirmed]
            unconfirmed_subs = [sub for sub in subscriptions if not sub.is_confirmed]
            
            # Build subscription data
            def build_subscription(sub):
                return {
                    'subscription_id': sub.id,
                    'course_id': sub.course.id,
                    'course_title': sub.course.title,
                    'group_id': sub.course_group.id,
                    'group_capacity': sub.course_group.capacity,
                    'teacher_id': sub.course_group.teacher.id,
                    'teacher_name': sub.course_group.teacher.name,
                    'created_at': sub.created_at,
                    'confirmed_at': sub.confirmed_at,
                    'timeslots': [
                        {
                            'day': slot.day,
                            'time': slot.time.strftime('%H:%M')
                        } for slot in sub.course_group.times.all()
                    ]
                }
            
            students_data.append({
                'student_id': student.id,
                'student_name': student.name,
                'student_code': student.code,
                'student_phone': student.parent_phone,
                'student_government': student.government,
                'student_year': student.year.name if student.year else None,
                'confirmed_subscriptions_count': len(confirmed_subs),
                'unconfirmed_subscriptions_count': len(unconfirmed_subs),
                'has_unconfirmed_subscriptions': len(unconfirmed_subs) > 0,
                'confirmed_subscriptions': [build_subscription(sub) for sub in confirmed_subs],
                'unconfirmed_subscriptions': [build_subscription(sub) for sub in unconfirmed_subs]
            })

        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(students_data, request)

        return paginator.get_paginated_response({
            'students': page,
            'filters': {
                'course_id': params.get('course_id'),
                'group_id': params.get('group_id'),
                'government': params.get('government'),
                'year_id': params.get('year_id'),
                'is_confirmed': params.get('is_confirmed'),
                'has_unconfirmed_subscriptions': params.get('has_unconfirmed_subscriptions'),
                'search': search_term
            }
        })








