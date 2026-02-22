"""
Скрипт для добавления тестовых рецептов
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pre_recipe_blog.settings')
django.setup()

from django.contrib.auth.models import User
from recipes.models import Category, Recipe, Tag


def add_recipes():
    # Get or create categories
    breakfast, _ = Category.objects.get_or_create(
        name='Breakfast', 
        defaults={'description': 'Morning recipes', 'slug': 'breakfast'}
    )
    lunch, _ = Category.objects.get_or_create(
        name='Lunch', 
        defaults={'description': 'Midday meals', 'slug': 'lunch'}
    )
    dinner, _ = Category.objects.get_or_create(
        name='Dinner', 
        defaults={'description': 'Evening dishes', 'slug': 'dinner'}
    )
    desserts, _ = Category.objects.get_or_create(
        name='Desserts', 
        defaults={'description': 'Sweet treats', 'slug': 'desserts'}
    )
    vegetarian, _ = Category.objects.get_or_create(
        name='Vegetarian', 
        defaults={'description': 'Plant-based recipes', 'slug': 'vegetarian'}
    )

    # Get admin user
    admin = User.objects.get(username='admin')

    # Recipe data
    recipes_data = [
        {
            'title': 'Classic Pancakes',
            'category': breakfast,
            'difficulty': 'easy',
            'cooking_time': 20,
            'description': 'Fluffy American-style pancakes perfect for weekend breakfast',
            'ingredients': '2 cups flour\n1 tbsp sugar\n2 eggs\n1.5 cups milk\n2 tbsp melted butter\n1 tsp baking powder',
            'instructions': '1. Mix dry ingredients\n2. Add wet ingredients and stir\n3. Cook on hot griddle until golden\n4. Serve with maple syrup'
        },
        {
            'title': 'Caesar Salad',
            'category': lunch,
            'difficulty': 'easy',
            'cooking_time': 15,
            'description': 'Classic Caesar salad with homemade dressing',
            'ingredients': 'Romaine lettuce\nParmesan cheese\nCroutons\nOlive oil\nLemon juice\nGarlic\nAnchovy paste',
            'instructions': '1. Wash and chop lettuce\n2. Make dressing with olive oil, lemon, garlic\n3. Toss lettuce with dressing\n4. Top with parmesan and croutons'
        },
        {
            'title': 'Spaghetti Carbonara',
            'category': dinner,
            'difficulty': 'medium',
            'cooking_time': 30,
            'description': 'Authentic Italian pasta with creamy egg sauce',
            'ingredients': '400g spaghetti\n200g guanciale\n4 egg yolks\n100g pecorino cheese\nBlack pepper\nSalt',
            'instructions': '1. Cook pasta al dente\n2. Fry guanciale until crispy\n3. Mix egg yolks with cheese\n4. Combine hot pasta with egg mixture\n5. Add guanciale and pepper'
        },
        {
            'title': 'Chocolate Lava Cake',
            'category': desserts,
            'difficulty': 'hard',
            'cooking_time': 25,
            'description': 'Decadent chocolate cake with molten center',
            'ingredients': '200g dark chocolate\n100g butter\n2 eggs\n2 egg yolks\n50g sugar\n25g flour\nButter for ramekins',
            'instructions': '1. Melt chocolate and butter\n2. Whisk eggs with sugar\n3. Combine mixtures\n4. Add flour\n5. Pour into ramekins\n6. Bake at 200C for 12 minutes'
        },
        {
            'title': 'Vegetable Stir Fry',
            'category': vegetarian,
            'difficulty': 'easy',
            'cooking_time': 15,
            'description': 'Quick and healthy Asian-style vegetable dish',
            'ingredients': 'Broccoli\nBell peppers\nCarrots\nSoy sauce\nSesame oil\nGinger\nGarlic\nRice',
            'instructions': '1. Cut vegetables\n2. Heat wok with oil\n3. Stir fry vegetables\n4. Add sauce\n5. Serve over rice'
        },
        {
            'title': 'Grilled Cheese Sandwich',
            'category': lunch,
            'difficulty': 'easy',
            'cooking_time': 10,
            'description': 'Perfect crispy sandwich with melted cheese',
            'ingredients': '2 slices bread\nButter\nCheddar cheese\nMozzarella cheese',
            'instructions': '1. Butter bread slices\n2. Place cheese between slices\n3. Grill on medium heat\n4. Flip when golden\n5. Serve hot'
        },
    ]

    # Create tags
    tag_quick, _ = Tag.objects.get_or_create(name='quick')
    tag_popular, _ = Tag.objects.get_or_create(name='popular')
    tag_delicious, _ = Tag.objects.get_or_create(name='delicious')

    # Create recipes
    created_count = 0
    for data in recipes_data:
        slug = data['title'].lower().replace(' ', '-')
        recipe, created = Recipe.objects.get_or_create(
            slug=slug,
            defaults={
                'title': data['title'],
                'author': admin,
                'category': data['category'],
                'description': data['description'],
                'ingredients': data['ingredients'],
                'instructions': data['instructions'],
                'cooking_time': data['cooking_time'],
                'difficulty': data['difficulty'],
                'is_published': True
            }
        )
        if created:
            recipe.tags.add(tag_quick, tag_popular)
            created_count += 1
            print(f'Created: {recipe.title}')

    print(f'\nTotal recipes in database: {Recipe.objects.count()}')
    print(f'New recipes added: {created_count}')


if __name__ == '__main__':
    add_recipes()
