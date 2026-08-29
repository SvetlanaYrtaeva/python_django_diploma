# Интернет-магазин (Django Diploma)

## Описание
Django-проект интернет-магазина с каталогом товаров, корзиной, заказами и админ-панелью.

## Технологии
- Python 3.11
- Django 5.2
- SQLite (для разработки)
- Vue.js 3 (фронтенд)

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone <url-репозитория>
cd diploma-backend
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Примените миграции:
```bash
python manage.py migrate
```

5. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

6. Загрузите фикстуры (тестовые данные):
```bash
python manage.py loaddata fixtures/initial_data.json
```

7. Запустите сервер:
```bash
python manage.py runserver 127.0.0.1:8010
```

8. Откройте в браузере: http://127.0.0.1:8010/

## Структура проекта
- `catalog/` — каталог товаров, категории, продавцы
- `cart/` — корзина
- `orders/` — заказы
- `users/` — пользователи
- `config/` — настройки проекта

## Админ-панель
http://127.0.0.1:8010/admin/

