"""
Скрипт для заполнения базы данных тестовыми данными
Запустите: python populate_db.py
"""

import os
import sys
import django
from django.contrib.auth.models import User

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pre_recipe_blog.settings')
django.setup()

from recipes.models import Category, Recipe
from users.models import Profile


def create_test_data():
    print("Создание тестовых данных...")

    # Создаем суперпользователя если его нет
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("+ Создан суперпользователь: admin/admin123")

    # Создаем тестового пользователя
    if not User.objects.filter(username='testuser').exists():
        user = User.objects.create_user('testuser', 'user@example.com', 'test123')
        print("+ Создан тестовый пользователь: testuser/test123")

    # Создаем категории
    categories_data = [
        {'name': 'Breakfast', 'description': 'Morning recipes'},
        {'name': 'Lunch', 'description': 'Midday meals'},
        {'name': 'Dinner', 'description': 'Evening dishes'},
        {'name': 'Desserts', 'description': 'Sweet treats'},
        {'name': 'Vegetarian', 'description': 'Plant-based recipes'},
    ]

    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"+ Создана категория: {cat.name}")

    print("\nТестовые данные созданы успешно!")
    print("\nДоступные учетные записи:")
    print("1. Админ: admin / admin123")
    print("2. Пользователь: testuser / test123")


if __name__ == '__main__':
    create_test_data()