from pathlib import Path
from dotenv import load_dotenv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

# Then use environment variables like:
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'

# Amadeus API Credentials
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")
AMADEUS_OFFICE_ID = os.getenv("AMADEUS_OFFICE_ID")

# SECURITY WARNING: don't run with debug turned on in production!

# Update this line
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Or for extra safety, add list comprehension to remove any empty strings:
ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "").split(",") if host.strip()]
ALLOWED_DOMAINS = os.getenv("ALLOWED_DOMAINS", "").split(",")

# Application definition

INSTALLED_APPS = [
    'accounts.apps.AccountsConfig', 
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'users.apps.UsersConfig',
    'formtools',

    # Allauth
    "allauth",
    "allauth.account",
    # "allauth.socialaccount",  # Commented out to disable social login

    # Editor
    'tinymce',

    # local apps
    'dashboard',
    'agent_support',
    'crm',
    'finance',
    'office',
    'external_links',
    'query_log',
    'itineraries',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Add this for Allauth
    "allauth.account.middleware.AccountMiddleware",

    # Recently Viewed
    'users.middleware.RecentlyViewedMiddleware',
]

TINYMCE_DEFAULT_CONFIG = {
    'height': 200,
    'menubar': False,
    'plugins': 'lists link autolink',
    'toolbar': 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | bullist numlist | link',
    'content_style': 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; }',
}

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'users.context_processors.recently_viewed',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django AllAuth Configuration
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Easy Avenues] '
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
ACCOUNT_RATE_LIMITS = {
    "login": "5/5m",  # 5 attempts per 5 minutes for login
    "login_failed": "5/5m",  # 5 attempts per 5 minutes for failed logins
    "signup": "5/5m",  # 5 attempts per 5 minutes for signup
    "send_mail": "5/5m",  # 5 attempts per 5 minutes for sending emails
}
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True

# Add this to ensure the site framework works correctly
SITE_ID = 1

# URL Redirects
LOGIN_URL = '/'
LOGOUT_URL = '/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

ACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomSignupForm',
}

ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Add this line

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files (Uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # Default Django authentication
    "allauth.account.auth_backends.AuthenticationBackend",  # Allauth authentication
]

# Disable social login providers
SOCIALACCOUNT_PROVIDERS = {}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'users': {  # Add this section for the users app
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        }
    },
}

# HubSpot API Configuration
HUBSPOT_API_KEY = os.environ.get('HUBSPOT_API_KEY', '')  # Get from environment variable