from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('index/', first),
    path('auth/', main), 
    path('sign/', SignupUrls),
    path('back',CallBack)
]
