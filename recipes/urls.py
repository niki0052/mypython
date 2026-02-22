from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('recipe/<slug:slug>/', views.recipe_detail, name='recipe-detail'),
    path('recipe/new/', views.create_recipe, name='create-recipe'),
    path('recipe/<slug:slug>/update/', views.update_recipe, name='update-recipe'),
    path('recipe/<slug:slug>/delete/', views.delete_recipe, name='delete-recipe'),
    path('category/<slug:slug>/', views.category_posts, name='category-posts'),
    path('recipe/<slug:slug>/like/', views.like_recipe, name='like-recipe'),
    path('recipe/<slug:slug>/favorite/', views.favorite_recipe, name='favorite-recipe'),
    path('recipe/<slug:slug>/comment/', views.add_comment, name='add-comment'),
    path('search/', views.search_recipes, name='search-recipes'),
    path('user/<str:username>/', views.user_recipes, name='user-recipes'),
    path('favorites/', views.favorites_list, name='favorites'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
