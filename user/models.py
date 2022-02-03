from email.policy import default
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    class Meta:
        verbose_name = 'CustomUser'
    GENDER_MAIL = 'male'
    GENDER_FEMAIL = 'female'
    GENDER_CHOICES = ((GENDER_MAIL, 'Male'),(GENDER_FEMAIL, 'Female'))
    LOGIN_EMAIL = 'email'
    LOGIN_GITHUB = 'github'
    LOGIN_KAKAO = 'kakao'
    LOGIN_CHOICES = ((LOGIN_EMAIL,'Email'),(LOGIN_KAKAO, 'Kakao'),(LOGIN_GITHUB, 'Github'))
    birthday = models.DateField(blank=True, null=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, default=GENDER_MAIL, )
    nickname = models.CharField(max_length=30,blank=True)
    profile_img = models.ImageField(upload_to='profile_img/',default='')
    login_method = models.CharField(choices=LOGIN_CHOICES, max_length=20, default=LOGIN_EMAIL)
