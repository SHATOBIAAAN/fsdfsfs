from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    """Модель категории для историй"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug категории")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]
    
    def __str__(self):
        return self.name


class Story(models.Model):
    """Модель истории/случая, связанная с пользователем"""
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stories", verbose_name="Автор")
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание истории")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус модерации"
    )
    categories = models.ManyToManyField(
        Category, 
        related_name="story_categories", 
        blank=True,
        verbose_name="Категории"
    )
    # Поддерживаем старое поле category для обратной совместимости
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        related_name="stories", 
        null=True, blank=True,
        verbose_name="Главная категория"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    likes = models.ManyToManyField(User, related_name="liked_stories", blank=True, verbose_name="Лайки")
    dislikes = models.ManyToManyField(User, related_name="disliked_stories", blank=True, verbose_name="Дизлайки")
    
    class Meta:
        verbose_name = "История"
        verbose_name_plural = "Истории"
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.title
    
    def like_count(self):
        return self.likes.count()
        
    def dislike_count(self):
        return self.dislikes.count()
        
    def comment_count(self):
        return self.comments.count()


class StoryMedia(models.Model):
    """Модель для хранения медиа-файлов, связанных с историей"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="media_files", verbose_name="История")
    file = models.FileField(upload_to="story_media/", verbose_name="Файл")
    file_type = models.CharField(max_length=20, blank=True, null=True, verbose_name="Тип файла")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    
    class Meta:
        verbose_name = "Медиа-файл"
        verbose_name_plural = "Медиа-файлы"
    
    def __str__(self):
        return f"Медиа для {self.story.title}"
    
    def save(self, *args, **kwargs):
        # Определяем тип файла при сохранении
        file_name = self.file.name.lower()
        if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            self.file_type = 'image'
        elif file_name.endswith(('.mp4', '.avi', '.mov')):
            self.file_type = 'video'
        elif file_name.endswith(('.mp3', '.wav', '.ogg')):
            self.file_type = 'audio'
        else:
            self.file_type = 'other'
        
        super().save(*args, **kwargs)


class Comment(models.Model):
    """Модель комментариев к историям"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="comments", verbose_name="История")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments", verbose_name="Автор")
    content = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Комментарий от {self.user.profile.nickname} к {self.story.title[:20]}"


class SiteSettings(models.Model):
    """Модель для хранения настроек сайта"""
    key = models.CharField(max_length=100, unique=True, verbose_name="Ключ настройки")
    value = models.TextField(verbose_name="Значение")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    
    class Meta:
        verbose_name = "Настройка сайта"
        verbose_name_plural = "Настройки сайта"
        
    def __str__(self):
        return self.key
        
    @classmethod
    def get_token_url(cls):
        """Получить URL для покупки токена"""
        try:
            return cls.objects.get(key="token_purchase_url").value
        except cls.DoesNotExist:
            # Если настройка не найдена, создаем её с дефолтным значением
            token_url = cls.objects.create(
                key="token_purchase_url",
                value="https://example.com/token",
                description="URL для покупки токена"
            )
            return token_url.value
