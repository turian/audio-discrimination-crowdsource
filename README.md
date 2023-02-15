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


Install FlyCtl

To work with the Fly platform, you first need to install Flyctl, a command line interface that allows tou to do everything from creating an account to deploy to Fly.

- To install it on Linux
    RUN `curl  -L https:fly.io/install.sh | sh`

- To install it on windows
    Run `iwr https://fly.io/install.ps1 -useb` from windows powershell

  # visit `https://fly.io/` if you need installation guide
  

Next authenticate with your fly.io account:
   Run `fly auth login`
   # in case you don't have an account yet: goto fly.io and signup


To make sure everything is working well:
  Run `fly apps list`
  # the output of the above command will be empty table since you have no apps launched yet


Configure the Project

  Environment Variables

  We shouldn't store secrets in source code, so utilizing environmental variables is needed.

  a. Generate SECRET_KEY 
      # Run the following from the root of your project
      Run `python generate_key.py`
      # Get your key and update in .env file SECRET_KEY='<your-key>'

Deploy App

In this step the app is going to be launched to fly.io.
  
  To create and configure new app
  # It will ask for app name, region annd if you need Postgresql database 
    - Run `fly launch`
  Notes: 
    1. write custom app name or leave it blank to get random name
    2. Choose the region for deployment: Closest to you
    3. Say 'Yes' for the question Would you like to setup Postgresql database now
    4. Database configuration: Development
    5. would like to deploy now: NO  # some other configurations are not done yet  
  
  This command will create you an app on Fly.io , spin up a postgres instance, and create an app configuration named fly.toml in your project root.

  To make sure the app is created successfully:
   # This command prints 3 apps: 
   # 1. your app, 
   # 2. database instance and 
   # 3. Fly builders: to build docker images

   Run `fly apps list`

Secrets

- Set the secrets  that you used in settings.py
      
    - Run `fly secrets set DEBUG="1"`
    - Run `fly secrets set SECRET_KEY="<your-key>"`
    - Run `fly secrets set ALLOWED_HOSTS="localhost 127.0.0.1 [::1 <your_app_hostname>"` # the last parameter is app name which you got from fly launch
    - Run `fly secrets set CSRF_TRUSTED_ORIGINS="https://<your_app_hostname>"`
    
    Or Simply sectets can be loaded from .env 
    - Run `flyctl secrets import -a audio-discrimination-croudsource-dev .env`  # it will import secrets from .env file/

Deploy

To deploy the app ti the FLY platform 
  - Run `fly deploy`

This command will use the Fly builder to build the Docker image , push it to the container registery and use it to deploy your application.


Everything looks great. Make sure the app works by opening browser:
  - Run `fly open`
  # this will open the app in browser with it's host name

Usefull Fly commands
  
    ```
      fly apps list # to see list of apps
      fly status # to check the status of the app
      fly launch # to launch the app to fly.io
      fly logs # to watch for logs
      flyctl auth login # to login to fly.io via ctl
      fly deploy # deploy the app
    ```


