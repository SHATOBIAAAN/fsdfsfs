from django.contrib import admin
from django.urls import path, include, re_path
from stories.views import MainPage
from django.conf import settings
from django.views.static import serve
# Импортируем представление для 404
from stories.views import page_not_found_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainPage, name='MainPage'),
    path('stories/', include('stories.urls')),
    path('users/', include('users.urls')),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Указываем обработчик для ошибки 404
handler404 = page_not_found_view