from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile
from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator, MinimumLengthValidator,
    CommonPasswordValidator, NumericPasswordValidator
)
from django.utils.translation import gettext_lazy as _

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email", "password1", "password2")
        error_messages = {
            'password_mismatch': "Пароли не совпадают. Попробуйте еще раз.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
        
        # Переопределяем сообщения об ошибках для пароля
        self.fields['password1'].help_text = _(
            "• Пароль должен содержать не менее 8 символов\n"
            "• Не используйте слишком простые пароли\n"
            "• Пароль не должен полностью состоять из цифр\n"
            "• Пароль не должен быть похож на ваш email"
        )
        
        # Ошибки валидации
        self.error_messages.update({
            'password_too_short': _("Пароль слишком короткий. Он должен содержать минимум 8 символов."),
            'password_too_similar': _("Пароль слишком похож на ваши личные данные. Используйте более надежный пароль."),
            'password_too_common': _("Пароль слишком простой. Используйте более сложную комбинацию."),
            'password_entirely_numeric': _("Пароль не может состоять только из цифр. Добавьте буквы или специальные символы."),
        })

    def clean_password2(self):
        """
        Переопределяем стандартную валидацию для улучшения сообщений об ошибках
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
            
        # Ручная проверка валидаторов с кастомными сообщениями
        email = self.cleaned_data.get('email', '')
        
        # Проверка на схожесть с email
        if email and password1:
            if email.lower() in password1.lower() or password1.lower() in email.lower():
                raise ValidationError(
                    "Пароль слишком похож на ваш email. Используйте более надежный пароль.",
                    code='password_too_similar',
                )
        
        # Проверка длины
        if len(password1) < 8:
            raise ValidationError(
                self.error_messages['password_too_short'],
                code='password_too_short'
            )
            
        # Проверка на полностью числовой пароль
        if password1.isdigit():
            raise ValidationError(
                self.error_messages['password_entirely_numeric'],
                code='password_entirely_numeric'
            )
            
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname', 'photo', 'crypto_token']
        widgets = {
            'nickname': forms.TextInput(attrs={'placeholder': 'Ваш никнейм'}),
            'crypto_token': forms.TextInput(attrs={'placeholder': 'Криптовалюта', 'id': 'cryptoTokenInput'})
        }

class UserEmailUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Новая почта'})
    )
    
    class Meta:
        model = User
        fields = ['email']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email != self.instance.email and User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с такой почтой уже существует')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Обновляем username вместе с email
        if commit:
            user.save()
        return user

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Текущий пароль'})
    )
    new_password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Новый пароль'})
    )
    new_password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердите новый пароль'})
    ) 