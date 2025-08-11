from django.shortcuts import get_object_or_404, render
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
from django.db.models import Q, Exists, OuterRef,Count, Case, When
from django.utils import timezone
from django.contrib.auth.models import User
from dashboard.filters import RequestLogFilter
from dashboard.models import RequestLog
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, BooleanField
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime,parse_date
from rest_framework.filters import SearchFilter,OrderingFilter
from django.db.models import Subquery, OuterRef, IntegerField
from django.conf import settings



from .serializers import (
    AdminCreateSubscriptionSerializer,
    AdminStudentCreateSerializer,
    AdminTeacherCreateUpdateSerializer,
    BulkDeclineSubscriptionSerializer,
    CourseGroupWithTimesSerializer,
    CourseSerializer,
    CourseSerializerDetail,
    RequestLogSerializer,
    StudentSerializer,
    SubscriptionSerializer,
    SubscriptionSimpleSerializer,
    YearSerializer, 
    TypeEducationSerializer, 
    TeacherSerializer,
    AboutPageSerializer,
    FeatureSerializer
)

# Custom permission to allow either authenticated user or requests with a valid private token
class IsAuthenticatedOrPrivateToken(permissions.BasePermission):
    """Allow access if user is authenticated or a valid private token is provided.
    Accepted token locations:
    - Header: X-Private-Token
    - Query param: private_token
    Settings keys checked (in order): private_token, PRIVATE_TOKEN
    """
    def has_permission(self, request, view):
        # Allow normal authenticated requests
        if getattr(request, 'user', None) and request.user.is_authenticated:
            return True

        # Fallback to private token check
        provided = (
            request.headers.get('X-Private-Token')
            or request.query_params.get('private_token')
            or request.META.get('HTTP_X_PRIVATE_TOKEN')
        )
        expected = getattr(settings, 'private_token', None) or getattr(settings, 'PRIVATE_TOKEN', None)
        return bool(expected and provided and provided == expected)

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
    filterset_fields = ['education_language_type', ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

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
    # permission_classes = [permissions.IsAdminUser]
    serializer_class = StudentSerializer
    queryset = Student.objects.select_related('year', 'type_education', 'user').all()

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['year', 'type_education', 'active', 'block', 'by_code','code', 'is_admin', 'division', 'government','user__username','parent_phone']
    search_fields = [
        'user__first_name', 'user__last_name', 'user__email',
        'name','government', 'division', 'code'
    ]
    ordering_fields = ['created', 'updated', 'points', 'year__name']
    ordering = ['-created']




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
    filter_backends = [DjangoFilterBackend, SearchFilter]
    
    filterset_fields = {
        'course': ['exact'],
        'course__year': ['exact'],
        'course__type_education': ['exact'],
        'teacher': ['exact'],
        'teacher__education_language_type': ['exact'],
        'is_active': ['exact'],
        'capacity': ['gte', 'lte'],
        'times__day': ['exact'],
    }
    
    search_fields = [
        'course__title',
        'course__year__name',
        'course__type_education__name',
        'teacher__name',
        'teacher__specialization',
        'teacher__education_language_type',
    ]
    
    def get_queryset(self):
        queryset = CourseGroup.objects.select_related(
            'course', 'course__year', 'course__type_education', 'teacher'
        ).prefetch_related(
            Prefetch('times', queryset=CourseGroupTime.objects.order_by('day', 'time')),
            'coursegroupsubscription_set'
        ).annotate(
            confirmed_subscriptions=Count(
                'coursegroupsubscription',
                filter=Q(coursegroupsubscription__is_confirmed=True)
            ),
            unconfirmed_subscriptions=Count(
                'coursegroupsubscription',
                filter=Q(coursegroupsubscription__is_confirmed=False)
            ),
            available_capacity=F('capacity') - Count(
                'coursegroupsubscription',
                filter=Q(coursegroupsubscription__is_confirmed=True)
            )
        ).annotate(
            has_seats=Case(
                When(available_capacity__gt=0, then=True),
                default=False,
                output_field=BooleanField()
            )
        )
        
        # Custom filters
        has_seats = self.request.query_params.get('has_seats')
        if has_seats is not None:
            if has_seats.lower() == 'true':
                queryset = queryset.filter(available_capacity__gt=0)
            else:
                queryset = queryset.filter(available_capacity__lte=0)
            
        min_available = self.request.query_params.get('min_available')
        if min_available:
            queryset = queryset.filter(available_capacity__gte=int(min_available))
            
        return queryset.order_by( 'teacher__order','course__title', 'teacher__name')


class DashboardSubscriptionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrPrivateToken]
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

