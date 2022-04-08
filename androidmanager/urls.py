from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('index/', first),
    path('auth/', main), 
    path('policy/', create_policy), 
]
