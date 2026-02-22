from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import (Recipe, Category, Like, Comment, Tag, Favorite, 
                     Rating, RecipeStep, Cookbook, ShoppingList, ShoppingItem)
from .forms import (RecipeForm, CommentForm, ReplyForm, RatingForm, 
                    RecipeStepFormSet, CookbookForm, ShoppingItemForm,
                    AddRecipeToShoppingListForm)
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
    comments = recipe.comments.filter(parent__isnull=True)  # Только корневые комментарии
    steps = recipe.steps.all()

    # Проверяем, лайкнул ли текущий пользователь рецепт
    user_liked = False
    user_favorited = False
    user_rating = None
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, recipe=recipe).exists()
        user_favorited = Favorite.objects.filter(user=request.user, recipe=recipe).exists()
        user_rating = Rating.objects.filter(user=request.user, recipe=recipe).first()

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
            # Проверяем, является ли это ответом на комментарий
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    # Проверяем, что родительский комментарий принадлежит этому рецепту
                    parent_comment = Comment.objects.get(id=parent_id, recipe=recipe)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass
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
        'user_rating': user_rating,
        'recommended': recommended,
        'steps': steps,
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
        formset = RecipeStepFormSet(request.POST, request.FILES)
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
            
            # Сохранение шагов
            if formset.is_valid():
                formset.instance = recipe
                formset.save()
            
            # Создаем уведомления для подписчиков
            Notification.create_recipe_notification(recipe)
            
            messages.success(request, 'Рецепт успешно создан!')
            return redirect('recipe-detail', slug=recipe.slug)
    else:
        form = RecipeForm()
        formset = RecipeStepFormSet()

    context = {'form': form, 'formset': formset}
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
        formset = RecipeStepFormSet(request.POST, request.FILES, instance=recipe)
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
            
            # Сохранение шагов
            if formset.is_valid():
                formset.save()
            
            messages.success(request, 'Рецепт успешно обновлён!')
            return redirect('recipe-detail', slug=recipe.slug)
    else:
        # Преобразуем существующие теги в строку для формы
        tags_str = ', '.join([tag.name for tag in recipe.tags.all()])
        form = RecipeForm(instance=recipe, initial={'tags': tags_str})
        formset = RecipeStepFormSet(instance=recipe)

    context = {'form': form, 'formset': formset}
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
def rate_recipe(request, slug):
    """Оценить рецепт"""
    recipe = get_object_or_404(Recipe, slug=slug)
    
    if request.method == 'POST':
        score = request.POST.get('score')
        if score and score.isdigit():
            score = int(score)
            if 1 <= score <= 5:
                rating, created = Rating.objects.update_or_create(
                    user=request.user,
                    recipe=recipe,
                    defaults={'score': score}
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'score': score,
                        'average': recipe.average_rating,
                        'count': recipe.rating_count
                    })
                
                messages.success(request, f'Вы оценили рецепт на {score} звёзд!')
    
    return redirect('recipe-detail', slug=slug)


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


@login_required
def reply_comment(request, slug, comment_id):
    """Ответить на комментарий"""
    recipe = get_object_or_404(Recipe, slug=slug)
    parent_comment = get_object_or_404(Comment, id=comment_id, recipe=recipe)
    
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.recipe = recipe
            reply.user = request.user
            reply.parent = parent_comment
            reply.save()
            messages.success(request, 'Ответ добавлен!')
    
    return redirect('recipe-detail', slug=slug)


@login_required
def delete_comment(request, slug, comment_id):
    """Удалить комментарий"""
    recipe = get_object_or_404(Recipe, slug=slug)
    comment = get_object_or_404(Comment, id=comment_id, recipe=recipe)
    
    if comment.user == request.user:
        comment.delete()
        messages.success(request, 'Комментарий удалён!')
    else:
        messages.error(request, 'Вы можете удалять только свои комментарии!')
    
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


# ==================== COOKBOOK VIEWS ====================

@login_required
def cookbook_list(request):
    """Список кулинарных книг пользователя"""
    cookbooks = Cookbook.objects.filter(user=request.user)
    public_cookbooks = Cookbook.objects.filter(is_public=True).exclude(user=request.user)[:6]
    
    context = {
        'cookbooks': cookbooks,
        'public_cookbooks': public_cookbooks,
    }
    return render(request, 'recipes/cookbook_list.html', context)


@login_required
def cookbook_create(request):
    """Создать кулинарную книгу"""
    if request.method == 'POST':
        form = CookbookForm(request.POST, request.FILES)
        if form.is_valid():
            cookbook = form.save(commit=False)
            cookbook.user = request.user
            cookbook.save()
            messages.success(request, 'Кулинарная книга создана!')
            return redirect('cookbook-detail', cookbook_id=cookbook.id)
    else:
        form = CookbookForm()
    
    context = {'form': form}
    return render(request, 'recipes/cookbook_form.html', context)


@login_required
def cookbook_detail(request, cookbook_id):
    """Детали кулинарной книги"""
    cookbook = get_object_or_404(Cookbook, id=cookbook_id)
    
    # Проверяем доступ
    if cookbook.user != request.user and not cookbook.is_public:
        messages.error(request, 'Эта кулинарная книга приватная!')
        return redirect('cookbook-list')
    
    recipes = cookbook.recipes.all()
    
    context = {
        'cookbook': cookbook,
        'recipes': recipes,
    }
    return render(request, 'recipes/cookbook_detail.html', context)


