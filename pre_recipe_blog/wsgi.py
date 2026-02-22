"""
WSGI config for pre_recipe_blog project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pre_recipe_blog.settings')

application = get_wsgi_application()