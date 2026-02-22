from django.contrib import admin
from .models import (Category, Tag, Recipe, Like, Favorite, Comment, 
                     Rating, RecipeStep, Cookbook, ShoppingList, ShoppingItem)


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 1
    ordering = ['step_number']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'difficulty', 'cooking_time', 'is_published', 'created_at']
    list_filter = ['category', 'difficulty', 'is_published', 'created_at']
    search_fields = ['title', 'description', 'ingredients']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [RecipeStepInline]
    raw_id_fields = ['author']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'author', 'category', 'tags', 'description', 'image')
        }),
        ('Содержание', {
            'fields': ('ingredients', 'instructions')
        }),
        ('Параметры', {
            'fields': ('cooking_time', 'difficulty', 'servings', 'is_published')
        }),
        ('Пищевая ценность', {
            'fields': ('calories', 'proteins', 'fats', 'carbohydrates'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'created_at']
    list_filter = ['created_at']
    raw_id_fields = ['user', 'recipe']
    date_hierarchy = 'created_at'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'created_at']
    list_filter = ['created_at']
    raw_id_fields = ['user', 'recipe']
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'content', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username', 'recipe__title']
    raw_id_fields = ['user', 'recipe', 'parent']
    date_hierarchy = 'created_at'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'score', 'created_at']
    list_filter = ['score', 'created_at']
    raw_id_fields = ['user', 'recipe']
    date_hierarchy = 'created_at'


@admin.register(RecipeStep)
class RecipeStepAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'step_number', 'title', 'duration']
    list_filter = ['recipe']
    ordering = ['recipe', 'step_number']


class ShoppingItemInline(admin.TabularInline):
    model = ShoppingItem
    extra = 1
    fields = ['name', 'quantity', 'is_checked', 'recipe']


@admin.register(Cookbook)
class CookbookAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_public', 'recipes_count', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    raw_id_fields = ['user']
    filter_horizontal = ['recipes']
    date_hierarchy = 'created_at'

    def recipes_count(self, obj):
        return obj.recipes.count()
    recipes_count.short_description = 'Количество рецептов'


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'items_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__username']
    raw_id_fields = ['user']
    inlines = [ShoppingItemInline]
    date_hierarchy = 'created_at'

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Количество элементов'


@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'shopping_list', 'is_checked', 'recipe', 'created_at']
    list_filter = ['is_checked', 'created_at']
    search_fields = ['name', 'shopping_list__name']
    raw_id_fields = ['shopping_list', 'recipe']
    date_hierarchy = 'created_at'
