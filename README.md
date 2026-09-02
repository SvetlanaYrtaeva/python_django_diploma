# Интернет-магазин (Diploma Backend)

## Развёртывание

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd python_django_diploma/diploma-backend

# 2. Виртуальное окружение
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 3. Зависимости
pip install -r requirements.txt

# 4. Конфигурация
cp .env.example .env
# Отредактировать .env — указать SECRET_KEY, при необходимости CELERY_BROKER_URL

# 5. Миграции (создаст БД, админа и настройки магазина)
python manage.py migrate

# 6. Загрузка фикстур (категории, продавцы, товары)
python manage.py loaddata fixtures/catalog_categories.json
python manage.py loaddata fixtures/catalog_sellers.json
python manage.py loaddata fixtures/products.json

# 7. Тестовые покупатели (пароль: 123456)
python manage.py create_test_users

# 8. Статика
python manage.py collectstatic --noinput

# 9. Запуск
python manage.py runserver 0.0.0.0:8000
```

## Очередь платежей (Celery)

Для асинхронной обработки оплаты:

```bash
# Установить и запустить Redis
redis-server

# Запустить воркер (в отдельном терминале)
celery -A config worker -l info
```

Если Redis недоступен — платежи обрабатываются синхронно.

## Доступы

- **Админка:** http://localhost:8000/admin/
  - Логин: `admin@example.com`
  - Пароль: `admin123`
- **Тестовые покупатели:**
  - `buyer1@example.com` / `buyer2@example.com` / `buyer3@example.com`
  - Пароль: `123456`
