from datetime import timedelta
import json
import random
import re
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from api.models import OTPVerification

# Create your views here.
@csrf_exempt
def sign_up(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, data['email']):
            return JsonResponse({'error': 'Invalid email'}, status=400)
        otp = OTPVerification.objects.filter(user=data['username'], otp_code=data['otp_code'], is_verified=False).last()
        if not otp:
            return JsonResponse({'err': 'Invalid OTP'}, status=400)
        if timezone.now() > otp.expired_at:
            otp.delete()
            return JsonResponse({'err': 'OTP expired'}, status=400)
        else:
            otp.is_verified = True
            otp.save()
        user = User.objects.create_user(data['username'], data['email'], data['password'])
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.save()
        OTPVerification.objects.filter(user=data['username']).delete()
        return JsonResponse({'msg': 'User created successfully'}, status=201)
    else:
        return JsonResponse({'err': 'Invalid request method'}, status=405)

@csrf_exempt
def send_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        otp_code = str(random.randint(100000, 999999))
        expired_at = timezone.now() + timedelta(minutes=5)
        OTPVerification.objects.create(user=data['username'], otp_code=otp_code, expired_at=expired_at)
        send_mail(
            'OTP for Sign Up in Chat Rooms',
            f'Your OTP code is: {otp_code}. It will expire in 5 minutes.',
            settings.EMAIL_HOST_USER,
            [data['email']],
            fail_silently=False,
        )
        return JsonResponse({'msg': 'OTP sent successfully'}, status=200)
    else:
        return JsonResponse({'err': 'Invalid request method'}, status=405)

@csrf_exempt
def sign_in(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = authenticate(username=data['email'], password=data['password'])
        if user is not None:
            login(request, user)
            return JsonResponse({'msg': 'Sign in successful'}, status=200)
        else:
            return JsonResponse({'err': 'Invalid credentials'}, status=400)
    else:
        return JsonResponse({'err': 'Invalid request method'}, status=405)