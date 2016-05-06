DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.auth',
    'postnl_checkout.contrib.django_postnl_checkout'
]

SITE_ID = 1

# Enable time-zone support for Django 1.4 (ignored in older versions)
USE_TZ = True

# Generate random secret key
import random
SECRET_KEY = ''.join([
    random.SystemRandom().choice(
        'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    ) for i in range(50)
])

# Required for django-webtest to work
STATIC_URL = '/static/'

# PostNL specific settings
POSTNL_CHECKOUT_USERNAME = 'klant1'
POSTNL_CHECKOUT_PASSWORD = 'xx'
POSTNL_CHECKOUT_WEBSHOP_ID = 'a0713e4083a049a996c302f48bb3f535'
