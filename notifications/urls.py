from django.urls import path
from .views import *

urlpatterns = [
    path('send/', SendNotifications ,name="send-notifications"),
    path('confirm/<uidb64>/<token>/',  activate, name='act'),  
]
