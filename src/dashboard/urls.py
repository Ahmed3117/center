from django.urls import path
from .views import (
    AdminCreateSubscriptionsView,
    AdminDeleteSubscriptionView,
    AdminStudentCreateView,
    AdminStudentDetailView,
    AdminStudentUpdateView,
    AdminTeacherCreateView,
    AdminTeacherDetailView,
    AdminTeacherUpdateView,
    ApplyStudentCodeView,
    BulkDeclineSubscriptionsView,
    ConfirmSubscriptionsView,
    CourseGroupListView,
    DashboardCourseGroupsView,
    DashboardCoursesView,
    DashboardStudentsView,
    DashboardSubscriptionsView,
    DeclineSubscriptionView,
    StudentSubscriptionDetailView,
    SubscriptionListView,
    TeacherStatsView,
    TeacherStudentsView,
    YearListCreateView, 
    YearRetrieveUpdateDestroyView,
    TypeEducationListCreateView,
    TypeEducationRetrieveUpdateDestroyView,
    TeacherListCreateView,
    TeacherRetrieveUpdateDestroyView,
    AboutPageView,
    FeatureListCreateView,
    FeatureRetrieveUpdateDestroyView,
    dashboard_stats
)

urlpatterns = [
    # Year URLs
    path('years/', YearListCreateView.as_view(), name='year-list-create'),
    path('years/<int:pk>/', YearRetrieveUpdateDestroyView.as_view(), name='year-detail'),
    
    # TypeEducation URLs
    path('education-types/', TypeEducationListCreateView.as_view(), name='education-type-list-create'),
    path('education-types/<int:pk>/', TypeEducationRetrieveUpdateDestroyView.as_view(), name='education-type-detail'),
    
    # Teacher URLs
    path('teachers/', TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('teachers/<int:pk>/', TeacherRetrieveUpdateDestroyView.as_view(), name='teacher-detail'),
    
    # AboutPage URL
    path('about-page/', AboutPageView.as_view(), name='about-page'),
    
    # Feature URLs
    path('features/', FeatureListCreateView.as_view(), name='feature-list-create'),
    path('features/<int:pk>/', FeatureRetrieveUpdateDestroyView.as_view(), name='feature-detail'),

    # needed get endpoints
    path('stats/', dashboard_stats, name='dashboard-stats'),
    path('students/', DashboardStudentsView.as_view(), name='dashboard-students'),
    
    path('courses/', DashboardCoursesView.as_view(), name='dashboard-courses'),
    path('coursegroups/', DashboardCourseGroupsView.as_view(), name='dashboard-coursegroups'),
    path('subscriptions/', DashboardSubscriptionsView.as_view(), name='dashboard-subscriptions'),


    # new
    path('apply-code/', ApplyStudentCodeView.as_view(), name='apply-code'),
    path('confirm-subscriptions/', ConfirmSubscriptionsView.as_view(), name='confirm-subscriptions'),
    path('subscriptions/<int:subscription_id>/delete/', AdminDeleteSubscriptionView.as_view(), name='admin-delete-subscription'),
    path('student-subscriptions/', SubscriptionListView.as_view(), name='subscription-list'),
    path('student-subscriptions/<int:student_id>/', StudentSubscriptionDetailView.as_view(), name='student-subscription-detail'),
    path('students/create/', AdminStudentCreateView.as_view(), name='admin-create-student'),
    path('students/update/<int:pk>/', AdminStudentUpdateView.as_view(), name='admin-update-student'),
    path('students/details/<int:pk>/', AdminStudentDetailView.as_view(), name='admin-student-detail'),
    path('teachers/create/', AdminTeacherCreateView.as_view(), name='admin-create-student'),
    path('teachers/update/<int:pk>/', AdminTeacherUpdateView.as_view(), name='admin-update-student'),
    path('teachers/details/<int:pk>/', AdminTeacherDetailView.as_view(), name='admin-teacher-detail'),
    path('subscriptions/create/', AdminCreateSubscriptionsView.as_view(), name='admin-create-subscriptions'),
    path('courses/details', CourseGroupListView.as_view(), name='course-group-list'),

    path('teachers/stats/', TeacherStatsView.as_view(), name='teacher-stats'),
    path('teachers/<int:teacher_id>/students/', TeacherStudentsView.as_view(), name='teacher-students'),
    path('subscriptions/<int:subscription_id>/decline/', DeclineSubscriptionView.as_view(), name='decline-subscription'),
    path('subscriptions/bulk-decline/', BulkDeclineSubscriptionsView.as_view(), name='bulk-decline-subscriptions'),
] 