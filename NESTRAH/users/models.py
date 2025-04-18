from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=150, blank=True, null=True, verbose_name='Никнейм')
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, verbose_name='Фото профиля')
    crypto_token = models.CharField(max_length=255, default='TON', blank=True, verbose_name='Токен для криптовалюты')
    tokens_balance = models.PositiveIntegerField(default=0, verbose_name='Баланс токенов')
    tokens_paid = models.PositiveIntegerField(default=0, verbose_name='Всего выплачено токенов')
    
    def __str__(self):
        return f'Профиль пользователя {self.user.email}'
    
    def get_total_likes(self):
        """Возвращает общее количество лайков у всех историй пользователя"""
        from stories.models import Story
        return Story.objects.filter(user=self.user).aggregate(Sum('likes')).get('likes__sum', 0) or 0
    
    def calculate_unpaid_tokens(self):
        """Рассчитывает количество невыплаченных токенов (1 лайк = 1 токен)"""
        total_likes = self.get_total_likes()
        return total_likes - self.tokens_paid

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создает профиль пользователя при создании пользователя."""
    if created:
        Profile.objects.create(user=instance, nickname=f'Аноним{instance.id}')