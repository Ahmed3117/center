from django.urls import path
from .views import (
    ApplyStudentCodeView,
    ConfirmSubscriptionsView,
    DashboardCourseGroupsView,
    DashboardCoursesView,
    DashboardStudentsView,
    DashboardSubscriptionsView,
    SubscriptionListView,
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
    
    path('confirm-subscriptions/', ConfirmSubscriptionsView.as_view(), name='confirm-subscriptions'),
    path('apply-code/', ApplyStudentCodeView.as_view(), name='apply-code'),
    path('student-subscriptions/', SubscriptionListView.as_view(), name='subscription-list'),


] 