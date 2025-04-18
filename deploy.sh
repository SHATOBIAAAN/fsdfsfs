#!/bin/bash

# Переходим в директорию проекта
cd /home/nestrah/nestrah

# Активируем виртуальное окружение
source venv/bin/activate

# Создаем директории для логов если их нет
mkdir -p logs

# Обновляем код из репозитория
git pull

# Устанавливаем/обновляем зависимости
pip install -r requirements.txt

# Инициализируем базу данных если нужно
read -p "Инициализировать базу данных? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./init_db.sh
else
    # Просто применяем миграции
    python manage.py migrate
fi

# Собираем статические файлы
python manage.py collectstatic --noinput

# Перезапускаем сервисы
sudo supervisorctl restart nestrah
sudo supervisorctl restart celery
sudo systemctl reload nginx

# Проверяем статус сервисов
echo "Checking services status..."
sudo supervisorctl status
sudo systemctl status nginx | grep Active

echo "Deployment completed!" 