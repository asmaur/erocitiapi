"""
Django settings for eroapi project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from decouple import config, Csv
from celery.schedules import crontab
from kombu import Queue
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

#ALLOWED_HOSTS = []
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]


LOCAL_APPS = ['apps.eros', 'apps.account', 'apps.api', 'apps.assina', 'apps.citiapi']


THIRD_PARTY_APPS = ['rest_framework', 'rest_framework.authtoken', 'imagekit', 'corsheaders', 'pagseguro', 'django_cleanup.apps.CleanupConfig']

INSTALLED_APPS = INSTALLED_APPS + LOCAL_APPS + THIRD_PARTY_APPS

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # <-- And here
        #'rest_framework.permissions.IsAuthenticated',
    ],
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eroapi.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

WSGI_APPLICATION = 'eroapi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DEPLOY = config('DEPLOY', cast=bool)

if DEPLOY:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': '',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
#DATA_UPLOAD_MAX_MEMORY_SIZE = 100000*1027

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'eroapi', 'static'),
)
SITE_ID = 1

WATERMARK_IMAGE = os.path.join(BASE_DIR, 'static/img/Coat_of_arms_of_Ireland.png')
DEFAULT_FONT = os.path.join(BASE_DIR, 'static/fonts/OpenSans-Italic.ttf')

CORS_ORIGIN_ALLOW_ALL = config('CORS_ORIGIN_ALLOW_ALL', cast=bool) #False pra ir ao servidor

CORS_ORIGIN_WHITELIST =config('CORS_ORIGIN_WHITELIST', cast=Csv())

#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True


EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
#EMAIL_FILE_PATH = PROJECT_DIR.parent.child('maildumps')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')


PAGSEGURO_EMAIL = config('PAGSEGURO_EMAIL')
PAGSEGURO_SANDBOX = config('PAGSEGURO_SANDBOX', cast=bool)
PAGSEGURO_LOG_IN_MODEL = config('PAGSEGURO_LOG_IN_MODEL', cast=bool)

CITIPROD = config('CITIPROD', cast=bool)

if CITIPROD:
    PAGSEGURO_TOKEN = config('PAGSEGURO_TOKEN_PROD')
    PAGSEGURO_TRANSACTIONS_URL = config('BASE_PAGSEGURO_TRANSACTIONS_URL')
else:
    PAGSEGURO_TOKEN = config('PAGSEGURO_TOKEN')
    PAGSEGURO_TRANSACTIONS_URL =config('BASE_PAGSEGURO_TRANSACTIONS_URL_SANDBOX')



CONTACT_FROM_EMAIL=config('CONTACT_FROM_EMAIL')
SUPPORT_FROM_EMAIL=config('SUPPORT_FROM_EMAIL')
NOREPLY_FROM_EMAIL=config('NOREPLY_FROM_EMAIL')
REPORT_FROM_EMAIL=config('REPORT_FROM_EMAIL')

#MAILCHIMP
MAILCHIMP_API_KEY=config('MAILCHIMP_API_KEY')
MAILCHIMP_DATA_CENTER=config('MAILCHIMP_DATA_CENTER')
MAILCHIMP_LIST_ID=config('MAILCHIMP_LIST_ID')



#celery config

CELERY_TIMEZONE = TIME_ZONE
CELERY_ACCEPT_CONTENT = ['json', 'pickle']
CELERYD_CONCURRENCY = 2
CELERYD_MAX_TASKS_PER_CHILD = 4
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_BROKER_URL = 'amqp://localhost'

# celery queues setup
"""
CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('feeds', Exchange('feeds'), routing_key='long_tasks'),
)
"""

CELERY_CREATE_MISSING_QUEUES=True

CELERY_ROUTES = {
    'apps.api.v1.tasks.esqueci_senha_task': {
        'queue': 'esqueci-senha',
        'routing_key': 'esqueci_senha',
    },
    'apps.api.v1.tasks.vencimento_de_plano_task': {
        'queue': 'noty-vencimento',
        'routing_key': 'noty_vencimento',
    },
    'apps.api.v1.tasks.add_ads_mailchimp_task': {
        'queue': 'ads-mailchimp',
        'routing_key': 'ads_mailchimp',
    },
    'apps.citiapi.v1.tasks.add_citi_mailchimp_task': {
        'queue': 'citi-mailchimp',
        'routing_key': 'citi_mailchimp',
    },
    'apps.citiapi.v1.tasks.sem_subscrition_task': {
        'queue': 'sem-subscrition',
        'routing_key': 'sem_subscrition',
    },
    'apps.citiapi.v1.tasks.sem_perfil_task': {
        'queue': 'sem-perfil',
        'routing_key': 'sem_perfil',
    },
    #'apps.api.v1.tasks.credito_acabando_task': {
     #   'queue': 'credito-acabando',
      #  'routing_key': 'credito_acabando',
    #},
}


if CITIPROD:

    CELERY_BEAT_SCHEDULE = {
        'vencimento-task': {
            'task': 'apps.api.v1.tasks.vencimento_de_plano_task',
            'schedule': crontab(minute=0, hour='11'),

        },
        'sem-perfil-task': {
            'task': 'apps.api.v1.tasks.sem_perfil_task',
            'schedule': crontab(minute=0, hour=17,day_of_week=1),

        },
        'sem-subscription-task': {
            'task': 'apps.api.v1.tasks.sem_subscrition_task',
            'schedule': crontab(minute=0, hour=18,day_of_week=1),

        },
        'remove-unactive-subscription-task': {
            'task': 'apps.api.v1.tasks.remove_unactive_subscription',
            'schedule': crontab(minute=0, hour=0),

        },
        # 'credito-acabando-task': {
        #   'task': 'apps.api.v1.tasks.credito_acabando_task',
        #  'schedule': crontab(minute=0, hour=9),

        # },
    }
else:
    CELERY_BEAT_SCHEDULE = {

       'vencimento-task': {
            'task': 'apps.api.v1.tasks.vencimento_de_plano_task',
           'schedule': crontab(minute=0, hour='15'),

       },
       'sem-perfil-task': {
           'task': 'apps.api.v1.tasks.sem_perfil_task',
           'schedule': crontab(minute=0, hour=18, day_of_week="3"),

        },
        'sem-subscription-task': {
            'task': 'apps.api.v1.tasks.sem_subscrition_task',
           'schedule': crontab(minute=0, hour=18, day_of_week="3"),

        },
        'remove-unactive-subscription-task': {
            'task': 'apps.api.v1.tasks.remove_unactive_subscription',
           'schedule': crontab(minute="*/1"),

        },
        #'credito-acabando-task': {
         #   'task': 'apps.api.v1.tasks.credito_acabando_task',
          #  'schedule': crontab(minute="*/1"),

        #},

    }