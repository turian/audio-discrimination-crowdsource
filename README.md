# audio-discrimination-crowdsource

Web service to crowd-source audio discrimination data

## Getting Started

### Local dev

This is the one time setup:
```
mkdir .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

And this is how you run it locally:
```
source .venv/bin/activate
export DEVELOPMENT_MODE='local'
export GOOGLE_CLIENT_ID='<your_client_id>'
export GOOGLE_CLIENT_SECRET='<your_client_secret>'
python manage.py migrate
python manage.py createsuperuser
#python manage.py startapp polls
DEBUG=True python manage.py runserver
```
- Load `fixtures.json` according to [OAuth Setup](#OAuth-Setup).

### Digital Ocean apps

There is a production app and a staging app, set up separately.
The staging app builds and deploys when there are pushed to `main` branch.
The production app builds and deploys when there are pushed to
`prod` branch. (We only selectively merge `main` into `prod`.)

- Create Digital Ocean App
  - Service Provider: Github
  
  - Run command should be:
  ```
  $(pyenv which gunicorn) gunicorn --worker-tmp-dir /dev/shm django_app.wsgi
  ```
  (This is slightly wrong but appears to work.)
  - Use the bulk editor to set the values as follows. The last three
  values should be encrypted.
  ```
  DATABASE_URL=${db.DATABASE_URL}
  DJANGO_ALLOWED_HOSTS=${APP_DOMAIN}
  DEBUG=[False|True]
  DEVELOPMENT_MODE=['staging'|'production']
  DJANGO_SECRET_KEY=********************
  GOOGLE_CLIENT_ID=********************
  GOOGLE_CLIENT_SECRET=********************
  ```
  - $5.00/mo – Basic 512 MB RAM | 1 vCPU  x  1
- Create a free static site.
  - Add another app resource from the same github branch.
  - Edit the resource type to 'static site'.
  - HTTP route should be `/static`
  - Output directory should be `staticfiles`
- Create a dev postgres database for $7/mo.

- After the first build + deploy
  - Add domain name in app settings (should be the domain authorized
  for Google OAuth).

- Run `python manage.py migrate`
- Run `python manage.py createsuperuser`
- Load `fixtures.json` according to [OAuth Setup](#OAuth-Setup).

### OAuth Setup

One-time Google OAuth setup:
- Visit this link: [Google Api](https://console.cloud.google.com/apis/dashboard)
- Goto `OAuth consent screen` and setup
- Go to `Credentials` and click on `CREATE CREDENTIALS` > `OAuth client ID` choose options
    - for local:
        - set `Authorized JS origins` to `http://127.0.0.1:8000`
	    - set `Authorized redirect URIs` to
    	`http://127.0.0.1:8000/accounts/google/login/callback/` and
    	`http://localhost:8000/accounts/google/login/callback/`
    - for production:
        - set `Authorized JS origins` to `https://audiodiscrimination.com`
	    - set `Authorized redirect URIs` to
    	`https://audiodiscrimination.com/accounts/google/login/callback/`

- Copy `fixtures/allauth.json.tmpl` to `fixtures/allauth.json`
- Run `python manage.py loaddata fixtures/allauth.json` to load fixtures.


## Theme App

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
