from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Profile, Follow, Notification
from recipes.models import Recipe


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Аккаунт успешно создан!')
            return redirect('home')
    else:
        form = UserCreationForm()
    
    context = {'form': form}
    return render(request, 'users/register.html', context)


@login_required
def profile(request):
    user = request.user
    recipes = Recipe.objects.filter(author=user, is_published=True).order_by('-created_at')
    
    context = {
        'user': user,
        'recipes': recipes,
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Обновление данных пользователя
        email = request.POST.get('email', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        bio = request.POST.get('bio', '')
        profile_image = request.FILES.get('profile_image')
        
        user = request.user
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        # Обновление профиля
        profile = user.profile
        profile.bio = bio
        if profile_image:
            profile.profile_image = profile_image
        profile.save()
        
        messages.success(request, 'Профиль успешно обновлён!')
        return redirect('profile')
    
    context = {
        'user': request.user,
    }
    return render(request, 'users/edit_profile.html', context)


@login_required
def follow_user(request, username):
    """Подписаться на пользователя"""
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user == user_to_follow:
        messages.error(request, 'Вы не можете подписаться на самого себя!')
        return redirect('user-recipes', username=username)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if created:
        # Создаем уведомление о новой подписке
        Notification.create_follow_notification(request.user, user_to_follow)
        message = f'Вы подписались на {user_to_follow.username}'
    else:
        follow.delete()
        message = f'Вы отписались от {user_to_follow.username}'
    
    # Если это AJAX запрос
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'following': created,
            'followers_count': user_to_follow.profile.followers_count,
            'message': message
        })
    
    messages.success(request, message)
    return redirect('user-recipes', username=username)


@login_required
def following_list(request):
    """Список подписок пользователя"""
    following_list = Follow.objects.filter(follower=request.user).select_related('following')
    paginator = Paginator(following_list, 20)
    page_number = request.GET.get('page')
    following = paginator.get_page(page_number)
    
    context = {
        'following': following,
    }
    return render(request, 'users/following.html', context)


@login_required
def followers_list(request):
    """Список подписчиков пользователя"""
    followers_list = Follow.objects.filter(following=request.user).select_related('follower')
    paginator = Paginator(followers_list, 20)
    page_number = request.GET.get('page')
    followers = paginator.get_page(page_number)
    
    context = {
        'followers': followers,
    }
    return render(request, 'users/followers.html', context)


@login_required
def notifications(request):
    """Список уведомлений пользователя"""
    notifications_list = Notification.objects.filter(recipient=request.user)
    paginator = Paginator(notifications_list, 20)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    # Отмечаем все как прочитанные при просмотре
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'users/notifications.html', context)


@login_required
def notifications_count(request):
    """Количество непрочитанных уведомлений (для AJAX)"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def mark_notification_read(request, notification_id):
    """Отметить уведомление как прочитанное"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})


@login_required
def delete_notification(request, notification_id):
    """Удалить уведомление"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.delete()
    return JsonResponse({'success': True})
