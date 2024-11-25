import environ
from pathlib import Path
import os
import environ
import django_heroku
import dj_database_url
from datetime import timedelta
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir' or os.path.join(BASE_DIR, 'subdir')
BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)  # Define the type and default for DEBUG
)

# Read the .env file for local development
# For production, ensure environment variables are set on Heroku
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))  # Ensure you have a .env file locally

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = env('SECRET_KEY', default='django-insecure-w)getnsr)9z21am-v4i2%)vz10ji05zcxkoa+xrzx)h7$=zaad')
SECRET_KEY = "django-insecure-w)getnsr)9z21am-v4i2%)vz10ji05zcxkoa+xrzx)h7$=zaad"
# Set Debug based on environment variable
DEBUG = env('DEBUG', default=True)

USER_APPROVAL_REQUIRED = True

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=[
        "127.0.0.1",
        "localhost",
        "social-distribution-1-3adb84f120d9.herokuapp.com",
        "social-sanket-603a86c4b610.herokuapp.com",
        "teal-rakshit-a972530cc317.herokuapp.com",
        "teal-pranav-0e8aa7849ad7.herokuapp.com",
        ".herokuapp.com",
    ],
)

# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'corsheaders',
    'backendApp',
    'channels',
]

AUTH_USER_MODEL = 'backendApp.Author'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must come first
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware"
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        'backendApp.authentication.NodeBasicAuthentication',
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ]
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # Frontend development server
    "http://localhost:8000",  # Backend development server
    "https://social-distribution-1-3adb84f120d9.herokuapp.com",  # Production domain
    'https://teal-rakshit-a972530cc317.herokuapp.com',
    "https://social-sanket-603a86c4b610.herokuapp.com",
    "https://teal-pranav-0e8aa7849ad7.herokuapp.com",
    "http://127.0.0.1:8000",  # Localhost alternative
]
CORS_ALLOW_CREDENTIALS = True

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'https://teal-rakshit-a972530cc317.herokuapp.com',
    "https://social-distribution-1-3adb84f120d9.herokuapp.com",
    "https://social-sanket-603a86c4b610.herokuapp.com",
    "https://teal-pranav-0e8aa7849ad7.herokuapp.com",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'node-password',
    'node-username',
]


# WhiteNoise Configuration (remove non-standard settings)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [BASE_DIR / "backendApp/static/",]

WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_INDEX_FILE = True

ROOT_URLCONF = "tealBackend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "backendApp/static/vue"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Database Configuration
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///' + str(BASE_DIR / 'db.sqlite3')),
}
print("This is database" , DATABASES)

# Password validation
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

# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [BASE_DIR / "backendApp/static/",]

WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_INDEX_FILE = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# Channels configuration
ASGI_APPLICATION = 'tealBackend.asgi.application'
WSGI_APPLICATION = 'tealBackend.wsgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Activate Django-Heroku.
django_heroku.settings(locals())
