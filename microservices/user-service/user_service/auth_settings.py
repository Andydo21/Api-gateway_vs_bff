AUTH_USER_MODEL = 'api.User'

# Add to the existing settings.py content
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True
