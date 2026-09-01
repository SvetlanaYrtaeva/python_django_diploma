# Интернет-магазин (Django Diploma)

## Описание
Django-проект интернет-магазина с каталогом товаров, корзиной, заказами и отзывами.

## Технологии
- Python 3.11
- Django 5.2
- SQLite
- Vue.js 3
- Django REST Framework

## Установка

1. Клонировать репозиторий
2. Создать виртуальное окружение: `python -m venv venv`
3. Активировать: `venv\Scripts\activate` (Windows)
4. Установить зависимости: `pip install -r requirements.txt`
5. Применить миграции: `python manage.py migrate`
6. Загрузить фикстуры: `python manage.py loaddata fixtures/initial_data.json`
7. Запустить: `python manage.py runserver 127.0.0.1:8010`

## Структура
- `catalog/` — товары, категории, продавцы
- `cart/` — корзина
- `orders/` — заказы
- `users/` — пользователи, авторизация
- `reviews/` — отзывы

## API Endpoints

### Каталог
- `GET /api/catalog` — список товаров
- `GET /api/categories` — категории
- `GET /api/products/popular` — популярные товары
- `GET /api/products/limited` — лимитированные товары
- `GET /api/tags` — теги (продавцы)

### Корзина
- `GET /api/basket` — получить корзину
- `POST /api/basket` — добавить товар
- `DELETE /api/basket` — удалить товар

### Авторизация
- `POST /api/sign-in` — вход
- `POST /api/sign-out` — выход
- `POST /api/sign-up` — регистрация

## Админ-панель
http://127.0.0.1:8010/admin/

## Фикстуры
`fixtures/initial_data.json` — 7 объектов (категории, товары, продавец, пользователь)