from django.contrib import admin
from django.urls import path, include
from .views import generate_pdf, profile_analysis

urlpatterns = [
    path('generate_pdf', generate_pdf, name='generate_pdf'),
    path('profile_analysis', profile_analysis, name='profile_analysis'),
]
