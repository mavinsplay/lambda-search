FROM python:3.12.4-slim

RUN apt update
RUN apt install gettext -y

COPY ./requirements /requirements
RUN pip install -r requirements/dev.txt
RUN rm -rf requirements

COPY ./lambda_search /lambda_search/
WORKDIR /lambda_search

CMD python manage.py makemigrations \
 && python manage.py migrate \
 && python manage.py compilemessages \
 && python manage.py collectstatic --no-input \
 && gunicorn datanar.wsgi:application \
    --workers $(nproc) \
    --bind 0.0.0.0:8000 \
    --access-logfile /datanar/logs/gunicorn_access.log \
    --error-logfile /datanar/logs/gunicorn_error.log