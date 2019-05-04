"""
Django settings for estagio project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
# import tornado.web
# import tornado_websockets
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%%9tv_l-w4n+^^a(*3icg6@as1f!fywpltz-_!)wx8hojdstg('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# CELERY_BROKER_URL = 'amqp://192.168.15.11:5672'
# CELERY_BROKER_URL = 'amqp://david:123@192.168.15.11/amd'
# CELERY_RESULT_BACKEND = 'amqp://192.168.15.11:5672'
# CELERY_RESULT_BACKEND = 'amqp://david:123@192.168.15.11/amd'


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'estagio.base',
    'django_celery_beat',
    'django_celery_results',
    'mathfilters',
    # 'tornado_websockets',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

ROOT_URLCONF = 'estagio.urls'

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
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'estagio.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
    ('en-us', u'English'),
    #('pt-br', u'Português'),
)
	
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
    os.path.join(BASE_DIR,'estagio', 'locale'),
    os.path.join(BASE_DIR,'estagio','base', 'locale'),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
#
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR,'estagio','arquivos')
BASE_MEDIA_URL = '/media/raphael/DISK/Thiago/'
MEDIA_URL = os.path.join(BASE_MEDIA_URL,'testes/')
COMPACTA_URL = os.path.join(BASE_MEDIA_URL,'arquivos/')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    'base/static/',
]


# TORNADO = {
#     'port': 8080,
#     'handlers': [
#         (r'%s(.*)' % STATIC_URL, tornado.web.StaticFileHandler, {'path': STATICFILES_DIRS}),
#         tornado_websockets.django_app()
#     ],
#     'settings': {
#         'autoreload': True,
#         'debug': True
#     }
# }
#renomear arquivos para ingles
#find . -iname "*ale*" -exec rename 's/ale/ran/' '{}' \;

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@nuti.ic.ufmt.br'
EMAIL_USE_TLS   =   True
EMAIL_HOST  =   'smtp.gmail.com'
EMAIL_HOST_USER =   'no-reply@nuti.ic.ufmt.br'
EMAIL_HOST_PASSWORD =   '84a8188e3172807ff42d8803e41df927'
EMAIL_PORT  =   587

CONTACT_EMAIL = ''

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
