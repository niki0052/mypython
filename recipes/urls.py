from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home and basic views
    path('', views.home, name='home'),
    path('search/', views.search_recipes, name='search-recipes'),
    
    # Recipe CRUD
    path('recipe/new/', views.create_recipe, name='create-recipe'),
    path('recipe/<slug:slug>/', views.recipe_detail, name='recipe-detail'),
    path('recipe/<slug:slug>/update/', views.update_recipe, name='update-recipe'),
    path('recipe/<slug:slug>/delete/', views.delete_recipe, name='delete-recipe'),
    
    # Category
    path('category/<slug:slug>/', views.category_posts, name='category-posts'),
    
    # User recipes
    path('user/<str:username>/', views.user_recipes, name='user-recipes'),
    
    # Likes and Favorites
    path('recipe/<slug:slug>/like/', views.like_recipe, name='like-recipe'),
    path('recipe/<slug:slug>/favorite/', views.favorite_recipe, name='favorite-recipe'),
    path('favorites/', views.favorites_list, name='favorites'),
    
    # Comments
    path('recipe/<slug:slug>/comment/', views.add_comment, name='add-comment'),
    path('recipe/<slug:slug>/comment/<int:comment_id>/reply/', views.reply_comment, name='reply-comment'),
    path('recipe/<slug:slug>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete-comment'),
    
    # Ratings
    path('recipe/<slug:slug>/rate/', views.rate_recipe, name='rate-recipe'),
    
    # Cookbooks
    path('cookbooks/', views.cookbook_list, name='cookbook-list'),
    path('cookbooks/new/', views.cookbook_create, name='cookbook-create'),
    path('cookbooks/<int:cookbook_id>/', views.cookbook_detail, name='cookbook-detail'),
    path('cookbooks/<int:cookbook_id>/update/', views.cookbook_update, name='cookbook-update'),
    path('cookbooks/<int:cookbook_id>/delete/', views.cookbook_delete, name='cookbook-delete'),
    path('cookbooks/<int:cookbook_id>/add/<int:recipe_id>/', views.cookbook_add_recipe, name='cookbook-add-recipe'),
    path('cookbooks/<int:cookbook_id>/remove/<int:recipe_id>/', views.cookbook_remove_recipe, name='cookbook-remove-recipe'),
    
    # Shopping List
    path('shopping-list/', views.shopping_list, name='shopping-list'),
    path('shopping-list/clear/', views.clear_shopping_list, name='clear-shopping-list'),
    path('shopping-list/item/<int:item_id>/toggle/', views.toggle_shopping_item, name='toggle-shopping-item'),
    path('shopping-list/item/<int:item_id>/delete/', views.delete_shopping_item, name='delete-shopping-item'),
    path('recipe/<slug:slug>/add-to-shopping-list/', views.add_recipe_to_shopping_list, name='add-recipe-to-shopping-list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
