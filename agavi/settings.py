import os
from datetime import timedelta
from pathlib import Path

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
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
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'cloudinary_storage',
    'cloudinary',

    'rest_framework',
    'corsheaders',

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
    'AUTH_COOKIE_SECURE': False if DEBUG else True,
    # Set to True in production (use HTTPS)
    'REFRESH_COOKIE_SECURE': False if DEBUG else True,

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

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

MEDIA_URL = '/media/'
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True


UNFOLD = {
    "SITE_TITLE": "AGAVI ADMIN",
    "SITE_HEADER": "AGAVI ADMINISTRATION",
    "SITE_URL": "https://agavi.in",
    # "SITE_ICON": lambda request: static("icon.svg"),  # both modes, optimise for 32px height
    "SITE_ICON": {
        "light": lambda request: static("icon-light.svg"),  # light mode
        "dark": lambda request: static("icon-dark.svg"),  # dark mode
    },
    # "SITE_LOGO": lambda request: static("logo.svg"),  # both modes, optimise for 32px height
    "SITE_LOGO": {
        "light": lambda request: static("logo-light.svg"),  # light mode
        "dark": lambda request: static("logo-dark.svg"),  # dark mode
    },
    "SITE_SYMBOL": "speed",  # symbol from icon set
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": lambda request: static("favicon.svg"),
        },
    ],
    "SHOW_HISTORY": True,  # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True,  # show/hide "View on site" button, default: True
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",
            "subtle-dark": "156 163 175",
            "default-light": "75 85 99",
            "default-dark": "209 213 219",
            "important-light": "17 24 39",
            "important-dark": "243 244 246",
        },
        # lime color scheme
        "primary": {
            "50": "247 254 231",
            "100": "236 252 203",
            "200": "217 249 157",
            "300": "190 242 100",
            "400": "163 230 53",
            "500": "132 204 22",
            "600": "101 163 13",
            "700": "77 124 15",
            "800": "63 98 18",
            "900": "54 83 20",
            "950": "26 46 5",
        },
    },

    "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": False,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": _("Navigation"),
                "separator": True,  # Top border
                "collapsible": True,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:index"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Users"),
                        "icon": "people",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },

                    {
                        "title": _("User Addresses"),
                        "icon": "location_on",
                        "link": reverse_lazy("admin:accounts_address_changelist"),
                    },
                    {
                        "title": _("Products"),
                        "icon": "store",
                        "link": reverse_lazy("admin:products_product_changelist"),
                    },

                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:products_category_changelist"),
                    },

                    {
                        "title": _("Carts"),
                        "icon": "shopping_cart",
                        "link": reverse_lazy("admin:cart_cart_changelist"),
                    },
                    {
                        "title": _("Orders and Payments"),
                        "icon": "shopping_bag",
                        "link": reverse_lazy("admin:app_list", kwargs={"app_label": "orders"}),
                    },
                ],
            },
        ],
    },
}
