import os

from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_to_market.settings')

application = get_wsgi_application()

def simple_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [b"Basic WSGI check passed!"]

# Temporarily set the application to our simple test app
# IMPORTANT: Remember to revert this after testing!
application = simple_app 