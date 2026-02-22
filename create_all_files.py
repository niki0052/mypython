import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

files_to_create = {

    'manage.py': '''#!/usr/bin/env python
import os
import sys

def main():
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
''',

    'requirements.txt': '''Django==5.0
Pillow==10.0.0
django-crispy-forms==2.0
crispy-bootstrap5==0.7
django-ckeditor==6.7.0
python-decouple==3.8
''',

    '.env': '''SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
''',



    #pre_recipeblog
    'pre_recipe_blog/__init__.py': '',
    'pre_recipe_blog/wsgi.py': '''import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pre_recipe_blog.settings')
application = get_wsgi_application()
''',
    'pre_recipe_blog/asgi.py': '''import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pre_recipe_blog.settings')
application = get_asgi_application()
''',




    #apps recipes
    'recipes/__init__.py': '',
    'recipes/apps.py': '''from django.apps import AppConfig

class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
''',






    'users/__init__.py': '',
    'users/apps.py': '''from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals
''',

    # Static fi
    'static/css/style.css': '''/* Custom CSS for Pre Recipe Blog */
body {
    font-family: Arial, sans-serif;
}
''',
    'static/js/script.js': '''// Custom JavaScript for Pre Recipe Blog
console.log('Pre Recipe Blog loaded');
''',
}


def create_files():
    print("Создание файлов проекта...")

    for filepath, content in files_to_create.items():
        full_path = BASE_DIR / filepath

        full_path.parent.mkdir(parents=True, exist_ok=True)
#3e pazobrati
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f" Создан: {filepath}")

    print("\nВсе файлы созданы успешно!")
    print("\nВыполните следующие команды:")
    print("1. pip install -r requirements.txt")
    print("2. python manage.py makemigrations")
    print("3. python manage.py migrate")
    print("4. python manage.py createsuperuser")
    print("5. python manage.py runserver")


if __name__ == '__main__':
    create_files()