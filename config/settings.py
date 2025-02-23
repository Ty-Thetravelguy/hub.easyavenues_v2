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
    'users.apps.UsersConfig',

    # Allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",

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

    # Social providers (Ensure 'microsoft' is listed if you are using it)
    "allauth.socialaccount.providers.microsoft",
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

SOCIALACCOUNT_PROVIDERS = {
    'microsoft': {
        'APP': {
            'client_id': 'YOUR_CLIENT_ID',
            'secret': 'YOUR_CLIENT_SECRET',
            'key': ''
        },
        'SCOPE': [
            'email',
            'profile',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

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

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # Default Django authentication
    "allauth.account.auth_backends.AuthenticationBackend",  # Allauth authentication
]

SITE_ID = 1

# URL Redirects
LOGIN_URL = '/'
LOGOUT_URL = '/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Options: 'none', 'optional', 'mandatory'
ACCOUNT_SIGNUP_REDIRECT_URL = '/dashboard/'  # Redirect after signup
ACCOUNT_LOGOUT_REDIRECT_URL = '/'  # Redirect after logout


ACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomSignupForm',
}

# Add this to your existing settings
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'

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
            'level': 'DEBUG',
            'propagate': False,
        },
        'users': {  # Add this section for the users app
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    },
}