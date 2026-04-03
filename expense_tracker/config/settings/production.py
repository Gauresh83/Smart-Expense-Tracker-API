from .base import *
import sentry_sdk
from decouple import config

DEBUG = False
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")

# ── Security ──────────────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="").split(",")

# ── Storage ───────────────────────────────────────────────────────────────────
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"

# ── Sentry ────────────────────────────────────────────────────────────────────
sentry_sdk.init(
    dsn=config("SENTRY_DSN", default=""),
    traces_sample_rate=0.2,
    profiles_sample_rate=0.1,
)
