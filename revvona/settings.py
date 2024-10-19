import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('ENV') != 'PROD'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',') or [
    'localhost', '127.0.0.1']

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
    'checkout',
    'dashboard',
    'about',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Whitenoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'revvona.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'dashboard' / 'templates',
        ],
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

WSGI_APPLICATION = 'revvona.wsgi.application'

POSTGRES_URL = urlparse(os.getenv("DATABASE_URL"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': POSTGRES_URL.path.replace('/', ''),
        'USER': POSTGRES_URL.username,
        'PASSWORD': POSTGRES_URL.password,
        'HOST': POSTGRES_URL.hostname,
        'PORT': 5432,
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
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=300),
    # User will be logged in for 10 days
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_COOKIE': 'access_token',
    'REFRESH_COOKIE': 'refresh_token',
    'AUTH_COOKIE_SECURE': not DEBUG,
    'REFRESH_COOKIE_SECURE': not DEBUG,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Enable CSRF protection
if os.getenv('ENV') == 'PROD':
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

MEDIA_URL = '/media/'
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
    'SECURE': True,
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASS')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
EMAIL_USE_TLS = True

# Frontend and Brand settings
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
BRAND_NAME = os.getenv('BRAND_NAME', 'REVVONA')

# unfold settings
# These settings are frontend dependent and should be adjusted based on your frontend
UNFOLD = {
    "SITE_TITLE": _(f"{BRAND_NAME} ADMIN"),
    "SITE_HEADER": _(f"{BRAND_NAME} ADMINISTRATION"),
    "SITE_URL": FRONTEND_URL,
    "SITE_ICON": f"{FRONTEND_URL}/favicon.ico",

    "SITE_LOGO": {
        "light": f"{FRONTEND_URL}/logo.png",
        "dark": f"{FRONTEND_URL}/logo-dark.png",
    },

    "SITE_SYMBOL": "grass",
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": f"{FRONTEND_URL}/favicon.ico",
        },
    ],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "DASHBOARD_CALLBACK": "dashboard.views.dashboard_callback",
    "STYLES": [
        lambda request: static("css/styles.css"),
    ],
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",
            "subtle-dark": "156 163 175",
            "default-light": "75 85 99",
            "default-dark": "209 213 219",
            "important-light": "17 24 39",
            "important-dark": "243 244 246",
        },
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
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            # Supported icon set: https://fonts.google.com/icons
            {
                "title": _("Product Management"),
                "separator": True,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "speed",
                        "link": reverse_lazy("admin:index"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:products_category_changelist"),
                    },
                    {
                        "title": _("Products and Reviews"),
                        "icon": "potted_plant",
                        "link": reverse_lazy("admin:products_product_changelist"),
                    },
                ],
            },
            {
                "title": _("Users and Groups"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                    {
                        "title": _("User Addresses"),
                        "icon": "location_on",
                        "link": reverse_lazy("admin:accounts_address_changelist"),
                    },
                    {
                        "title": _("User Carts"),
                        "icon": "shopping_cart",
                        "link": reverse_lazy("admin:cart_cart_changelist"),
                    },
                ],
            },
            {
                "title": _("Orders and Payments"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Orders"),
                        "icon": "shopping_bag",
                        "link": reverse_lazy("admin:checkout_order_changelist"),
                    },
                    {
                        "title": _("Payments"),
                        "icon": "payment",
                        "link": reverse_lazy("admin:checkout_payment_changelist"),
                    },
                ],
            },
            {
                "title": _("Legal and Branding"),
                "collapsible": True,
                "items": [
                    {
                        "title": _(f"About {BRAND_NAME.capitalize()}"),
                        "icon": "info",
                        "link": reverse_lazy("admin:about_about_changelist"),
                    },
                    {
                        "title": _("Legal Documents"),
                        "icon": "gavel",
                        "link": reverse_lazy("admin:about_legal_changelist"),
                    },
                    {
                        "title": _("Socials"),
                        "icon": "thumb_up",
                        "link": reverse_lazy("admin:about_instagram_changelist"),
                    },
                    {
                        "title": _("Testimonials"),
                        "icon": "star",
                        "link": reverse_lazy("admin:about_testimonial_changelist"),
                    },
                ],
            }
        ],
    },
}
