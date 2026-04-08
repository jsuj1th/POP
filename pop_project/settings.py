from pathlib import Path
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-pop-dev-key-change-in-production')

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mozilla_django_oidc',
    'observations',
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

ROOT_URLCONF = 'pop_project.urls'

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

WSGI_APPLICATION = 'pop_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ***REDACTED***
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# OIDC Configuration for TAMU Login
AUTHENTICATION_BACKENDS = [
    'observations.auth.TAMUOIDCAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',  # Keep default auth as fallback
]

# OIDC Settings for TAMU (Microsoft Azure AD)
OIDC_RP_CLIENT_ID = config('OIDC_RP_CLIENT_ID', default='')
OIDC_RP_CLIENT_SECRET = config('OIDC_RP_CLIENT_SECRET', default='')
OIDC_RP_SIGN_ALGO = 'RS256'
OIDC_RP_IDP_SIGN_ALGO = 'RS256'

# Required scope for OIDC
OIDC_RP_SCOPES = config('OIDC_RP_SCOPES', default='openid profile email')

# TAMU uses Azure AD, update these endpoints if needed
OIDC_OP_AUTHORIZATION_ENDPOINT = config('OIDC_OP_AUTHORIZATION_ENDPOINT', default='https://login.microsoftonline.com/common/oauth2/v2.0/authorize')
OIDC_OP_TOKEN_ENDPOINT = config('OIDC_OP_TOKEN_ENDPOINT', default='https://login.microsoftonline.com/common/oauth2/v2.0/token')
OIDC_OP_USER_ENDPOINT = config('OIDC_OP_USER_ENDPOINT', default='https://graph.microsoft.com/oidc/userinfo')
OIDC_OP_JWKS_ENDPOINT = config('OIDC_OP_JWKS_ENDPOINT', default='https://login.microsoftonline.com/common/discovery/v2.0/keys')

# For development only
OIDC_VERIFY_SSL = config('OIDC_VERIFY_SSL', default=True, cast=bool)

# Allow auto-login for new users
OIDC_CREATE_USER = True
OIDC_UPDATE_USER = True

# Allow OIDC claims to be retrieved
OIDC_USE_NONCE = config('OIDC_USE_NONCE', default=True, cast=bool)
OIDC_NONCE_SIZE = 32

# Store tokens for later use
OIDC_STORE_ID_TOKEN = True
