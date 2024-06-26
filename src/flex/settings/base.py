"""
Django settings for flex project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# with open(os.path.expanduser('~/.flex-secret')) as secret_file:
#     SECRET_KEY = secret_file.read().strip()

SECRET_KEY = "CdxIj8y95ma4wBX3FnUgofFsKbDg4tti64'"

# Application definition

INSTALLED_APPS = (

    # http://django-registration-redux.readthedocs.io/en/latest/quickstart.html#quickstart
    # django-registration-redux
    'registration',
    # Why up here? #http://stackoverflow.com/questions/34577607/django-registration-redux-change-password-link

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # userena

    # For django-userena http://django-userena.readthedocs.io/en/latest/installation.html
    # 'userena',
    # 'guardian',
    # 'easy_thumbnails',

    'crispy_forms',
    'django_select2',  # http://django-select2.readthedocs.io/en/latest/get_started.html
    'embed_video',  # https://github.com/jazzband/django-embed-video
    'imagekit', #https://github.com/matthewwithanm/django-imagekit

    # 'django_summernote',

    # My custom apps
    'profiles',
    'events',
    'excuses',
    'utilities',
)

AUTHENTICATION_BACKENDS = (
    #'userena.backends.UserenaAuthenticationBackend',
    #'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'profiles.models.PasswordResetRequiredMiddleware',
)

ROOT_URLCONF = 'flex.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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



WSGI_APPLICATION = 'flex.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Vancouver'

USE_I18N = True

USE_L10N = True

USE_TZ = True


ADMIN_SITE_HEADER = 'Timberline Flex Site - Administration'


# django-registration-redux
ACCOUNT_ACTIVATION_DAYS = 7
LOGIN_REDIRECT_URL = "/"

SITE_ID = 1

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# required for select2
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

