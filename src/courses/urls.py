from django.urls import path
from .views import (
    StudentCoursesView,
    CourseGroupsView,
    SubscribeToGroupsView,
    StudentSubscriptionsView
)

urlpatterns = [
    path('student_courses/', StudentCoursesView.as_view(), name='student-courses'),
    path('<int:course_id>/groups/', CourseGroupsView.as_view(), name='course-groups'),
    path('subscribe/', SubscribeToGroupsView.as_view(), name='subscribe-to-groups'),
    path('subscriptions/', StudentSubscriptionsView.as_view(), name='student-subscriptions'),
]