"""
Django settings for POS_SYSTEM project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
from email.policy import default
import os
from pathlib import Path
import environ
import pymysql


# Initialize environment variables
env = environ.Env()

# Read .env file (only for local development)
environ.Env.read_env()


pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-z#bxi2e(75qy&1r2xd5-oo4vtm_5k2q992nt2f$@*aq=q8&ws8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = [
    '127.0.0.1', 'localhost',  
    ".vercel.app",
    "mysql://root:iLUNESurqBBWmsppSLqQkkzbjFCRccnN@mysql.railway.internal:3306/railway"
    ]




# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pos_app',
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

ROOT_URLCONF = 'POS_SYSTEM.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

WSGI_APPLICATION = 'POS_SYSTEM.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases




if env('RAILWAY_MYSQL_HOST', default=None):
    # Use Railway MySQL settings for production
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('MYSQL_DATABASE'),
            'USER': env('MYSQLUSER'),
            'PASSWORD': env('MYSQL_ROOT_PASSWORD'),
            'HOST': env('RAILWAY_MYSQL_HOST'),  # Correct Railway MySQL host
            'PORT': env('RAILWAY_MYSQL_PORT'),  # Use the correct port from your env variables
        }
    }
else:
    # Use localhost MySQL for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('MYSQL_DATABASE'),
            'USER': env('MYSQLUSER'),
            'PASSWORD': env('MYSQL_ROOT_PASSWORD'),
            'HOST': env('RAILWAY_MYSQL_HOST',default='127.0.0.1'),   # Default to localhost if not set
            'PORT': env('RAILWAY_MYSQL_PORT', default=env('port')),     # Default MySQL port
        }
    }


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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/



# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'  
LOGIN_REDIRECT_URL = '/inventory/'
LOGOUT_REDIRECT_URL = '/login/'  # Redirect to login page after logout
