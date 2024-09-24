import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')


if os.getenv('ENV') == 'PROD':
    DEBUG = False
else:
    DEBUG = True

ALLOWED_HOSTS = [os.getenv('ALLOWED_HOST'),
                 '.cloudflarestorage.com', '.vercel.app']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',
    'storages',

    'accounts',
    'products',
    'cart',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Whitenoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',                    # CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agavi.urls'

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

WSGI_APPLICATION = 'agavi.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django_cockroachdb',
        'NAME': os.getenv('COCKROACH_DB_NAME'),
        'USER': os.getenv('COCKROACH_DB_USER'),
        'PASSWORD': os.getenv('COCKROACH_DB_PASS'),
        'HOST': os.getenv('COCKROACH_DB_HOST'),
        'PORT': os.getenv('COCKROACH_DB_PORT'),
        'OPTIONS': {
            'sslmode': 'require',
        },
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


SIMPLE_JWT = {
    # 5 hours for access token
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=300),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # 1 day for refresh token
    # Don't rotate refresh tokens on access token refresh
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,  # Blacklist tokens after rotation
    'UPDATE_LAST_LOGIN': False,  # Don't update the last login on token refresh

    'ALGORITHM': 'HS256',  # Default signing algorithm
    'SIGNING_KEY': SECRET_KEY,  # Use the Django secret key for token signing
    # Not required unless you're using asymmetric keys (RSA/ECDSA)
    'VERIFYING_KEY': None,
    'AUDIENCE': None,  # Not using specific audience validation
    'ISSUER': None,  # Not using issuer validation

    # Cookie settings for access and refresh tokens
    'AUTH_COOKIE': 'access_token',  # Name of the access token cookie
    'REFRESH_COOKIE': 'refresh_token',  # Name of the refresh token cookie

    # Set to True in production (use HTTPS)
    'AUTH_COOKIE_SECURE': True if os.getenv('ENV') == 'PROD' else False,
    # Set to True in production (use HTTPS)
    'REFRESH_COOKIE_SECURE': True if os.getenv('ENV') == 'PROD' else False,

    # Default token type in the Authorization header
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',  # Default header for authorization
    'USER_ID_FIELD': 'id',  # Field for the user ID
    'USER_ID_CLAIM': 'user_id',  # Claim for the user ID
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    # Only use AccessToken class
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',  # Claim used to store token type

    'JTI_CLAIM': 'jti',  # JWT token identifier claim for blacklisting

    # Settings for sliding tokens (not necessary if not using sliding tokens)
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


# # Enable CSRF protection
if os.getenv('ENV') == 'PROD':
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # custom JWT middleware for cookies based auth
        'accounts.authentication.CustomJWTAuthentication',
    )
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

MEDIA_URL = os.getenv('MEDIA_URL')

# S3 / Cloudflare R2 Configurations
AWS_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('R2_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL')
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_REGION_NAME = 'auto'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
