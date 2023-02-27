"""
Django settings for django_app project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
import os.path
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(".env")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# assert os.path.exists(BASE_DIR / ".env")
# load_dotenv(BASE_DIR / ".env")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

from django.core.management.utils import get_random_secret_key

SECRET_KEY = os.getenv("SECRET_KEY", get_random_secret_key())

CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS", "https://127.0.0.1 https://localhost"
).split(" ")

DEBUG = os.getenv("DEBUG", "False") in ("True", "true", "1")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1 localhost").split(" ")

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "local")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "polls",
    "bootstrap5",
    "themeapp",
    "django_extensions",
    # django-allauth
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "rest_framework",
    "rest_framework.authtoken",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # custom context processors
                "polls.context_processors.get_color",
            ],
        },
    },
]

WSGI_APPLICATION = "django_app.wsgi.application"

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

# db id of the entry in 'Sites' table
if DEVELOPMENT_MODE == "production":
    SITE_ID = 3
elif DEVELOPMENT_MODE == "staging":
    SITE_ID = 2
elif DEVELOPMENT_MODE == "local":
    SITE_ID = 1
else:
    raise Exception("DEVELOPMENT_MODE environment variable is not correct")

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
LOGIN_URL = "account_login"

# Provider specific settings allauth
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
            "key": "",
        },
        # to capture email/profile data from google Oauth
        "SCOPE": [
            "email",
        ],
    }
}


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

import os
import sys

import dj_database_url

if DEVELOPMENT_MODE == "local":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
elif len(sys.argv) > 0 and sys.argv[1] != "collectstatic":
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(
            os.environ.get("DATABASE_URL"), conn_max_age=0
        ),
    }

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# DRF global settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "rest_framework.permissions.IsAdminUser",
    ],
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
}

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

AUTH_USER_MODEL = "polls.User"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/


STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# The static files folder is staticfiles
# But the URL used to load these files are /static
STATIC_URL = "/static/"
STATIC_ROOT = Path(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [Path(BASE_DIR, "assets")]

# If you plan on storing static files in other locations outside
# of your individual Django-app static files, you will need to add
# an additional directive to your settings file.
# STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# Media setup for media files e.g images.
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(BASE_DIR, "assets/images")

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
