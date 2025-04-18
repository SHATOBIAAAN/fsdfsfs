from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ProfileUpdateForm, UserEmailUpdateForm, CustomPasswordChangeForm
from .models import Profile
import os
from stories.models import Story

# Create your views here.

@login_required(login_url='login')
def profile(request):
    # Получаем профиль или создаем, если не существует
    try:
        profile_obj = request.user.profile
    except Profile.DoesNotExist:
        profile_obj = Profile.objects.create(user=request.user, nickname=f'Аноним{request.user.id}')
    
    # Получаем актуальный email пользователя из имени пользователя
    # (при регистрации email сохраняется как username)
    email_to_display = request.user.username
    
    # Инициализируем формы с текущими данными
    p_form = ProfileUpdateForm(instance=profile_obj)
    e_form = UserEmailUpdateForm(instance=request.user)
    password_form = CustomPasswordChangeForm(request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            # Проверяем флаг удаления фото
            delete_photo = request.POST.get('delete_photo') == '1'
            
            if delete_photo and profile_obj.photo:
                # Сохраняем путь к старой фотографии для последующего удаления
                old_photo = profile_obj.photo.path
                
                # Удаляем фото из профиля
                profile_obj.photo = None
                profile_obj.save()
                
                # Удаляем файл с диска, если он существует
                if os.path.isfile(old_photo):
                    os.remove(old_photo)
                
                # Обновляем форму из остальных данных, исключая поле photo
                form_data = request.POST.copy()
                form = ProfileUpdateForm(form_data, instance=profile_obj)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Ваш профиль успешно обновлен!')
                return redirect('profile')
            else:
                # Стандартная обработка формы
                form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_obj)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Ваш профиль успешно обновлен!')
                    return redirect('profile')
                else:
                    p_form = form
        elif action == 'update_nickname':
            form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_obj)
            if form.is_valid():
                form.save()
                messages.success(request, 'Ваш профиль успешно обновлен!')
                return redirect('profile')
            else:
                p_form = form
        elif action == 'update_photo':
            form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_obj)
            if form.is_valid():
                form.save()
                messages.success(request, 'Фото профиля успешно обновлено!')
                return redirect('profile')
            else:
                p_form = form
        elif action == 'update_email':
            form = UserEmailUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                user = form.save()
                # Обновляем отображаемый email
                email_to_display = user.username
                messages.success(request, 'Ваша почта успешно обновлена!')
                return redirect('profile')
            else:
                e_form = form
        elif action == 'change_password':
            form = CustomPasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Ваш пароль успешно изменен!')
                return redirect('profile')
            else:
                password_form = form
        elif action == 'delete_account':
            request.user.delete()
            messages.success(request, 'Ваш аккаунт был успешно удален!')
            return redirect('login')
    
    # Получаем количество публикаций пользователя
    posts_count = Story.objects.filter(user=request.user).count()
    
    context = {
        'p_form': p_form,
        'e_form': e_form,
        'password_form': password_form,
        'profile': profile_obj,
        'user': request.user,
        'email': email_to_display,  # Добавляем email отдельно в контекст
        'posts_count': posts_count
    }
    
    return render(request, 'users/profile.j2', context)

def login_view(request):
    # Если пользователь уже аутентифицирован, редирект на профиль
    if request.user.is_authenticated:
        return redirect('profile')
        
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        # Если email пустой
        if not email:
            return render(request, 'users/login.j2', {'error': 'Введите email'})
        
        # Проверяем существует ли пользователь
        from django.contrib.auth.models import User
        
        # Простая проверка на существование пользователя
        user_exists = User.objects.filter(email__iexact=email).exists()
        
        if not user_exists:
            # Если пользователя нет - предлагаем зарегистрироваться
            return render(request, 'users/login.j2', 
                         {'error': 'Пользователь с такой почтой не найден, вам нужно зарегистрироваться.'})
        
        # Находим пользователя и проверяем пароль
        user_obj = User.objects.get(email__iexact=email)
        auth_user = authenticate(request, username=user_obj.username, password=password)
        
        if auth_user:
            login(request, auth_user)
            return redirect('profile')
        else:
            # Пароль неверный
            return render(request, 'users/login.j2', {'error': 'Неверный пароль!'})
    
    # GET запрос
    return render(request, 'users/login.j2')

def register(request):
    # Если пользователь уже аутентифицирован, редирект на профиль
    if request.user.is_authenticated:
        return redirect('profile')
        
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        # Если email пустой
        if not email:
            form = UserRegisterForm(request.POST)
            return render(request, 'users/register.j2', {'form': form, 'error': 'Введите email'})
        
        # Проверяем, существует ли пользователь с таким email
        from django.contrib.auth.models import User
        if User.objects.filter(email__iexact=email).exists():
            form = UserRegisterForm(request.POST)
            return render(request, 'users/register.j2', 
                         {'form': form, 'error': 'Пользователь с такой почтой уже зарегистрирован'})
        
        # Если уникальный email, обрабатываем форму
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            messages.success(request, f'Аккаунт успешно создан для {email}!')
            login(request, user)
            return redirect('profile')
        else:
            # Обработка ошибок валидации формы
            error_messages = []
            
            # Получаем и обрабатываем все ошибки из формы
            for field, errors in form.errors.items():
                field_name = field
                if field == 'password2':
                    field_name = 'Пароль'
                elif field == 'password1':
                    field_name = 'Пароль'
                elif field == 'email':
                    field_name = 'Email'
                    
                for error in errors:
                    error_messages.append(f"{error}")
            
            if error_messages:
                error = error_messages[0]  # Берем первую ошибку
            else:
                error = 'Ошибка при регистрации. Проверьте данные и попробуйте снова.'
                
            return render(request, 'users/register.j2', {'form': form, 'error': error, 'all_errors': error_messages})
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.j2', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
