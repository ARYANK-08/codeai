from django.contrib import admin
from django.urls import path, include
from .views import generate_pdf

urlpatterns = [
    path('generate_pdf', generate_pdf, name='generate_pdf')
]
