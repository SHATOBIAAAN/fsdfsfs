from django.core.management.base import BaseCommand
import psycopg2
from django.conf import settings

class Command(BaseCommand):
    help = 'Сбрасывает базу данных и создает её заново'

    def handle(self, *args, **options):
        db_settings = settings.DATABASES['default']
        
        # Подключаемся к PostgreSQL
        conn = psycopg2.connect(
            host=db_settings['HOST'],
            port=db_settings['PORT'],
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            database='postgres'  # Подключаемся к системной БД
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Закрываем все соединения к базе
        self.stdout.write(self.style.WARNING(f'Закрываем все соединения к базе {db_settings["NAME"]}...'))
        cursor.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{db_settings["NAME"]}'
        AND pid <> pg_backend_pid();
        """)
        
        # Удаляем базу данных
        self.stdout.write(self.style.WARNING(f'Удаляем базу данных {db_settings["NAME"]}...'))
        try:
            cursor.execute(f'DROP DATABASE "{db_settings["NAME"]}";')
        except psycopg2.Error as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при удалении базы: {e}'))
        
        # Создаем базу данных заново
        self.stdout.write(self.style.WARNING(f'Создаем базу данных {db_settings["NAME"]}...'))
        cursor.execute(f'CREATE DATABASE "{db_settings["NAME"]}";')
        
        # Закрываем соединение
        cursor.close()
        conn.close()
        
        self.stdout.write(self.style.SUCCESS('База данных успешно сброшена. Теперь выполните миграции: python manage.py migrate')) 