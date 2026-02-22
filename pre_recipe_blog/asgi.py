"""
ASGI config for pre_recipe_blog project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pre_recipe_blog.settings')

application = get_asgi_application()