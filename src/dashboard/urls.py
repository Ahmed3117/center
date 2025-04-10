from django.urls import path
from .views import (
    YearListCreateView, 
    YearRetrieveUpdateDestroyView,
    TypeEducationListCreateView,
    TypeEducationRetrieveUpdateDestroyView,
    TeacherListCreateView,
    TeacherRetrieveUpdateDestroyView,
    AboutPageView,
    FeatureListCreateView,
    FeatureRetrieveUpdateDestroyView
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
] 