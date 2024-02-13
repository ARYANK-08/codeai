from django.contrib import admin
from django.urls import path, include
from gemini.views import gemini

urlpatterns = [
    path('gemini', gemini, name='gemini'),
]
