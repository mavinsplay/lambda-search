# Lambda-search project

## Как запустить проект

### Требования

Наличие [python](https://www.python.org/) >= 3.9

1. Скопируйте проект в нужную папку при помощи команды:

```bash
    git clone https://gitlab.crja72.ru/django/2024/autumn/course/students/182732-mavinsplay2007-course-1187
```

    (на вашем пк должен быть установлен git, [подробнее](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git))

1. Создайте виртуальное окружение
 | Для windows / linux / macos

    откройте папку со скаченным репозиторием

    создайте виртуальное окружение,
    пропишите в командную строку:

    ```bash
    python3 -m venv venv
    ```

    активируйте виртуальное окружение,
    пропишите в командную строку:

    Для windows

    ```bash
    venv\Scripts\activate
    ```

    Для linux и macos

    ```bash
    source venv/bin/activate
    ```

1. Добавьте переменные окружения,
пропишите в командную строку:
для linux:

    ```bash
    cp .env.example .env
    ```

    для windows:

    ```bash
    copy .env.example .env
    ```

    измените нужные вам параметры в файле .env
    согласно комментариям-подсказкам

1. Скачайте нужные зависимости
    пропишите в командную строку:

```bash
    pip3 install -r requirements/prod.txt
```

    (Для запуска в проде) или

```bash
    pip3 install -r requirements/dev.txt
```

    (для запуска в dev режиме)

1. Запустите проект.
    пропишите в командную строку:

```bash
    cd lambda_search
    python manage.py runserver
```

1. Создать фикстуру можно командой

```bash
    python -Xutf8 manage.py dumpdata catalog > fixtures/data.json --indent 4
```

    применить фикстуру можно командой:

```bash
    python manage.py loaddata fixtures/data.json
```

1. Локализация проекта

    1. Добавьте поддержку языков в settings.py перечислив желаемые языки в параметре LANGUAGE. Этот файл находится в каталоге lambda_search/lambda_search/settings.py. Пример:

```python
            LANGUAGES = [
            ("en", _("English")),
            ("ru", _("Russian")),
            ]
```

    1. Сгенерируйте файлы сообщений переводов, сделать это можно командой:

        ```bash
            django-admin makemessages -l ru -l en
        ```

        (через [-l "язык"] указываются нужные вам языки, которые вы указали ранее в settings.py)

    1. Заполните переводы в файлах locale/ru/ LC_MESSAGES/django.pо и locale/en/LC_MESSAGES/_ django.po (файлы могут различаться, смотрите на язык в каталогах), сделать это можно примерно так:

         ```bash
            #: .\lambda_search\settings.py:268
            msgid "Russian"
            msgstr "Russian"

            #: .\templates\includes\header.html:15 .\templates\includes\header.html:17
            msgid "На главную"
            msgstr "Homepage"

            #: .\templates\includes\header.html:22 .\templates\includes\header.html:24
            msgid "О проекте"
            msgstr "About"

            #: .\templates\includes\header.html:29 .\templates\includes\header.html:31
            msgid "Список товаров"
            msgstr "Item list"
        ```

    1. Скомпилируйте сообщения при помощи команды:

        ```bash
            django-admin compilemessages
        ```

1. Проведение миграций, после изменения моделей

    Если вы изменили модель в каком-то из файлов, то необходимо провести миграции командами:

    ```bash
        python manage.py makemigrations
        python manage.py migrate
    ```

1. Тестирование приложения

    Если после изменения кода вы хотите протестировать приложение, то измените нужные вам тесты в файлах с именем test*.py и воспользуйтесь командой:

    ```bash
        python manage.py test
    ```

1. Сбор статики

    Чтобы собрать статику необходимо воспользоваться командой:

    ```bash
        python manage.py collectstatic
    ```

1. Создание суперпользователя

    Чтобы создать пользователя с правами администратора необходимо воспользоваться командой:

    ```bash
        python3 manage.py createsuperuser
    ```

    следуйте указанным инструкциям в подсказках, указанных в терминале
1. Уменьшение количества миграций

    Чтобы уменьшить количество миграций нужно прописать в командной строке следующие:

    ```bash
        python manage.py squashmigrations <appname> <squashfrom> <squashto>
    ```

    appname - Имя приложения
    squashfrom - Первая миграция
    squashto - Последняяя миграция

ER диаграмма базы данных:
![image](ER.jpg)
