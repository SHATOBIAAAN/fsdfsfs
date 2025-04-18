from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.text import slugify
from .models import Category, Story, StoryMedia, Comment
import re
from django.db.models import Count
from django.db import models
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def MainPage(request):
    return render(request, 'base/MainPage.j2')

def story_list(request):
    """Отображение списка историй с возможностью фильтрации по категории и сортировки"""
    # Определяем тип сортировки из параметра запроса
    sort_type = request.GET.get('sort', 'new')
    
    # Базовый запрос историй - только одобренные
    stories = Story.objects.filter(status='approved')
    
    # Применяем соответствующую сортировку
    if sort_type == 'popular':
        # Сортируем по количеству лайков (популярные)
        stories = stories.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
    elif sort_type == 'liked' and request.user.is_authenticated:
        # Показываем только истории, которые лайкнул пользователь
        stories = stories.filter(likes=request.user).order_by('-created_at')
    elif sort_type == 'old':
        # Сортируем по дате создания (старые в начале)
        stories = stories.order_by('created_at')
    else:
        # По умолчанию сортируем по дате создания (новые)
        stories = stories.order_by('-created_at')
    
    # Фильтрация по категориям
    categories_param = request.GET.get('categories')
    if categories_param:
        try:
            # Разбиваем строку с ID категорий на список
            category_ids = [int(cat_id) for cat_id in categories_param.split(',') if cat_id]
            
            if category_ids:
                # Создаем Q-объект для фильтрации по нескольким категориям
                query = models.Q()
                
                # Добавляем каждую категорию в OR-запрос
                for category_id in category_ids:
                    query |= models.Q(categories__id=category_id) | models.Q(category_id=category_id)
                
                # Применяем фильтр и удаляем дубликаты
                stories = stories.filter(query).distinct()
        except (ValueError, TypeError):
            # Если не удалось преобразовать в числа, игнорируем фильтр
            pass
    # Если нет фильтрации по нескольким категориям, применяем обычную фильтрацию по одной категории
    else:
        # Фильтрация по категории
        category_id = request.GET.get('category')
        if category_id and category_id != 'all' and category_id != 'None':
            try:
                # Преобразуем строку в целое число для безопасной фильтрации
                category_id_int = int(category_id)
                # Отфильтруем истории, которые имеют указанную категорию
                # в новом поле categories или в старом поле category
                stories = stories.filter(
                    models.Q(categories__id=category_id_int) | models.Q(category_id=category_id_int)
                ).distinct()  # distinct() для удаления дубликатов
            except (ValueError, TypeError):
                # Если не удалось преобразовать в число, игнорируем фильтр
                pass
    
    # Получение всех категорий для фильтрации
    categories = Category.objects.all()
    
    # Реализуем пагинацию - ограничиваем количество историй на странице
    items_per_page = 10  # Можно изменить в зависимости от требований
    
    # Получаем текущую страницу из параметров запроса
    page_number = request.GET.get('page', 1)
    try:
        page_number = int(page_number)
        if page_number < 1:
            page_number = 1
    except (ValueError, TypeError):
        page_number = 1
    
    # Получаем общее количество историй
    total_stories = stories.count()
    
    # Вычисляем количество страниц
    total_pages = (total_stories + items_per_page - 1) // items_per_page
    
    # Применяем смещение для получения нужной страницы историй
    offset = (page_number - 1) * items_per_page
    stories = stories[offset:offset + items_per_page]
    
    # Контекст для шаблона
    context = {
        'page_obj': stories,
        'categories': categories,
        'current_sort': sort_type,
        'current_categories': request.GET.get('categories', ''),
        'current_page': page_number,
        'total_pages': total_pages,
        'total_stories': total_stories,
    }
    
    # Проверяем наличие флага об успешной отправке истории
    if request.session.pop('story_submitted', False):
        context['story_submitted'] = True
    
    return render(request, 'stories/StoryList.j2', context)

