from jinja2 import Environment, FileSystemLoader
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from pathlib import Path

def environment(**options):
    # Указываем путь к папке с шаблонами
    template_dir = Path(__file__).resolve().parent.parent / 'templates'
    env = Environment(
        loader=FileSystemLoader(template_dir),
        extensions=[
            'jinja2.ext.loopcontrols',
            'jinja2.ext.do',
            'jinja2.ext.i18n',
            
        ],
        autoescape=True,
        auto_reload=options.get('auto_reload', False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    
    # Определяем пользовательскую функцию url, которая правильно обрабатывает аргументы
    def custom_url(view_name, *args, **kwargs):
        # Если передан только один аргумент (не именованный), и он является целым числом,
        # то это ID для URL-параметра (например story_id)
        if args and len(args) == 1 and isinstance(args[0], int):
            # Список представлений, которые принимают story_id
            story_id_views = [
                'story_detail', 'add_comment', 'like_story', 'dislike_story', 
                'story_comments', 'ajax_like_story', 'ajax_dislike_story'
            ]
            
            if view_name in story_id_views:
                return reverse(view_name, kwargs={'story_id': args[0]})
            else:
                # Для других URL с одним параметром
                return reverse(view_name, args=args)
        else:
            # Для всех остальных случаев
            return reverse(view_name, args=args, kwargs=kwargs)
    
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': custom_url,
    })
    
    # Добавляем контекстный процессор для request и user
    from django.template.context_processors import csrf
    
    def _get_user(request):
        return {'user': request.user}
    
    def _csrf_token(request):
        return {'csrf_token': csrf(request)['csrf_token']}
    
    def _get_profile(request):
        if request.user.is_authenticated:
            try:
                # Импортируем Profile только здесь, чтобы избежать циклических импортов
                from users.models import Profile
                try:
                    profile = request.user.profile
                except Profile.DoesNotExist:
                    profile = Profile.objects.create(user=request.user, nickname=f'Аноним{request.user.id}')
                return {'user_profile': profile}
            except:
                return {'user_profile': None}
        return {'user_profile': None}
    
    def _get_site_settings(request):
        # Импорт здесь, чтобы избежать циклических импортов
        from stories.models import SiteSettings
        try:
            token_url = SiteSettings.get_token_url()
            return {'token_url': token_url}
        except:
            return {'token_url': '#'}
    
    env.globals['get_user'] = _get_user
    env.globals['csrf_token'] = _csrf_token
    env.globals['get_profile'] = _get_profile
    env.globals['get_site_settings'] = _get_site_settings
    
    return env