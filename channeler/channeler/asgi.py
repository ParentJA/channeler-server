# Standard library imports.
import os

# Django imports.
import django

# Third-party imports.
from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'channeler.settings')

django.setup()

application = get_default_application()
