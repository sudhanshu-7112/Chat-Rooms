from django.db import models

# Create your models here.

class OTPVerification(models.Model):
    user = models.CharField(max_length=20)
    otp_code = models.CharField(max_length=6)
    expired_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)