from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [

    path('sign-up/', SignUp.as_view()),
    path('log-in/', LogIn.as_view()),
    path('log-out/', Logout.as_view()),
    path('update-profile/', UpdateDetails.as_view()),
    path('send_otp/', ForgotPasswordOTP.as_view()),
    path('reset_password/', FogotPassword.as_view()),
    path('verify_email/', VerifyEmail.as_view()),
    path('change_password/', ResetPassword.as_view()),
]
