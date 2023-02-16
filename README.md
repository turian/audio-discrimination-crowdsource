# audio-discrimination-crowdsource

Web service to crowd-source audio discrimination data.

Users are given instructions about the kind of audio they will be
listening to, and what kind of annotation they should make.

When they begin work, they are presented with a listening task.
They are presented with an MP3 to listen to (from an S3 endpoint
probably) in a JS audio player. Later we might switch to FLAC or
OGG (quality 10). They listen to the audio and must select a radio
box choosing their annotation.

For v1, they hear audio that is under 20 seconds long and is three
sounds. "AAB", "ABA", "BBA", or "BAB". They are asked to choose
whether the first and second sound are the same ("XXY"), or the
first and third sound are the same ("XYX").

10% of the time, they are given "gold" tasks so we know the right
answer. This allows us to discard the work of annotators that are
just clicking randomly.

After 15 minutes of work, the annotators are told to take a break
for an hour. This is so they don't get fatigued and start making
mistakes.

We want an admin interface to see the quality of the work each
annotator is doing. It should also track time worked, so annotators
can be paid properly. Lastly, it would be interesting to see how
long it takes before the quality of their work goes down, so we can
adjust the 15 minute time limit per session.

V2: We will want several different kinds of audio experiments, each
of which has a different name in the database. Each different audio
experiment will have:
* A different set of initial instructions.
* A different list of audio file S3 paths.
* (Possibly) more than one audio file to listen to, but we can also
do one audio file and add silence in between.
* A different set of radio options to choose between.
For example, in a second kind of audio experiment, they might listen
to two audio compression algorithms and pick the one with fewer
artifacts.

## Usage

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

# Deployment to Fly.io

## Install FlyCtl

To work with the Fly platform, you first need to install Flyctl, a command line interface that allows you to do everything from creating an account to deploy to Fly.
  - Linux:
    ```  
    curl  -L https://fly.io/install.sh | sh
    ```
  - OSX:
    ```
    brew install flyctl
    ```
  - Windows:
    ```
    iwr https://fly.io/install.ps1 -useb
    ```  
    Here is the [Installation Guilde](https://fly.io/docs/hands-on/install-flyctl/)


Next authenticate with your fly.io account:
  ```
  fly auth login
  ```

- To make sure everything is working well:    
  ```
  fly apps list
  ```
The output of the above command will be empty table since you have no apps launched yet


## Configure the Project

### Environment Variables

We shouldn't store secrets in source code, so utilizing environmental variables is needed.
- Run the following from the root of your project
  ```
 #!/usr/bin/env  python3 set_env.py
  ```

### Deploy App

In this step the app is going to be launched to fly.io.
- Create and configure the app  
  ```
  #!/usr/bin/env python3 fly_manager.py launch <app-name>
  
  ```
    
This command will create you an app on Fly.io , spin up a postgres instance, and create an app configuration named fly.toml in your project root. fly.toml file contains all app details.
  
Copy the DATABASE_URL from the termial output of the above process(fly launch)
and Update DATABASE_URL in .env file.

- To make sure the app is created successfully:
  ```
  fly apps list
  ```
  This command prints 3 apps: 
  1. your app
  2. database instance and 
  3. Fly builders: to build docker images
   


#### Deploy

- To deploy the app to the FLY platform.
  ```
  #!/usr/bin/env python3 fly_manager.py deploy <app-name>
  ```

- Open the app in browser

  ```  
  #!/usr/bin/env python3 fly_manager.py open <app-name>
  ```
