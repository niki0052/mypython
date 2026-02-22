from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Recipe, Category, Like, Comment, Tag, Favorite
from .forms import RecipeForm, CommentForm
from django.contrib.auth.models import User
from users.models import Follow, Notification


def home(request):
    recipes_list = Recipe.objects.filter(is_published=True).order_by('-created_at')
    paginator = Paginator(recipes_list, 6)
    page_number = request.GET.get('page')
    recipes = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    featured = Recipe.objects.filter(is_published=True).order_by('-created_at')[:3]

    context = {
        'recipes': recipes,
        'categories': categories,
        'featured_recipes': featured,
    }
    return render(request, 'recipes/home.html', context)


def recipe_detail(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)
    comments = recipe.comments.all()

    # Проверяем, лайкнул ли текущий пользователь рецепт
    user_liked = False
    user_favorited = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, recipe=recipe).exists()
        user_favorited = Favorite.objects.filter(user=request.user, recipe=recipe).exists()

    # Рекомендации (рецепты из той же категории)
    recommended = Recipe.objects.filter(
        category=recipe.category,
        is_published=True
    ).exclude(id=recipe.id)[:4]

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.recipe = recipe
            comment.user = request.user
            comment.save()
            # Создаем уведомление о комментарии
            Notification.create_comment_notification(request.user, recipe, comment)
            messages.success(request, 'Комментарий успешно добавлен!')
            return redirect('recipe-detail', slug=recipe.slug)
    else:
        comment_form = CommentForm()

    context = {
        'recipe': recipe,
        'comments': comments,
        'comment_form': comment_form,
        'user_liked': user_liked,
        'user_favorited': user_favorited,
        'recommended': recommended,
    }
    return render(request, 'recipes/recipe_detail.html', context)


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    recipes_list = Recipe.objects.filter(category=category, is_published=True).order_by('-created_at')
    paginator = Paginator(recipes_list, 6)
    page_number = request.GET.get('page')
    recipes = paginator.get_page(page_number)
    categories = Category.objects.all()

    context = {
        'category': category,
        'recipes': recipes,
        'categories': categories,
    }
    return render(request, 'recipes/category_posts.html', context)


@login_required
def create_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            
            # Сохранение тегов
            tags_str = form.cleaned_data.get('tags', '')
            if tags_str:
                tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name.lower())
                    recipe.tags.add(tag)
            
            # Создаем уведомления для подписчиков
            Notification.create_recipe_notification(recipe)
            
            messages.success(request, 'Рецепт успешно создан!')
            return redirect('recipe-detail', slug=recipe.slug)
    else:
        form = RecipeForm()

    context = {'form': form}
    return render(request, 'recipes/recipe_form.html', context)


@login_required
def update_recipe(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)

    # Проверяем, что пользователь - автор рецепта
    if recipe.author != request.user:
        messages.error(request, 'Вы можете редактировать только свои рецепты!')
        return redirect('recipe-detail', slug=slug)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            recipe = form.save(commit=False)
            
            # Обновление тегов
            recipe.tags.clear()
            tags_str = form.cleaned_data.get('tags', '')
            if tags_str:
                tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name.lower())
                    recipe.tags.add(tag)
            
            recipe.save()
            messages.success(request, 'Рецепт успешно обновлён!')
            return redirect('recipe-detail', slug=recipe.slug)
    else:
        # Преобразуем существующие теги в строку для формы
        tags_str = ', '.join([tag.name for tag in recipe.tags.all()])
        form = RecipeForm(instance=recipe, initial={'tags': tags_str})

    context = {'form': form}
    return render(request, 'recipes/recipe_form.html', context)


@login_required
def delete_recipe(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)

    if recipe.author != request.user:
        messages.error(request, 'Вы можете удалять только свои рецепты!')
        return redirect('recipe-detail', slug=slug)

    if request.method == 'POST':
        recipe.delete()
        messages.success(request, 'Рецепт успешно удалён!')
        return redirect('home')

    context = {'recipe': recipe}
    return render(request, 'recipes/recipe_confirm_delete.html', context)


@login_required
def like_recipe(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)

    # Проверяем, есть ли уже лайк от пользователя
    like, created = Like.objects.get_or_create(user=request.user, recipe=recipe)

    if not created:
        # Если лайк уже был, удаляем его (переключение)
        like.delete()
    else:
        # Создаем уведомление о лайке
        Notification.create_like_notification(request.user, recipe)

    # Если это AJAX запрос, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': created,
            'count': recipe.likes.count()
        })

    return redirect('recipe-detail', slug=slug)


@login_required
def favorite_recipe(request, slug):
    """Добавить/удалить рецепт из избранного"""
    recipe = get_object_or_404(Recipe, slug=slug)
    
    favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
    
    if not created:
        favorite.delete()
        message = 'Рецепт удалён из избранного'
    else:
        message = 'Рецепт добавлен в избранное'
    
    # Если это AJAX запрос, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'favorited': created,
            'count': recipe.favorites.count(),
            'message': message
        })
    
    messages.success(request, message)
    return redirect('recipe-detail', slug=slug)


@login_required
def favorites_list(request):
    """Список избранных рецептов пользователя"""
    favorites_list = Favorite.objects.filter(user=request.user).select_related('recipe')
    paginator = Paginator(favorites_list, 9)
    page_number = request.GET.get('page')
    favorites = paginator.get_page(page_number)
    
    context = {
        'favorites': favorites,
    }
    return render(request, 'recipes/favorites.html', context)


@login_required
def add_comment(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.user = request.user
            comment.save()
            # Создаем уведомление о комментарии
            Notification.create_comment_notification(request.user, recipe, comment)
            messages.success(request, 'Комментарий успешно добавлен!')

    return redirect('recipe-detail', slug=slug)


def search_recipes(request):
    query = request.GET.get('q', '')
    recipes_list = Recipe.objects.filter(is_published=True)

    if query:
        recipes_list = recipes_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    paginator = Paginator(recipes_list, 6)
    page_number = request.GET.get('page')
    recipes = paginator.get_page(page_number)

    context = {
        'recipes': recipes,
        'query': query,
    }
    return render(request, 'recipes/search_results.html', context)


def user_recipes(request, username):
    user = get_object_or_404(User, username=username)
    recipes_list = Recipe.objects.filter(author=user, is_published=True).order_by('-created_at')
    paginator = Paginator(recipes_list, 6)
    page_number = request.GET.get('page')
    recipes = paginator.get_page(page_number)
    
    # Проверяем, подписан ли текущий пользователь на этого автора
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    context = {
        'profile_user': user,
        'recipes': recipes,
        'is_following': is_following,
    }
    return render(request, 'recipes/user_recipes.html', context)
