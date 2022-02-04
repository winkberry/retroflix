import os
import json
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
with open(os.path.join(BASE_DIR, 'retroflix/config/secret.json')) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

SECRET_KEY = get_secret("SECRET_KEY")

DATABASES = {
    'default': {
        'ENGINE': get_secret('DATABASES')['default']['ENGINE'],
        'NAME': get_secret('DATABASES')['default']['NAME'],
        'USER': get_secret('DATABASES')['default']['USER'],
        'PASSWORD': get_secret('DATABASES')['default']['PASSWORD'],
        'HOST': get_secret('DATABASES')['default']['HOST'],
        'PORT': get_secret('DATABASES')['default']['PORT'],
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
    },
    
    
}
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'retroflix',
    'storages',
    'movie',
    'user',
    'review'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'retroflix.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'retroflix.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

AUTH_USER_MODEL = 'user.CustomUser'


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

with open(os.path.join(BASE_DIR, 'retroflix/config/aws.json')) as f:
    secret = json.loads(f.read())

AWS_ACCESS_KEY_ID = secret['AWS']['ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = secret['AWS']['SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = secret['AWS']['STORAGE_BUCKET_NAME']
AWS_REGION = 'ap-northeast-2'
AWS_DEFAULT_ACL = 'public-read' # 올린 파일을 누구나 읽을 수 있게 지정합니다!
AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (AWS_STORAGE_BUCKET_NAME,AWS_REGION)


with open(os.path.join(BASE_DIR, 'retroflix/config/email.json')) as f: 
    email = json.loads(f.read()) 

EMAIL_HOST = email['HOST'] 
EMAIL_PORT = int(email['PORT']) 
EMAIL_HOST_USER = email['HOST_USER'] 
EMAIL_HOST_PASSWORD = email['HOST_PASSWORD'] 
EMAIL_USE_TLS = True 
EMAIL_USE_SSL = False 
LOGIN_URL = '/sign-in'