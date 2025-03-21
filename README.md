# Lambda Search


Проект доступен по адресу https://lambda-search.ru

## О проекте
Lambda Search — это инструмент, созданный для проверки, были ли ваши данные скомпрометированы в результате утечек. Мы ориентированы на российских пользователей и учитываем локальные риски и угрозы. Сервис предоставляет удобный интерфейс для анализа утечек, позволяя пользователям быстро реагировать на возможные угрозы.

## Требования

- Python 3.12.1
- PostgreSQL (установка: [PostgreSQL Official Docs](https://www.postgresql.org/download/))

## Запуск проекта доступен двух видов:

   1. Нативно по [инструкции](#инструкция-по-нативному-запуску-проекта)

   2. Через Docker контейнер по [инструкции](#запуск-через-docker-в-prod-режиме)


## Инструкция по нативному запуску проекта

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://https://github.com/mavinsplay/lambda-search.git
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
   cd lambda_search
   django-admin compilemessages
   ```

6. **Настройте PostgreSQL:**

   [Настройка для Windows](https://winitpro.ru/index.php/2019/10/25/ustanovka-nastrojka-postgresql-v-windows/)

   [Настройка для Linux](https://www.postgresql.org/docs/current/tutorial-install.html)


7. **Примените миграции:**

   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

8. **Запустите сервер:**

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

## Запуск через Docker в prod-режиме:

   1. Скачайте и установите [Docker](https://www.docker.com/)

   2. Настройте окружение

   3. Запустите контейнер, перед этим остановив существующие:

   ```bash
   docker compose down
   docker compose --profile prod up --build -d
   ```

## ER-диаграмма БД

![image info](ER.jpg)

