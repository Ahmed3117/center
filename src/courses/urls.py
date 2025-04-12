from django.urls import path
from .views import (
    GetTeacherFullDataView,
    StudentCoursesView,
    CourseGroupsView,
    SubscribeToGroupsView,
    StudentSubscriptionsView
)

urlpatterns = [
    path('student_courses/', StudentCoursesView.as_view(), name='student-courses'),
    path('<int:course_id>/<int:teacher_id>/groups/', CourseGroupsView.as_view(), name='course-groups'),
    path('subscribe/', SubscribeToGroupsView.as_view(), name='subscribe-to-groups'),
    path('subscriptions/', StudentSubscriptionsView.as_view(), name='student-subscriptions'),
    path('teachers/<int:id>/full-data/', GetTeacherFullDataView.as_view(), name='teacher-full-data'),
]