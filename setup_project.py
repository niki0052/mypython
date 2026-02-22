
"""
Скрипт для автоматической настройки проекта pre_recipe_blog
Запустите: python setup_project.py
"""
#доделать теги!!
import os
import sys
import subprocess
from pathlib import Path


def create_file(filepath, content):
    """Создает файл с указанным содержимым."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Создан: {filepath}")
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка при создании {filepath}: {e}")
        return False


def run_command(command, description):
    """Выполняет команду в терминале."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] {description} успешно")
            return True
        else:
            print(f"[ERROR] Ошибка: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        return False


def main():
    print("=" * 60)
    print("НАСТРОЙКА ПРОЕКТА PRE_RECIPE_BLOG")
    print("=" * 60)

    #структуру папок
    folders = [
        'static/css',
        'static/js',
        'static/images',
        'media/recipe_images',
        'media/profile_images',
        'templates/recipes',
        'templates/users',
        'templates/registration',
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"[OK] Создана папка: {folder}")

    #requirements.txt
    requirements = """Django==5.0
Pillow==10.0.0
django-crispy-forms==2.0
crispy-bootstrap5==0.7
django-ckeditor==6.7.0
python-decouple==3.8
"""
    create_file('requirements.txt', requirements)

    #env файл
    env_content = """SECRET_KEY=django-insecure-your-secret-key-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
"""
    create_file('.env', env_content)

    #.gitignore
    gitignore = """# Django
*.log
*.pot
*.pyc
__pycache__/
local_settings.py
db.sqlite3
db.sqlite3-journal
media/

# Virtual environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Static files
staticfiles/
"""
    create_file('.gitignore', gitignore)

    #файлы для static
    create_file('static/css/style.css', '/* Custom CSS for Pre Recipe Blog */\n')
    create_file('static/js/script.js', '// Custom JavaScript for Pre Recipe Blog\n')

    print("\n" + "=" * 60)
    print("СТРУКТУРА ПРОЕКТА СОЗДАНА!")
    print("=" * 60)

    #Предлагаем установить зависимости
    install = input("\nУстановить зависимости? (y/n): ").lower()
    if install == 'y':
        run_command('pip install -r requirements.txt', 'Установка зависимостей')

    #Предлагаем выполнить миграции
    migrate = input("\nВыполнить миграции? (y/n): ").lower()
    if migrate == 'y':
        run_command('python manage.py makemigrations', 'Создание миграций')
        run_command('python manage.py migrate', 'Применение миграций')

    #Предлагаем создать суперпользователя
    superuser = input("\nСоздать суперпользователя? (y/n): ").lower()
    if superuser == 'y':
        run_command('python manage.py createsuperuser', 'Создание суперпользователя')

    print("\n" + "=" * 60)
    print("СЛЕДУЮЩИЕ ШАГИ:")
    print("=" * 60)
    print("1. Запустите сервер: python manage.py runserver")
    print("2. Откройте браузер: http://127.0.0.1:8000")
    print("3. Админка: http://127.0.0.1:8000/admin")
    print("=" * 60)


if __name__ == '__main__':
    main()