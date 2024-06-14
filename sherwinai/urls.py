from django.contrib import admin
from django.urls import path, include
from sherwinai.views import *

urlpatterns = [
        path('run-code/', RunCodeView.as_view(), name='run-code'),
        path('sherwinai/', code_runner, name='code_runner'),
        path('emmuai/', python_generate_code, name='python_generate_code'),
]
