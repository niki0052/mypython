#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pre_recipe_blog.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()



    # This file is used to run administrative tasks like running the development server, applying migrations, creating superusers, etc. It sets up the environment and calls Django's command-line utility.
    #https://github.com/niki0052/mypython.git