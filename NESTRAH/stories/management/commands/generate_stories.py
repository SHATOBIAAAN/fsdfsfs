from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from stories.models import Story, Category, Comment
from django.utils import timezone
from faker import Faker
import random
from datetime import timedelta
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Generates test stories with categories, likes, and comments'

    def handle(self, *args, **kwargs):
        fake = Faker('ru_RU')
        User = get_user_model()

        # Получаем или создаем тестового пользователя
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            # Создаем профиль для пользователя если нужно
            if hasattr(test_user, 'profile'):
                test_user.profile.nickname = 'Тестовый Пользователь'
                test_user.profile.save()

        # Создаем или получаем категории
        categories = [
            'Смешные', 'Грустные', 'Страшные', 'Романтические', 
            'На работе', 'В транспорте', 'В магазине', 'На улице',
            'С друзьями', 'С семьей'
        ]
        category_objects = []
        for cat_name in categories:
            # Создаем уникальный slug из названия категории
            slug = slugify(cat_name)
            if not slug:  # Если slugify вернул пустую строку
                slug = f"category-{len(category_objects) + 1}"
                
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={'slug': slug}
            )
            category_objects.append(cat)

        # Создаем 100 историй
        for i in range(100):
            # Генерируем случайную дату за последний год
            random_date = timezone.now() - timedelta(days=random.randint(0, 365))
            
            # Создаем историю
            story = Story.objects.create(
                title=fake.sentence(nb_words=6, variable_nb_words=True),
                content=fake.text(max_nb_chars=2000),
                user=test_user,
                created_at=random_date,
                status='approved'  # Устанавливаем статус как одобренный
            )

            # Добавляем случайные категории (1-3)
            num_categories = random.randint(1, 3)
            story.categories.add(*random.sample(category_objects, num_categories))

            # Добавляем случайное количество лайков (0-50)
            num_likes = random.randint(0, 50)
            for _ in range(num_likes):
                story.likes.add(test_user)

            # Добавляем случайное количество дизлайков (0-20)
            num_dislikes = random.randint(0, 20)
            for _ in range(num_dislikes):
                story.dislikes.add(test_user)

            # Добавляем случайное количество комментариев (0-10)
            num_comments = random.randint(0, 10)
            for _ in range(num_comments):
                Comment.objects.create(
                    story=story,
                    user=test_user,
                    content=fake.sentence(nb_words=10, variable_nb_words=True),
                    created_at=random_date + timedelta(days=random.randint(0, 30))
                )

            self.stdout.write(f'Created story {i+1}/100')

        self.stdout.write(self.style.SUCCESS('Successfully generated 100 test stories')) 