class DashboardSubscriptionsSimpleView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrPrivateToken]
    serializer_class = SubscriptionSimpleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['student', 'course', 'course_group', 'is_confirmed']
    search_fields = [
        'student__name', 'student__user__username', 'student__parent_phone',
        'course__title', 'course_group__teacher__name'
    ]
    ordering_fields = ['created_at', 'confirmed_at']
    ordering = ['-created_at']

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
    # permission_classes = [IsAdminUser]

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
    # permission_classes = [IsAdminUser]

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
                confirmed_at=timezone.now(),
                is_declined=False,
                decline_note=None,
                declined_at=None

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


class AdminDeleteSubscriptionView(APIView):
    # permission_classes = [IsAdminUser]

    def delete(self, request, subscription_id):
        try:
            # Get the subscription
            subscription = get_object_or_404(CourseGroupSubscription, id=subscription_id)
            
            # Delete the subscription
            subscription.delete()
            
            return Response(
                {
                    "success": True,
                    "message": "تم حذف الاشتراك بنجاح",
                    "deleted_subscription_id": subscription_id
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )








class SubscriptionListView(APIView):
    pagination_class = CustomPageNumberPagination

    def get(self, request):
        params = request.query_params

        # Base queryset
        student_queryset = Student.objects.filter(
            coursegroupsubscription__isnull=False
        ).distinct().select_related(
            'year', 'type_education'
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
        if 'type_education' in params:
            student_queryset = student_queryset.filter(
                type_education_id=params['type_education']
            )
        if 'year_id' in params:
            student_queryset = student_queryset.filter(
                year_id=params['year_id']
            )
        if 'is_confirmed' in params:
            student_queryset = student_queryset.filter(
                coursegroupsubscription__is_confirmed=params['is_confirmed'].lower() == 'true'
            )
        # Add teacher filter
        if 'teacher_id' in params:
            student_queryset = student_queryset.filter(
                coursegroupsubscription__course_group__teacher_id=params['teacher_id']
            )
        if 'has_unconfirmed_subscriptions' in params:
            if params['has_unconfirmed_subscriptions'].lower() == 'true':
                student_queryset = student_queryset.filter(
                    Exists(
                        CourseGroupSubscription.objects.filter(
                            student_id=OuterRef('id'),
                            is_confirmed=False,
                            is_declined=False
                        )
                    )
                )
            else:
                student_queryset = student_queryset.exclude(
                    Exists(
                        CourseGroupSubscription.objects.filter(
                            student_id=OuterRef('id'),
                            is_confirmed=False,
                            is_declined=False
                        )
                    )
                )
        if 'has_declined_subscriptions' in params:
            if params['has_declined_subscriptions'].lower() == 'true':
                student_queryset = student_queryset.filter(
                    Exists(
                        CourseGroupSubscription.objects.filter(
                            student_id=OuterRef('id'),
                            is_declined=True
                        )
                    )
                )
            else:
                student_queryset = student_queryset.exclude(
                    Exists(
                        CourseGroupSubscription.objects.filter(
                            student_id=OuterRef('id'),
                            is_declined=True
                        )
                    )
                )

        # Search
        search_term = params.get('search', '').strip()
        if search_term:
            student_queryset = student_queryset.filter(
                Q(name__icontains=search_term) |
                Q(user__username__icontains=search_term) |
                Q(parent_phone__icontains=search_term) |
                Q(code__icontains=search_term) |
                Q(coursegroupsubscription__course__title__icontains=search_term) |
                Q(coursegroupsubscription__course_group__teacher__name__icontains=search_term)
            ).distinct()

        # Accurate subscription count annotations using Subquery
        confirmed_subs = CourseGroupSubscription.objects.filter(
            student_id=OuterRef('pk'),
            is_confirmed=True
        ).values('student_id').annotate(c=Count('id')).values('c')

        unconfirmed_subs = CourseGroupSubscription.objects.filter(
            student_id=OuterRef('pk'),
            is_confirmed=False,
            is_declined=False
        ).values('student_id').annotate(c=Count('id')).values('c')

        declined_subs = CourseGroupSubscription.objects.filter(
            student_id=OuterRef('pk'),
            is_declined=True
        ).values('student_id').annotate(c=Count('id')).values('c')

        student_queryset = student_queryset.annotate(
            confirmed_count=Subquery(confirmed_subs, output_field=IntegerField()),
            unconfirmed_count=Subquery(unconfirmed_subs, output_field=IntegerField()),
            declined_count=Subquery(declined_subs, output_field=IntegerField())
        )

        # Prepare response data
        students_data = []
        for student in student_queryset:
            confirmed = student.confirmed_count or 0
            unconfirmed = student.unconfirmed_count or 0
            declined = student.declined_count or 0

            # Get all subscriptions for the student to include teacher names
            subscriptions = CourseGroupSubscription.objects.filter(student=student).select_related(
                'course_group__teacher'
            )
            
            teachers = []
            for sub in subscriptions:
                if sub.course_group.teacher:
                    teachers.append({
                        'id': sub.course_group.teacher.id,
                        'name': sub.course_group.teacher.name
                    })
            
            # Remove duplicate teachers
            unique_teachers = []
            seen_teacher_ids = set()
            for teacher in teachers:
                if teacher['id'] not in seen_teacher_ids:
                    seen_teacher_ids.add(teacher['id'])
                    unique_teachers.append(teacher)

            students_data.append({
                'student_id': student.id,
                'student_name': student.name,
                'student_code': student.code,
                'student_division': student.division,
                'student_phone': student.user.username,
                'parent_phone': student.parent_phone,
                'student_government': student.government,
                'student_year': student.year.name if student.year else None,
                'type_education': student.type_education.name if student.type_education else None,
                'confirmed_subscriptions_count': confirmed,
                'unconfirmed_subscriptions_count': unconfirmed,
                'declined_subscriptions_count': declined,
                'has_unconfirmed_subscriptions': unconfirmed > 0,
                'has_declined_subscriptions': declined > 0,
                'teachers': unique_teachers  # Include list of teachers
            })

        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(students_data, request)
        return paginator.get_paginated_response(page)





class StudentSubscriptionDetailView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request, student_id):
        try:
            student = Student.objects.select_related(
                'year', 'type_education'
            ).prefetch_related(
                Prefetch('coursegroupsubscription_set', 
                        queryset=CourseGroupSubscription.objects.select_related(
                            'course', 'course_group', 'course_group__teacher'
                        ).prefetch_related(
                            'course_group__times'
                        ))
            ).get(id=student_id)

            subscriptions = student.coursegroupsubscription_set.all()
            
            # Split subscriptions
            confirmed_subs = []
            unconfirmed_subs = []
            declined_subs = []
            
            for sub in subscriptions:
                sub_data = {
                    'subscription_id': sub.id,
                    'course_id': sub.course.id if sub.course else None,
                    'course_title': sub.course.title if sub.course else None,
                    'year_id': sub.course.year.id if sub.course and sub.course.year else None,
                    'year_name': sub.course.year.name if sub.course and sub.course.year else None,
                    'group_id': sub.course_group.id if sub.course_group else None,
                    'group_capacity': sub.course_group.capacity if sub.course_group else None,
                    'teacher_id': sub.course_group.teacher.id if sub.course_group and sub.course_group.teacher else None,
                    'teacher_name': sub.course_group.teacher.name if sub.course_group and sub.course_group.teacher else None,
                    'teacher_education_language_type': sub.course_group.teacher.education_language_type if sub.course_group and sub.course_group.teacher else None,
                    'created_at': sub.created_at,
                    'confirmed_at': sub.confirmed_at,
                    'declined_at': sub.declined_at,
                    'decline_note': sub.decline_note,
                    'timeslots': [
                        {
                            'day': slot.day,
                            'time': slot.time.strftime('%H:%M')
                        } for slot in sub.course_group.times.all()
                    ]
                }
                
                if sub.is_declined:
                    declined_subs.append(sub_data)
                elif sub.is_confirmed:
                    confirmed_subs.append(sub_data)
                else:
                    unconfirmed_subs.append(sub_data)

            response_data = {
                'student_id': student.id,
                'student_name': student.name,
                'student_code': student.code,
                'student_division': student.division,
                'student_phone': student.user.username,
                'student_government': student.government,
                'student_year': student.year.name if student.year else None,
                'type_education': student.type_education.name if student.type_education else None,
                'confirmed_subscriptions_count': len(confirmed_subs),
                'unconfirmed_subscriptions_count': len(unconfirmed_subs),
                'declined_subscriptions_count': len(declined_subs),
                'has_unconfirmed_subscriptions': len(unconfirmed_subs) > 0,
                'has_declined_subscriptions': len(declined_subs) > 0,
                'confirmed_subscriptions': confirmed_subs,
                'unconfirmed_subscriptions': unconfirmed_subs,
                'declined_subscriptions': declined_subs
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Student.DoesNotExist:
            return Response(
                {'error': 'Student not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class AdminStudentCreateView(APIView):
    # permission_classes = [IsAdminUser]

    def post(self, request):
        username = request.data.get('username')
        if username and User.objects.filter(username=username).exists():
            return Response(
                {'username': ['يوجد مستخدم بنفس اسم المستخدم']},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AdminStudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()

            response_data = {
                'student_id': student.id,
                'user_id': student.user.id,
                'username': student.user.username,
                'email': student.user.email,
                'first_name': student.user.first_name,
                'last_name': student.user.last_name,
                'student_data': {
                    'name': student.name,
                    'parent_phone': student.parent_phone,
                    'code': student.code,
                    'government': student.government,
                    'year': student.year.name if student.year else None,
                    'type_education': student.type_education.name if student.type_education else None,
                },
                'message': 'Student created successfully'
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminStudentUpdateView(APIView):
    # permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminStudentCreateSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            student = serializer.save()

            response_data = {
                'student_id': student.id,
                'user_id': student.user.id,
                'username': student.user.username,
                'email': student.user.email,
                'first_name': student.user.first_name,
                'last_name': student.user.last_name,
                'student_data': {
                    'name': student.name,
                    'parent_phone': student.parent_phone,
                    'code': student.code,
                    'block': student.block,
                    'government': student.government,
                    'year': student.year.name if student.year else None,
                    'type_education': student.type_education.name if student.type_education else None,
                },
                'message': 'Student updated successfully'
            }

            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminStudentDetailView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        response_data = {
            'student_id': student.id,
            'user_id': student.user.id,
            'username': student.user.username,
            'email': student.user.email,
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'student_data': {
                'name': student.name,
                'parent_phone': student.parent_phone,
                'code': student.code,
                'government': student.government,
                'year': student.year.name if student.year else None,
                'type_education': student.type_education.name if student.type_education else None,
            }
        }
        return Response(response_data)

    def delete(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        student.user.delete()  # This also deletes the student due to on_delete=models.CASCADE
        return Response({'message': 'Student and associated user deleted successfully'})


class AdminTeacherCreateView(APIView):
    # permission_classes = [IsAdminUser]

    def post(self, request):
        username = request.data.get('username')
        if username and User.objects.filter(username=username).exists():
            return Response(
                {'username': ['يوجد مستخدم بنفس اسم المستخدم']},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AdminTeacherCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            teacher = serializer.save()

            response_data = {
                'teacher_id': teacher.id,
                'user_id': teacher.user.id,
                'username': teacher.user.username,
                'email': teacher.user.email,
                'first_name': teacher.user.first_name,
                'last_name': teacher.user.last_name,
                'teacher_data': {
                    'name': teacher.name,
                    'specialization': teacher.specialization,
                    'education_language_type': teacher.education_language_type,
                    'order': teacher.order,
                    'description': teacher.description,
                    'promo_video': request.build_absolute_uri(teacher.promo_video.url) if teacher.promo_video else None,
                    'promo_video_link': teacher.promo_video_link,
                    'image': request.build_absolute_uri(teacher.image.url) if teacher.image else None,
                },
                'message': 'Teacher created successfully'
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminTeacherUpdateView(APIView):
    # permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            teacher = Teacher.objects.get(pk=pk)
        except Teacher.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminTeacherCreateUpdateSerializer(teacher, data=request.data, partial=True)
        if serializer.is_valid():
            teacher = serializer.save()

            response_data = {
                'teacher_id': teacher.id,
                'user_id': teacher.user.id,
                'username': teacher.user.username,
                'email': teacher.user.email,
                'first_name': teacher.user.first_name,
                'last_name': teacher.user.last_name,
                'teacher_data': {
                    'name': teacher.name,
                    'specialization': teacher.specialization,
                    'education_language_type': teacher.education_language_type,
                    'order': teacher.order,
                    'description': teacher.description,
                    'promo_video': request.build_absolute_uri(teacher.promo_video.url) if teacher.promo_video else None,
                    'promo_video_link': teacher.promo_video_link,
                    'image': request.build_absolute_uri(teacher.image.url) if teacher.image else None,
                },
                'message': 'Teacher updated successfully'
            }

            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






from django.contrib.auth import get_user_model
from django.db import transaction

class AdminTeacherDetailView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            teacher = Teacher.objects.get(pk=pk)
        except Teacher.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)

        response_data = {
            'teacher_id': teacher.id,
            'user_id': teacher.user.id,
            'username': teacher.user.username,
            'email': teacher.user.email,
            'first_name': teacher.user.first_name,
            'last_name': teacher.user.last_name,
            'teacher_data': {
                'name': teacher.name,
                'specialization': teacher.specialization,
                'education_language_type': teacher.education_language_type,
                'order': teacher.order,
                'description': teacher.description,
                'promo_video': request.build_absolute_uri(teacher.promo_video.url) if teacher.promo_video else None,
                'promo_video_link': teacher.promo_video_link,
                'image': request.build_absolute_uri(teacher.image.url) if teacher.image else None,
            }
        }
        return Response(response_data)

    def delete(self, request, pk):
        try:
            teacher = Teacher.objects.get(pk=pk)
        except Teacher.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get the user before deleting the teacher
        user = teacher.user
        
        # First delete the teacher
        teacher.delete()
        
        # Then delete the associated user
        user.delete()
        
        return Response({'message': 'Teacher and associated user deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class AdminCreateSubscriptionsView(APIView):
    # permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminCreateSubscriptionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        student_id = serializer.validated_data['student_id']
        group_ids = serializer.validated_data['group_ids']

        try:
            student = get_object_or_404(Student, id=student_id)
            created_subscriptions = []
            existing_subscriptions = []
            failed_groups = []

            for group_id in group_ids:
                group = get_object_or_404(CourseGroup, id=group_id)
                
                # Check if subscription already exists
                if CourseGroupSubscription.objects.filter(student=student, course_group=group).exists():
                    existing_subscriptions.append(group_id)
                    continue
                
                try:
                    # Create confirmed subscription
                    subscription = CourseGroupSubscription.objects.create(
                        student=student,
                        course=group.course,
                        course_group=group,
                        is_confirmed=True,
                        confirmed_at=timezone.now()
                    )
                    created_subscriptions.append(subscription.id)
                except Exception as e:
                    failed_groups.append({
                        'group_id': group_id,
                        'error': str(e)
                    })

            response_data = {
                'success': True,
                'student_id': student.id,
                'student_name': student.name,
                'created_subscriptions': created_subscriptions,
                'existing_subscriptions': existing_subscriptions,
                'failed_groups': failed_groups,
                'message': 'Subscription process completed'
            }

            if not created_subscriptions and not existing_subscriptions and failed_groups:
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CourseGroupListView(APIView):
    def get(self, request):
        # Get query parameters
        year_id = request.query_params.get('year_id')
        type_education_id = request.query_params.get('type_education_id')
        course_id = request.query_params.get('course_id')
        search = request.query_params.get('search', '').strip()
        
        # Base queryset
        queryset = Course.objects.select_related(
            'year', 'type_education'
        ).prefetch_related(
            'coursegroup_set',
            'coursegroup_set__teacher',
            'coursegroup_set__times'
        ).order_by('title')
        
        # Apply filters
        if year_id:
            queryset = queryset.filter(year_id=year_id)
        if type_education_id:
            queryset = queryset.filter(type_education_id=type_education_id)
        if course_id:
            queryset = queryset.filter(id=course_id)
        
        # Apply search
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(year__name__icontains=search) |
                Q(type_education__name__icontains=search) |
                Q(coursegroup__teacher__name__icontains=search)
            ).distinct()
        
        # Serialize data
        serializer = CourseSerializerDetail(
            queryset, 
            many=True,
            context={'request': request}
        )
        
        return Response({
            'courses': serializer.data
        })


class TeacherStatsView(APIView):
    def get(self, request):
        teachers = Teacher.objects.annotate(
            group_count=Count('coursegroup', distinct=True),
            confirmed_subscriptions=Count(
                'coursegroup__coursegroupsubscription',
                filter=Q(coursegroup__coursegroupsubscription__is_confirmed=True),
                distinct=True
            ),
            unconfirmed_subscriptions=Count(
                'coursegroup__coursegroupsubscription',
                filter=Q(coursegroup__coursegroupsubscription__is_confirmed=False),
                distinct=True
            )
        ).select_related('user').prefetch_related('coursegroup_set')

        data = []
        for teacher in teachers:
            data.append({
                'teacher_id': teacher.id,
                'name': teacher.name,
                'specialization': teacher.specialization,
                'education_language_type': teacher.education_language_type,
                'order': teacher.order,
                'image': teacher.image.url if teacher.image else None,
                'total_groups': teacher.group_count,
                'confirmed_subscriptions': teacher.confirmed_subscriptions,
                'unconfirmed_subscriptions': teacher.unconfirmed_subscriptions,
            })

        return Response({'teachers': data})

class TeacherStudentsView(APIView):
    def get(self, request, teacher_id):
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            
            # Get confirmed subscriptions
            confirmed_subs = CourseGroupSubscription.objects.filter(
                course_group__teacher=teacher,
                is_confirmed=True
            ).select_related('student', 'course_group')
            
            # Get unconfirmed subscriptions
            unconfirmed_subs = CourseGroupSubscription.objects.filter(
                course_group__teacher=teacher,
                is_confirmed=False
            ).select_related('student', 'course_group')

            def build_student_data(subscriptions):
                students = {}
                for sub in subscriptions:
                    if sub.student.id not in students:
                        students[sub.student.id] = {
                            'student_id': sub.student.id,
                            'name': sub.student.name,
                            'code': sub.student.code,
                            'government': sub.student.government,
                            'subscriptions': []
                        }
                    students[sub.student.id]['subscriptions'].append({
                        'subscription_id': sub.id,
                        'course_id': sub.course.id,
                        'course_title': sub.course.title,
                        'group_id': sub.course_group.id,
                        'created_at': sub.created_at,
                        'confirmed_at': sub.confirmed_at
                    })
                return list(students.values())

            response_data = {
                'teacher_id': teacher.id,
                'teacher_name': teacher.name,
                'teacher_education_language_type': teacher.education_language_type,
                'confirmed_students': build_student_data(confirmed_subs),
                'unconfirmed_students': build_student_data(unconfirmed_subs)
            }

            return Response(response_data)

        except Teacher.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=404)



class DeclineSubscriptionView(APIView):
    # permission_classes = [IsAdminUser]
    
    def post(self, request, subscription_id):
        try:
            subscription = CourseGroupSubscription.objects.get(id=subscription_id)
            
            # Removed the is_confirmed check
            # Get note from request data (empty string if not provided)
            decline_note = request.data.get('decline_note', '')
            
            # Update subscription
            subscription.is_confirmed = False  # Add this to unconfirm if it was confirmed
            subscription.is_declined = True
            subscription.decline_note = decline_note
            subscription.declined_at = timezone.now()
            subscription.save()
            
            return Response({
                "success": True,
                "message": "تم رفض الاشتراك بنجاح",
                "subscription_id": subscription.id,
                "student_id": subscription.student.id,
                "student_name": subscription.student.name,
                "course_title": subscription.course.title,
                "decline_note": subscription.decline_note,
                "declined_at": subscription.declined_at
            })
            
        except CourseGroupSubscription.DoesNotExist:
            return Response(
                {"error": "الاشتراك غير موجود"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )



class BulkDeclineSubscriptionsView(APIView):
    # permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = BulkDeclineSubscriptionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        subscription_data = serializer.validated_data['subscriptions']
        results = {
            'successful': [],
            'failed': []
            # Removed 'already_confirmed' as we no longer track this
        }

        for item in subscription_data:
            try:
                subscription = CourseGroupSubscription.objects.get(
                    id=item['subscription_id']
                )
                
                # Removed the is_confirmed check
                subscription.is_confirmed = False  # Add this to unconfirm if it was confirmed
                subscription.is_declined = True
                subscription.decline_note = item['decline_note']
                subscription.declined_at = timezone.now()
                subscription.save()
                
                results['successful'].append({
                    'subscription_id': subscription.id,
                    'student_id': subscription.student.id,
                    'course_title': subscription.course.title,
                    'decline_note': subscription.decline_note
                })
                
            except CourseGroupSubscription.DoesNotExist:
                results['failed'].append({
                    'subscription_id': item['subscription_id'],
                    'error': 'Subscription not found'
                })
            except Exception as e:
                results['failed'].append({
                    'subscription_id': item.get('subscription_id', 'unknown'),
                    'error': str(e)
                })

        return Response({
            'total_processed': len(subscription_data),
            'successful_count': len(results['successful']),
            'failed_count': len(results['failed']),
            'details': results
        }, status=status.HTTP_200_OK)





#^ < ==============================[ <- Logs -> ]============================== > ^#

class RequestLogListView(generics.ListAPIView):
    queryset = RequestLog.objects.all()
    serializer_class = RequestLogSerializer
    # permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = RequestLogFilter 
    search_fields = ['path', 'view_name']
    ordering_fields = ['timestamp', 'response_time', 'status_code']
    ordering = ['-timestamp']

class RequestLogDeleteView(APIView):
    # permission_classes = [IsAdminUser]

    def delete(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date and not end_date:
            return Response(
                {"error": "At least one of start_date or end_date must be provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start building the query
        query_filter = {}
        
        # Process start_date if provided
        if start_date:
            try:
                # Try to parse as ISO datetime first
                start_datetime = parse_datetime(start_date)
                
                # If that fails, try to parse as date only
                if not start_datetime:
                    date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                    start_datetime = timezone.make_aware(datetime.datetime.combine(date_obj, datetime.time.min))
                
                # If it's still None, it's an invalid format
                if not start_datetime:
                    return Response(
                        {"error": "Invalid start_date format. Use ISO format (YYYY-MM-DDThh:mm:ss) or YYYY-MM-DD"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                query_filter['timestamp__gte'] = start_datetime
                
            except ValueError:
                return Response(
                    {"error": "Invalid start_date format. Use ISO format (YYYY-MM-DDThh:mm:ss) or YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Process end_date if provided
        if end_date:
            try:
                # Try to parse as ISO datetime first
                end_datetime = parse_datetime(end_date)
                
                # If that fails, try to parse as date only
                if not end_datetime:
                    date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
                    end_datetime = timezone.make_aware(datetime.datetime.combine(date_obj, datetime.time.max))
                
                # If it's still None, it's an invalid format
                if not end_datetime:
                    return Response(
                        {"error": "Invalid end_date format. Use ISO format (YYYY-MM-DDThh:mm:ss) or YYYY-MM-DD"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                query_filter['timestamp__lte'] = end_datetime
                
            except ValueError:
                return Response(
                    {"error": "Invalid end_date format. Use ISO format (YYYY-MM-DDThh:mm:ss) or YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Debug info before deletion
        logs_before_delete = RequestLog.objects.filter(**query_filter).count()
        
        # Delete logs
        deleted, _ = RequestLog.objects.filter(**query_filter).delete()
        
        # Add debug info to response
        return Response({
            "message": f"Successfully deleted {deleted} logs",
            "deleted_count": deleted,
            "found_before_delete": logs_before_delete,
            "query_filter": {
                "start_date": str(query_filter.get('timestamp__gte')),
                "end_date": str(query_filter.get('timestamp__lte'))
            }
        })

