from django.urls import path
from . import views
from .views import AdminSignInView, MySubscriptionsView, TeacherSignInView

urlpatterns = [
    #* < ==============================[ <- Auth  -> ]============================== > ^#
    path("student-sign-in", views.StudentSignInView.as_view(), name="student_sign_in"),
    path("student-sign-up", views.StudentSignUpView.as_view(), name="student_sign_up"),
    path("student-sign-code", views.StudentSignCodeView.as_view(), name="student_sign_code"),
    #* < ==============================[ <- Reset Password  -> ]============================== > ^#
    path("request-reset-password", views.RequestResetPasswordView.as_view(), name="request_password_reset"),
    path("verify-pin-code", views.VerifyPinCodeView.as_view(), name="verify_pin_code"),
    path("reset-password", views.ResetPasswordView.as_view(), name="reset_password"),
    #* < ==============================[ <- Profile  -> ]============================== > ^#
    path("student-profile", views.StudentProfileView.as_view(), name="student_profile"),
    path('teacher-signin/', TeacherSignInView.as_view(), name='teacher-signin'),


    path('admin-signin/', AdminSignInView.as_view(), name='admin-signin'),


    path('my-subscriptions/', MySubscriptionsView.as_view(), name='my-subscriptions'),
    
] 





