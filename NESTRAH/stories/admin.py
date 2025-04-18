from django.contrib import admin
from .models import Category, Story, StoryMedia, Comment, SiteSettings
from django.utils.html import format_html

# Регистрация модели Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    ordering = ('name',)

# Inline модель для медиа-файлов
class StoryMediaInline(admin.TabularInline):
    model = StoryMedia
    extra = 1
    fields = ('file', 'file_type', 'uploaded_at')
    readonly_fields = ('file_type', 'uploaded_at')

# Inline модель для комментариев
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('user', 'content', 'created_at')
    readonly_fields = ('user', 'created_at')
    can_delete = True
    show_change_link = True
    verbose_name = "Комментарий"
    verbose_name_plural = "Комментарии"

# Действия для модерации
def approve_stories(modeladmin, request, queryset):
    queryset.update(status='approved')
approve_stories.short_description = "Одобрить выбранные истории"

def reject_stories(modeladmin, request, queryset):
    queryset.update(status='rejected')
reject_stories.short_description = "Отклонить выбранные истории"

# Регистрация модели Story
@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'created_at', 'get_likes_count', 'get_dislikes_count', 'get_status')
    list_filter = ('category', 'created_at', 'status')
    search_fields = ('title', 'content', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [StoryMediaInline, CommentInline]
    filter_horizontal = ('likes', 'dislikes', 'categories')
    actions = [approve_stories, reject_stories]
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    get_likes_count.short_description = 'Лайки'
    
    def get_dislikes_count(self, obj):
        return obj.dislikes.count()
    get_dislikes_count.short_description = 'Дизлайки'
    
    def get_status(self, obj):
        status_colors = {
            'pending': '#FFA500',  # Оранжевый для ожидающих
            'approved': '#00A000',  # Зеленый для одобренных
            'rejected': '#FF0000',  # Красный для отклоненных
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            status_colors.get(obj.status, '#000000'),
            obj.get_status_display()
        )
    get_status.short_description = 'Статус'

# Регистрация модели StoryMedia (если нужно отдельно)
@admin.register(StoryMedia)
class StoryMediaAdmin(admin.ModelAdmin):
    list_display = ('story', 'file_type', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('story__title',)
    readonly_fields = ('file_type', 'uploaded_at')

# Регистрация модели Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('story', 'user', 'short_content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'user__email', 'story__title')
    readonly_fields = ('created_at',)
    
    def short_content(self, obj):
        if len(obj.content) > 30:
            return obj.content[:30] + '...'
        return obj.content
    short_content.short_description = 'Текст комментария'

# Регистрация модели SiteSettings
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description')
    search_fields = ('key', 'value', 'description')
    list_editable = ('value',)
    
    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление настроек через админку для предотвращения случайного удаления
        return False
