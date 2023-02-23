ARG PYTHON_VERSION=3.10-slim-buster

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code
WORKDIR /code

COPY requirements.txt /tmp/requirements.txt

RUN set -ex && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

COPY . /code/

RUN python manage.py collectstatic --noinput

EXPOSE 8080

# replace demo.wsgi with <project_name>.wsgi
CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "django_app.wsgi"]