@login_required(login_url='login')
def new_story(request):
    """Создание новой истории"""
    # Получение всех категорий
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # Получение данных из формы
        title = request.POST.get('title')
        content = request.POST.get('content')
        categories_ids_str = request.POST.get('categories', '')  # Получаем список ID категорий из формы
        
        # Валидация
        if not title or not content:
            return render(request, 'stories/NewStory.j2', {
                'error': 'Заголовок и содержание истории обязательны',
                'categories': categories
            })
        
        # Создание истории
        story = Story(
            user=request.user,
            title=title,
            content=content,
            status='pending'  # Устанавливаем статус "на модерации"
        )
        
        # Сохраняем историю, чтобы потом добавить к ней категории
        story.save()
        
        # Добавление категорий, если выбраны
        if categories_ids_str:
            try:
                # Разбиваем строку с ID категорий на список
                categories_ids = [int(cat_id) for cat_id in categories_ids_str.split(',') if cat_id]
                
                # Находим категории и добавляем их к истории
                selected_categories = Category.objects.filter(id__in=categories_ids)
                story.categories.add(*selected_categories)
                
                # Устанавливаем первую категорию как основную для обратной совместимости
                if selected_categories.exists():
                    story.category = selected_categories.first()
                    story.save()
                    
            except (ValueError, Category.DoesNotExist):
                # Обработка ошибок при преобразовании строки в число или при поиске категории
                pass
        
        # Обработка загруженных файлов
        media_files = request.FILES.getlist('media_files')
        for media_file in media_files:
            StoryMedia.objects.create(story=story, file=media_file)
        
        # Устанавливаем флаг успешной отправки истории в сессию
        request.session['story_submitted'] = True
        return redirect('story_list')
    
    # GET запрос - отображаем форму
    return render(request, 'stories/NewStory.j2', {
        'categories': categories
    })

