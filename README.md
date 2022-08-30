# audio-discrimination-crowdsource

Web service to crowd-source audio discrimination data

## Digital Ocean apps

We deploy on Digital Ocean apps. Please [set one
up](https://docs.digitalocean.com/tutorials/app-deploy-django-app/), so
you test pushing stuff to production.

## Local dev

Based upon https://docs.digitalocean.com/tutorials/app-deploy-django-app/

### Getting started

```
mkdir .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

### Running locally

```
source .venv/bin/activate
export DEVELOPMENT_MODE=True
#python manage.py startapp polls
DEBUG=True python manage.py runserver
```

- Create a `.env` file in base directory and place secret keys related to google auth there.

### Theme App

Theme app is a django app consisting of the main theme of the application.
This can be reused in other applications as well.

To use the themeapp in the application, following things need to be done:

In settings.py, make sure static settings is configured

```
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 
    "assets",
]
```

All assets of the theme needs to keep inside assets folder

Now, for any new html page, we need to do the following:

```
{% extends 'base.html' %}
{% load static %}

{% block css-block%}
// any extra css here
{% endblock %}

{% block body-block%}
// Main Content of the page here
{% endblock %}

{% block js-block%}
// any extra js here
{% endblock %}

```
