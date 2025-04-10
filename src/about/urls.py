from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AboutPageWithFeaturesView, TeachersPublicView

urlpatterns = [
    # Public API endpoints
    path('info/', AboutPageWithFeaturesView.as_view(), name='about-info'),
    path('teachers/', TeachersPublicView.as_view(), name='teachers-list'),
]
