from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name_plural = "Categories"
        verbose_name = "Категория"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category-posts', kwargs={'slug': self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Легко'),
        ('medium', 'Средне'),
        ('hard', 'Сложно'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='Категория')
    tags = models.ManyToManyField('Tag', blank=True, verbose_name='Теги')
    description = models.TextField(verbose_name='Описание')
    ingredients = models.TextField(verbose_name='Ингредиенты')
    instructions = models.TextField(verbose_name='Инструкции')
    cooking_time = models.PositiveIntegerField(help_text="Время в минутах", verbose_name='Время приготовления')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, verbose_name='Сложность')
    image = models.ImageField(upload_to='recipe_images/', default='recipe_images/default.jpg', verbose_name='Изображение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    
    # Пищевая ценность
    calories = models.PositiveIntegerField(default=0, verbose_name='Калории (ккал)')
    proteins = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='Белки (г)')
    fats = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='Жиры (г)')
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='Углеводы (г)')
    servings = models.PositiveIntegerField(default=1, verbose_name='Количество порций')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def favorites_count(self):
        return self.favorites.count()

    @property
    def average_rating(self):
        """Средний рейтинг рецепта"""
        ratings = self.ratings.all()
        if ratings:
            return sum(r.score for r in ratings) / ratings.count()
        return 0

    @property
    def rating_count(self):
        """Количество оценок"""
        return self.ratings.count()

    @property
    def calories_per_serving(self):
        """Калории на порцию"""
        if self.servings > 0:
            return round(self.calories / self.servings)
        return self.calories


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='likes', verbose_name='Рецепт')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        unique_together = ['user', 'recipe']
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.title}'


class Favorite(models.Model):
    """Избранные рецепты пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorites', verbose_name='Рецепт')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        unique_together = ['user', 'recipe']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.title}'


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments', verbose_name='Рецепт')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    content = models.TextField(verbose_name='Содержание')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='Родительский комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}...'

    @property
    def is_reply(self):
        """Является ли комментарий ответом"""
        return self.parent is not None

    @property
    def replies_count(self):
        """Количество ответов на комментарий"""
        return self.replies.count()


class Rating(models.Model):
    """Рейтинг рецепта от 1 до 5 звезд"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings', verbose_name='Рецепт')
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата оценки')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        unique_together = ['user', 'recipe']
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'

    def __str__(self):
        return f'{self.user.username} оценил "{self.recipe.title}" на {self.score}/5'


class RecipeStep(models.Model):
    """Шаги приготовления рецепта"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps', verbose_name='Рецепт')
    step_number = models.PositiveIntegerField(verbose_name='Номер шага')
    title = models.CharField(max_length=200, blank=True, verbose_name='Заголовок шага')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='recipe_steps/', blank=True, null=True, verbose_name='Изображение')
    duration = models.PositiveIntegerField(default=0, help_text="Время в минутах", verbose_name='Время выполнения')

    class Meta:
        ordering = ['step_number']
        verbose_name = 'Шаг приготовления'
        verbose_name_plural = 'Шаги приготовления'

    def __str__(self):
        return f'Шаг {self.step_number}: {self.recipe.title}'


class Cookbook(models.Model):
    """Кулинарная книга - коллекция рецептов пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cookbooks', verbose_name='Пользователь')
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    recipes = models.ManyToManyField(Recipe, blank=True, related_name='cookbooks', verbose_name='Рецепты')
    is_public = models.BooleanField(default=True, verbose_name='Публичная')
    cover_image = models.ImageField(upload_to='cookbook_covers/', blank=True, null=True, verbose_name='Обложка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Кулинарная книга'
        verbose_name_plural = 'Кулинарные книги'

    def __str__(self):
        return f'{self.name} ({self.user.username})'

    @property
    def recipes_count(self):
        return self.recipes.count()


class ShoppingList(models.Model):
    """Список покупок пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_lists', verbose_name='Пользователь')
    name = models.CharField(max_length=100, default='Мой список покупок', verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.name} ({self.user.username})'

    @property
    def items_count(self):
        return self.items.count()

    @property
    def unchecked_count(self):
        return self.items.filter(is_checked=False).count()


class ShoppingItem(models.Model):
    """Элемент списка покупок"""
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='items', verbose_name='Список покупок')
    name = models.CharField(max_length=200, verbose_name='Название')
    quantity = models.CharField(max_length=50, blank=True, verbose_name='Количество')
    is_checked = models.BooleanField(default=False, verbose_name='Куплено')
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Из рецепта')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        ordering = ['is_checked', '-created_at']
        verbose_name = 'Элемент списка'
        verbose_name_plural = 'Элементы списка'

    def __str__(self):
        return f'{self.name} ({self.quantity})' if self.quantity else self.name