@login_required
def cookbook_update(request, cookbook_id):
    """Редактировать кулинарную книгу"""
    cookbook = get_object_or_404(Cookbook, id=cookbook_id)
    
    if cookbook.user != request.user:
        messages.error(request, 'Вы можете редактировать только свои книги!')
        return redirect('cookbook-detail', cookbook_id=cookbook.id)
    
    if request.method == 'POST':
        form = CookbookForm(request.POST, request.FILES, instance=cookbook)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга обновлена!')
            return redirect('cookbook-detail', cookbook_id=cookbook.id)
    else:
        form = CookbookForm(instance=cookbook)
    
    context = {'form': form, 'cookbook': cookbook}
    return render(request, 'recipes/cookbook_form.html', context)


@login_required
def cookbook_delete(request, cookbook_id):
    """Удалить кулинарную книгу"""
    cookbook = get_object_or_404(Cookbook, id=cookbook_id)
    
    if cookbook.user != request.user:
        messages.error(request, 'Вы можете удалять только свои книги!')
        return redirect('cookbook-list')
    
    if request.method == 'POST':
        cookbook.delete()
        messages.success(request, 'Книга удалена!')
        return redirect('cookbook-list')
    
    context = {'cookbook': cookbook}
    return render(request, 'recipes/cookbook_confirm_delete.html', context)


@login_required
def cookbook_add_recipe(request, cookbook_id, recipe_id):
    """Добавить рецепт в кулинарную книгу"""
    cookbook = get_object_or_404(Cookbook, id=cookbook_id, user=request.user)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    cookbook.recipes.add(recipe)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Рецепт добавлен в книгу!'})
    
    messages.success(request, f'Рецепт "{recipe.title}" добавлен в книгу "{cookbook.name}"!')
    return redirect('cookbook-detail', cookbook_id=cookbook.id)


@login_required
def cookbook_remove_recipe(request, cookbook_id, recipe_id):
    """Удалить рецепт из кулинарной книги"""
    cookbook = get_object_or_404(Cookbook, id=cookbook_id, user=request.user)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    cookbook.recipes.remove(recipe)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Рецепт удалён из книги!'})
    
    messages.success(request, f'Рецепт "{recipe.title}" удалён из книги!')
    return redirect('cookbook-detail', cookbook_id=cookbook.id)


# ==================== SHOPPING LIST VIEWS ====================

@login_required
def shopping_list(request):
    """Список покупок пользователя"""
    shopping_list, created = ShoppingList.objects.get_or_create(
        user=request.user,
        defaults={'name': 'Мой список покупок'}
    )
    
    items = shopping_list.items.all()
    
    if request.method == 'POST':
        form = ShoppingItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.shopping_list = shopping_list
            item.save()
            messages.success(request, 'Элемент добавлен!')
            return redirect('shopping-list')
    else:
        form = ShoppingItemForm()
    
    context = {
        'shopping_list': shopping_list,
        'items': items,
        'form': form,
    }
    return render(request, 'recipes/shopping_list.html', context)


@login_required
def add_recipe_to_shopping_list(request, slug):
    """Добавить ингредиенты рецепта в список покупок"""
    recipe = get_object_or_404(Recipe, slug=slug)
    shopping_list, created = ShoppingList.objects.get_or_create(
        user=request.user,
        defaults={'name': 'Мой список покупок'}
    )
    
    if request.method == 'POST':
        form = AddRecipeToShoppingListForm(request.POST, recipe=recipe)
        if form.is_valid():
            selected_indices = form.cleaned_data.get('ingredients', [])
            ingredient_lines = [line.strip() for line in recipe.ingredients.split('\n') if line.strip()]
            
            for idx in selected_indices:
                idx = int(idx)
                if 0 <= idx < len(ingredient_lines):
                    ShoppingItem.objects.create(
                        shopping_list=shopping_list,
                        name=ingredient_lines[idx],
                        recipe=recipe
                    )
            
            messages.success(request, f'Ингредиенты добавлены в список покупок!')
            return redirect('shopping-list')
    else:
        form = AddRecipeToShoppingListForm(recipe=recipe)
    
    context = {
        'form': form,
        'recipe': recipe,
    }
    return render(request, 'recipes/add_to_shopping_list.html', context)


@login_required
def toggle_shopping_item(request, item_id):
    """Отметить/снять отметку с элемента списка"""
    item = get_object_or_404(ShoppingItem, id=item_id, shopping_list__user=request.user)
    item.is_checked = not item.is_checked
    item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_checked': item.is_checked
        })
    
    return redirect('shopping-list')


@login_required
def delete_shopping_item(request, item_id):
    """Удалить элемент из списка"""
    item = get_object_or_404(ShoppingItem, id=item_id, shopping_list__user=request.user)
    item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Элемент удалён!')
    return redirect('shopping-list')


@login_required
def clear_shopping_list(request):
    """Очистить список покупок"""
    shopping_list = get_object_or_404(ShoppingList, user=request.user)
    shopping_list.items.all().delete()
    
    messages.success(request, 'Список покупок очищен!')
    return redirect('shopping-list')
