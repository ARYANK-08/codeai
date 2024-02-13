from django.contrib import admin
from django.urls import path, include
from .views import generate_pdf, profile_analysis, index, user_signin

urlpatterns = [
    path('generate_pdf', generate_pdf, name='generate_pdf'),
    path('profile_analysis', profile_analysis, name='profile_analysis'),
    path('', index, name='index'),
    path('user_signin', user_signin, name='user_signin')
]

