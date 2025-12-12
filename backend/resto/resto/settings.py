"""
Django settings for resto project.
"""

import os
from pathlib import Path
import dj_database_url

# -------------------------------------------------------------------
# BASE
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Secrets & debug
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-key-pas-bien")
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

# Hosts
ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,restot.onrender.com"
).split(",")

# -------------------------------------------------------------------
# Application definition
# -------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Media storage
    'cloudinary_storage',
    'cloudinary',

    # App métier
    'shop',
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

ROOT_URLCONF = 'resto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # tu peux mettre un dossier templates global si besoin
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'resto.wsgi.application'

# -------------------------------------------------------------------
# DATABASE
# -------------------------------------------------------------------
IS_PRODUCTION = os.environ.get("RENDER") is not None

# -------------------------------------------------------------------
# Password validation
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# Internationalization
# -------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# STATIC FILES
# -------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # important pour Render (collectstatic)

# -------------------------------------------------------------------
# MEDIA & CLOUDINARY
# -------------------------------------------------------------------
MEDIA_URL = '/media/'

if IS_PRODUCTION:
    # Configuration Cloudinary
    import cloudinary
    
    cloudinary.config(
        cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key=os.environ.get("CLOUDINARY_API_KEY"),
        api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
        secure=True
    )
    
    # Storage pour les médias
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
        "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
        "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
    }
else:
    # En local → fichiers sur disque
    MEDIA_ROOT = BASE_DIR / "media"

# -------------------------------------------------------------------
# SESSION PANIER
# -------------------------------------------------------------------
CART_SESSION_ID = "cart"

# -------------------------------------------------------------------
# LOGIN / LOGOUT
# -------------------------------------------------------------------
# Après login / logout → retour au menu principal
LOGIN_REDIRECT_URL = 'shop:meal_list'
LOGOUT_REDIRECT_URL = 'shop:meal_list'