@login_required(login_url='login')
def create_category(request):
    """Создание новой категории (только для администраторов)"""
    if not request.user.is_staff:
        return redirect('story_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if not name:
            return render(request, 'stories/CreateCategory.j2', {
                'error': 'Название категории обязательно'
            })
        
        # Генерация slug из названия
        slug = slugify(name)
        
        # Проверка уникальности slug
        if Category.objects.filter(slug=slug).exists():
            return render(request, 'stories/CreateCategory.j2', {
                'error': 'Категория с таким названием уже существует'
            })
        
        # Создание категории
        Category.objects.create(name=name, slug=slug, description=description)
        return redirect('admin:stories_category_changelist')
    
    return render(request, 'stories/CreateCategory.j2')

def story_detail(request, story_id):
    """Отображение деталей истории"""
    # Получаем историю по ID и проверяем, что она одобрена
    story = get_object_or_404(Story, id=story_id, status='approved')
    context = {'story': story}
    return render(request, 'stories/StoryDetail.j2', context)

@login_required(login_url='login')
def like_story(request, story_id):
    """Добавление или удаление лайка истории"""
    story = get_object_or_404(Story, id=story_id)
    
    # Проверяем, был ли дизлайк ранее и удаляем его
    if request.user in story.dislikes.all():
        story.dislikes.remove(request.user)
    
    # Проверяем, лайкнул ли пользователь историю
    if request.user in story.likes.all():
        # Удаляем лайк
        story.likes.remove(request.user)
    else:
        # Добавляем лайк
        story.likes.add(request.user)
    
    # Возвращаем пользователя на страницу истории
    return redirect('story_detail', story_id=story_id)

@login_required(login_url='login')
def dislike_story(request, story_id):
    """Добавление или удаление дизлайка истории"""
    story = get_object_or_404(Story, id=story_id)
    
    # Проверяем, был ли лайк ранее и удаляем его
    if request.user in story.likes.all():
        story.likes.remove(request.user)
    
    # Проверяем, дизлайкнул ли пользователь историю
    if request.user in story.dislikes.all():
        # Удаляем дизлайк
        story.dislikes.remove(request.user)
    else:
        # Добавляем дизлайк
        story.dislikes.add(request.user)
    
    # Возвращаем пользователя на страницу истории
    return redirect('story_detail', story_id=story_id)

@require_POST
def ajax_like_story(request, story_id):
    """AJAX-обработчик для лайка истории"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Пожалуйста, авторизуйтесь'}, status=401)
    
    story = get_object_or_404(Story, id=story_id)
    
    # Проверяем, был ли дизлайк ранее и удаляем его
    was_disliked = request.user in story.dislikes.all()
    if was_disliked:
        story.dislikes.remove(request.user)
    
    # Проверяем, лайкнул ли пользователь историю
    if request.user in story.likes.all():
        # Удаляем лайк
        story.likes.remove(request.user)
        liked = False
    else:
        # Добавляем лайк
        story.likes.add(request.user)
        liked = True
    
    # Возвращаем обновленные счетчики и статус
    return JsonResponse({
        'status': 'success',
        'liked': liked,
        'likes_count': story.likes.count(),
        'dislikes_count': story.dislikes.count(),
        'was_disliked': was_disliked
    })

@require_POST
def ajax_dislike_story(request, story_id):
    """AJAX-обработчик для дизлайка истории"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Пожалуйста, авторизуйтесь'}, status=401)
    
    story = get_object_or_404(Story, id=story_id)
    
    # Проверяем, был ли лайк ранее и удаляем его
    was_liked = request.user in story.likes.all()
    if was_liked:
        story.likes.remove(request.user)
    
    # Проверяем, дизлайкнул ли пользователь историю
    if request.user in story.dislikes.all():
        # Удаляем дизлайк
        story.dislikes.remove(request.user)
        disliked = False
    else:
        # Добавляем дизлайк
        story.dislikes.add(request.user)
        disliked = True
    
    # Возвращаем обновленные счетчики и статус
    return JsonResponse({
        'status': 'success',
        'disliked': disliked,
        'likes_count': story.likes.count(),
        'dislikes_count': story.dislikes.count(),
        'was_liked': was_liked
    })

def story_comments(request, story_id):
    """Страница комментариев к истории"""
    story = get_object_or_404(Story, id=story_id, status='approved')
    comments = story.comments.all().order_by('-created_at')
    
    context = {
        'story': story,
        'comments': comments
    }
    return render(request, 'stories/StoryComments.j2', context)

@login_required(login_url='login')
def add_comment(request, story_id):
    """Добавление комментария к истории"""
    story = get_object_or_404(Story, id=story_id, status='approved')
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        
        if content:
            comment = Comment.objects.create(
                story=story,
                user=request.user,
                content=content
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Если это AJAX запрос, возвращаем данные нового комментария
                return JsonResponse({
                    'status': 'success',
                    'comment': {
                        'user_nickname': comment.user.profile.nickname,
                        'user_photo': comment.user.profile.photo.url if comment.user.profile.photo else None,
                        'content': comment.content,
                        'user_initial': comment.user.profile.nickname[:1].upper()
                    }
                })
            
            # Если обычный POST запрос, перенаправляем на ту же страницу
            return redirect('story_comments', story_id=story_id)
        else:
            messages.error(request, 'Комментарий не может быть пустым')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Комментарий не может быть пустым'
                })
    
    return redirect('story_comments', story_id=story_id)

@require_POST
def clear_notification(request):
    """Очистка флага уведомления из сессии"""
    if 'story_submitted' in request.session:
        del request.session['story_submitted']
    return JsonResponse({'status': 'success'})

def story_media(request, story_id):
    """Отображение медиа-файлов истории"""
    story = get_object_or_404(Story, id=story_id, status='approved')
    
    # Получаем все медиа-файлы, связанные с историей
    media_files = story.media_files.all()
    
    context = {
        'story': story,
        'media_files': media_files
    }
    return render(request, 'Stories/ImageStory.j2', context)

def page_not_found_view(request, exception):
    """Обработчик для ошибки 404 Page Not Found."""
    return render(request, 'Base/404.j2', status=404)
