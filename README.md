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
export GOOGLE_CLIENT_ID='<your_client_id>'
export GOOGLE_CLIENT_SECRET='<your_client_secret>'
python manage.py migrate

#python manage.py startapp polls
DEBUG=True python manage.py runserver
```

### Running in Production
- Set environment variables `DEVELOPMENT_MODE`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `DEBUG`, `SECRET_KEY` & `DJANGO_ALLOWED_HOSTS`
- Run `python manage.py migrate`
- Load `fixtures` according to [these](#Common-for-all-environments) instructions

### Common for all environments
- Get your Google OAuth2 keys following [this](#Google-auth-keys) method
- Copy `fixtures/allauth.json.tmpl` to `fixtures/allauth.json`
- In `fixtures/allauth.json`:
    - For `DEVELOPMENT_MODE = True` if not using `127.0.0.1:8000` then replace `127.0.0.1:8000` with your domain.
    - Set `client_id` to *Client ID* and `secret` to *Client secret* from google OAuth2 credentials.
- Run `python manage.py loaddata fixtures/allauth.json` to load fixtures.


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

### Google auth keys:
- Visit this link : [Google Api](https://console.cloud.google.com/apis/dashboard)
- Goto `OAuth consent screen` and setup
- Go to `Credentials` and click on `CREATE CREDENTIALS` > `OAuth client ID` choose options
    - for local:
        - set `Authorized JS orignins` to `http://127.0.0.1:8000`
        - set `Authorized redirect URIs` to `http://127.0.0.1:8000/accounts/google/login/callback/` and `http://localhost:8000/accounts/google/login/callback/`
    - for production:
        - set `Authorized JS orignins` to `https://audiodiscrimination.com`
        - set `Authorized redirect URIs` to `https://audiodiscrimination.com/accounts/google/login/callback/`