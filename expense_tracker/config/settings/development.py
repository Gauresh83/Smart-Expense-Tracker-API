from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

# Use local file storage in development
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Override email backend for dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
