# Lambda Search

![Pipeline Status](https://gitlab.crja72.ru/django/2024/autumn/course/projects/team-3/badges/main/pipeline.svg)

Проект доступен по адресу https://lambda-search.ru

## О проекте
Lambda Search — это инструмент, созданный для проверки, были ли ваши данные скомпрометированы в результате утечек. Мы ориентированы на российских пользователей и учитываем локальные риски и угрозы. Сервис предоставляет удобный интерфейс для анализа утечек, позволяя пользователям быстро реагировать на возможные угрозы.

## Требования

- python 3.12.1
- PostgreSQL (установка: [PostgreSQL Official Docs](https://www.postgresql.org/download/))

## Инструкция по запуску проекта

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://gitlab.crja72.ru/django/2024/autumn/course/projects/team-3.git
   cd lambda_search
   ```

2. **Создайте и активируйте виртуальное окружение:**

   - На Linux/macOS:

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

   - На Windows:

     ```bash
     python3 -m venv venv
     venv\Scripts\activate
     ```

   2.1 **Обновите pip:**

   ```bash
   python3 -m pip3 install --upgrade pip
   ```

3. **Установите зависимости:**

   1. Основные:

      ```bash
      pip3 install -r requirements/prod.txt
      ```

   2. Для тестирования:

      ```bash
      pip3 install -r requirements/test.txt
      ```

   3. Для разработки:

      ```bash
      pip3 install -r requirements/dev.txt
      ```

4. **Настройка окружения:**

   Скопируйте шаблон файла настроек окружения и заполните его:

   ```bash
   cp .env.template .env
   ```

   Пример файла `.env`:

   ```plaintext
   # Django project settings
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=your_secret_key
   DJANGO_ALLOWED_HOSTS=*
   DJANGO_SITE_URL="https://lambda-search.ru"
   DJANGO_ENCRYPTION_KEY="dsEa3e6lF983WPH88NsSS9A0HGCIK5xA"

   # Superuser settings
   LAMBDA_SUPERUSER_NAME=admin
   LAMBDA_SUPERUSER_EMAIL=lambda-search@yandex.ru
   LAMBDA_SUPERUSER_PASSWORD=4pNWn03s!6zKka7Bhed574H

   # PostgreSQL database settings
   DJANGO_POSTGRESQL_NAME=lambda_db
   DJANGO_POSTGRESQL_USER=lambda_user
   DJANGO_POSTGRESQL_PASSWORD=your_password
   DJANGO_POSTGRESQL_HOST=localhost
   DJANGO_POSTGRESQL_PORT=5432

   # Let's Encrypt settings for nginx
   LAMBDA_CERTBOT_DEBUG=1
   LAMBDA_CERTBOT_STAGING=1
   LAMBDA_CERTBOT_EMAIL=lambda-search@yandex.ru
   ```

5. **Выполните локализации**

   Необходимо установить **gettext**

   Windows: [gettext](https://mlocati.github.io/articles/gettext-iconv-windows.html)

   Linux:
   (Пакетный менеджер может отличаться)

   ```bash
   apt-get update
   apt-get install gettext
   ```

   MacOS:

   ```bash
   brew install gettext
   ```

   В данный момент добавлен русский и английский язык

   Перед запуском необходимо скомпилировать локализации

   ```bash
   cd lyceum
   django-admin compilemessages
   ```

6. **Примените миграции:**

   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

7. **Запустите сервер:**

   ```bash
   python3 manage.py runserver
   ```

   После этого сервер будет доступен по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/).


## Другие команды

**Для создания суперпользователя:**

```bash
python3 manage.py createsuperuser
```

**Для тестов:**

```bash
python3 manage.py test
```

## ER-диаграмма БД

![image info](ER.jpg)

