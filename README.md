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
- Run `python manage.py loaddata fixtures/allauth.json` to load fixtures.

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

## pre deployment to fly.io


- Setting Up environmental variables

  - Add `python-dotenv>=0.21.0` to requirements.txt
  - Run `pip install -r requirements.txt`

  -  create new .env file
      add the following informations in it
          SECRET_KEY
          DATABASE_URL
          DEBUG

      NB for Secret key generate random variable of length 60
      ```
       import secrets
       import string
       ''.join(secrets.choice(string.printable) for i in range(60))
       # random string will be generated and used as secret key for the app
      ```

There are some options to deploy apps to servers/fly.io. from those options docker is the one and good option to deploy with proper environment and it's easy to update and scalable
- Doeckerization
  * To dockerize the app the following 2 files will be created on the root of the project
   - create Docker file
   - create .dockerignore

 - launch to fly.io with appname, region and postgress configuration


Useful fly commands
  
    ```
      fly apps list # to see list of apps
      fly status # to check the status of the app
      fly launch # to launch the app to fly.io
      fly logs # to watch for logs
      flyctl auth login # to login to fly.io via ctl
    
    ```

Secrets

- set the secrets  that we need
      ```
        fly secrets set DEBUG="1"
        fly secrets set SECRET_KEY=""
        fly secrets set ALLOWED_HOSTS="localhost 127.0.0.1 [::1 audio-discrimination-croudsource-dev"
        fly secrets set CSRF_TRUSTED_ORIGINS="https://audio-discrimination-croudsource-dev"
      ```
    Or 
      Simply sectets can be loaded from .env 
      - RUN "flyctl secrets import -a audio-discrimination-croudsource-dev .env"  # it will import secrets from .env file/
        






