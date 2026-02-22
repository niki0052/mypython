from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit-profile'),
    path('follow/<str:username>/', views.follow_user, name='follow-user'),
    path('following/', views.following_list, name='following'),
    path('followers/', views.followers_list, name='followers'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/count/', views.notifications_count, name='notifications-count'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete-notification'),
]
