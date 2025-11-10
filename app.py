"""
Small compatibility wrapper so platforms expecting a module named `app` with a WSGI
callable named `app` (for example Render with `gunicorn app:app`) can run this
Django project without changing the platform start command.

This file simply imports the WSGI application from `bossmail.wsgi` and exposes
it as the name `app`.
"""
import os

# Ensure the settings module is set when gunicorn imports this file.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bossmail.settings")

from bossmail.wsgi import application as app
