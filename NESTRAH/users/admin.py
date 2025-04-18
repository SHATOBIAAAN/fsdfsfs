from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Переопределяем админку для модели User
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    
    def delete_model(self, request, obj):
        """
        Обеспечивает полное удаление пользователя из базы данных
        """
        obj.delete()
        
    def delete_queryset(self, request, queryset):
        """
        Обеспечивает полное удаление набора пользователей из базы данных
        """
        queryset.delete()

# Отменяем стандартную регистрацию User и регистрируем нашу версию
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname')
    search_fields = ('user__email', 'nickname')
    
    def delete_model(self, request, obj):
        """
        При удалении профиля также удаляем связанного пользователя
        """
        user = obj.user
        obj.delete()
        user.delete()
        
    def delete_queryset(self, request, queryset):
        """
        При удалении нескольких профилей также удаляем связанных пользователей
        """
        users = [profile.user for profile in queryset]
        queryset.delete()
        User.objects.filter(id__in=[user.id for user in users]).delete()
