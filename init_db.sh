#!/bin/bash

# Загружаем переменные окружения
source .env

# Проверяем, установлен ли PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL не установлен. Устанавливаем..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
fi

# Создаем пользователя и базу данных
echo "Создаем пользователя и базу данных..."
sudo -u postgres psql << EOF
-- Создаем пользователя если его нет
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

-- Удаляем базу если она существует
DROP DATABASE IF EXISTS $DB_NAME;

-- Создаем базу данных
CREATE DATABASE $DB_NAME;

-- Даем права пользователю
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
EOF

echo "База данных $DB_NAME создана и настроена!"

# Применяем миграции
echo "Применяем миграции..."
cd /home/nestrah/nestrah
source venv/bin/activate
python manage.py migrate

# Создаем суперпользователя если нужно
read -p "Создать суперпользователя Django? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

echo "Инициализация базы данных завершена!" 