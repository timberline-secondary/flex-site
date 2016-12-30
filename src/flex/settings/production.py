#THIS IS A TEMPLATE FILE, COPT THIS AND RENAME IT: production_mysite.py

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
# ALLOWED_HOSTS = [www.hackerspace.sd72.bc.ca, hackerspace.sd72.bc.ca] or IPs

EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = open(os.path.expanduser('~/.flex-email-password')).read().strip()
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    #'/var/www/static/',
]
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static_cdn")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "media_cdn")


# # Static files (CSS, JavaScript, Images) ####################
# # https://docs.djangoproject.com/en/1.8/howto/static-files/
#
# # The absolute path to the directory where collectstatic will collect static files for deployment.
# # Set in production settings for deployment
# STATIC_ROOT = "/home/couture/www/hackerspace/static"
# # STATIC_ROOT = "/home/90158/www/hackerspace/static"
#
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, "static_in_project",  "static_root"),
#     # '/var/www/static/',
# )
#
# MEDIA_URL = "/media/"
# # The absolute path to the directory where collectstatic will collect static files for deployment.
# # Set properly in production settings for deployment
# MEDIA_ROOT = "/home/couture/www/hackerspace/media"
# # MEDIA_ROOT = "/home/90158/www/hackerspace/media"


# END STATIC #######################################
