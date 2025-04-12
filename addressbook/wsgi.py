import os
from django.core.wsgi import get_wsgi_application

# Set the default settings module for the 'wsgi' command-line utility
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'addressbook.settings')

# Get the WSGI application callable for use by any WSGI server
application = get_wsgi_application()
