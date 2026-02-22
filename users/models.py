from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    bio = models.TextField(max_length=500, blank=True, verbose_name='Биография')
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.jpg', verbose_name='Фото профиля')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль {self.user.username}'

    @property
    def followers_count(self):
        return self.user.followers.count()

    @property
    def following_count(self):
        return self.user.following.count()


class Follow(models.Model):
    """Подписка на пользователей"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following', verbose_name='Подписчик')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers', verbose_name='Подписан на')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')

    class Meta:
        unique_together = ['follower', 'following']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.follower.username} -> {self.following.username}'

    def save(self, *args, **kwargs):
        if self.follower == self.following:
            raise ValueError("Нельзя подписаться на самого себя")
        super().save(*args, **kwargs)


class Notification(models.Model):
    """Уведомления пользователя"""
    NOTIFICATION_TYPES = [
        ('follow', 'Новый подписчик'),
        ('like', 'Лайк рецепта'),
        ('comment', 'Комментарий к рецепту'),
        ('favorite', 'Рецепт добавлен в избранное'),
        ('recipe', 'Новый рецепт от подписки'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='Получатель')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', verbose_name='Отправитель')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name='Тип уведомления')
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    link = models.URLField(blank=True, verbose_name='Ссылка')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return f'{self.recipient.username}: {self.title}'

    @classmethod
    def create_follow_notification(cls, follower, following):
        """Создать уведомление о новой подписке"""
        return cls.objects.create(
            recipient=following,
            sender=follower,
            notification_type='follow',
            title='Новый подписчик',
            message=f'{follower.username} подписался на вас',
            link=f'/user/{follower.username}/'
        )

    @classmethod
    def create_like_notification(cls, user, recipe):
        """Создать уведомление о лайке"""
        if user != recipe.author:
            return cls.objects.create(
                recipient=recipe.author,
                sender=user,
                notification_type='like',
                title='Новый лайк',
                message=f'{user.username} оценил ваш рецепт "{recipe.title}"',
                link=f'/recipe/{recipe.slug}/'
            )
        return None

    @classmethod
    def create_comment_notification(cls, user, recipe, comment):
        """Создать уведомление о комментарии"""
        if user != recipe.author:
            return cls.objects.create(
                recipient=recipe.author,
                sender=user,
                notification_type='comment',
                title='Новый комментарий',
                message=f'{user.username} прокомментировал ваш рецепт "{recipe.title}"',
                link=f'/recipe/{recipe.slug}/'
            )
        return None

    @classmethod
    def create_recipe_notification(cls, recipe):
        """Создать уведомления о новом рецепте для подписчиков"""
        notifications = []
        for follow in recipe.author.followers.all():
            notification = cls.objects.create(
                recipient=follow.follower,
                sender=recipe.author,
                notification_type='recipe',
                title='Новый рецепт',
                message=f'{recipe.author.username} опубликовал новый рецепт "{recipe.title}"',
                link=f'/recipe/{recipe.slug}/'
            )
            notifications.append(notification)
        return notifications
