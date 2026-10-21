from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/', views.sign_up),
    path('send-otp/', views.send_otp),
    # path('otp-verification/', views.otp_verification),
    path('sign-in/', views.sign_in),
]