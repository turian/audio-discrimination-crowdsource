# audio-discrimination-crowdsource

Web service to crowd-source audio discrimination data.

## Motivation

Audio researchers need subjective evaluation of audio models. For
example, does this model or this model produce better sounding
speech?

This repo allows you to run listening experiments so that people
can say "audio A" is better than "audio B" and collect those
annotations.

## Approach

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

### Local Dev

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

### Database Population

There is a directory by the name ```fixtures``` in root project directory

It contains initial data for our app in ```initial_data.json``` file.

To load this data execute the following command:

```
python manage.py loaddata fixtures/initial_data.json
```

This will populate your database with the data inside ```initial_data.json```

### Deployment to fly.io

#### Install flyctl

To work with the fly platform, you first need to install flyctl, a command line interface that allows you to do everything from creating an account to deploy to fly.
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

(If interested, here is the [Installation Guide](https://fly.io/docs/hands-on/install-flyctl/))

- Once you're done with flyctl installation, add flyctl to path:
```
export FLYCTL_INSTALL="/home/$USER/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
```

- Next authenticate with your fly.io account if you already have one:
```
fly auth login
```
- If you do not have an existing fly.io account, authenticate using:
```
fly auth signup
```
- To make sure everything is working well:    
```
fly apps list
```
The output of the above command will be empty table since you have no apps launched yet

#### fly setup

So that different devs have diff app names, please set an environment
variable with a unique handle or username in lowercase alphabetic
characters:

NOTE: replace "{username}" with the name you like fly.io to use as your user name. e.g: export HANDLE=myname
```
export HANDLE={username}
```

For free, you can set up just a staging app with postgres. In that case, skip all commands below involving production.
If you want a staging AND production app, you will be billed by `fly.io`.

Now, use the follow commands to create a staging and production app:
```
export STAGING_APP_NAME=audio-discrimination-crowdsource-$HANDLE-staging
export PRODUCTION_APP_NAME=audio-discrimination-crowdsource-$HANDLE-production

flyctl launch --name $STAGING_APP_NAME --region iad --dockerfile Dockerfile --dockerignore-from-gitignore
flyctl launch --name $PRODUCTION_APP_NAME --region iad --dockerfile Dockerfile --dockerignore-from-gitignore
```
and answer the questions as follows:
```
Would you like to set up a Postgresql database now? Yes
Select configuration: Development - Single node, 1x shared CPU, 256MB RAM, 1GB disk
Would you like to set up an Upstash Redis database now? No
Would you like to deploy now? No
```

Remove the created `fly.toml` and use the repo's toml configs:
```
rm fly.toml
sed "s/HANDLE/$HANDLE/g" fly-staging.toml.tmpl > fly-staging.toml
sed "s/HANDLE/$HANDLE/g" fly-production.toml.tmpl > fly-production.toml
```

Create a random secret key for your Django apps:
```
flyctl secrets set --app $STAGING_APP_NAME SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
flyctl secrets set --app $PRODUCTION_APP_NAME SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
```

### fly deployment

This will do all migrations:

Staging:
```
fly deploy -c fly-staging.toml --app $STAGING_APP_NAME
```

Production:
```
fly deploy -c fly-production.toml --app $PRODUCTION_APP_NAME
```

If you get an error like this:
```
	 django.db.utils.OperationalError: could not translate host name "top2.nearest.of.audio-discrimination-crowdsource-HANDLE-staging-db.internal" to address: Name or service not known
	 Starting clean up.
```
Then change your secrets, for example:
```
flyctl secrets set --app $STAGING_APP_NAME DATABASE_URL="what you saved in db.txt"
```

- Finally, open the app in a browser:

```  
flyctl open --app $STAGING_APP_NAME
flyctl open --app $PRODUCTION_APP_NAME
```

### Messed up, start over

If you mess up and want to delete EVERY SINGLE fly.io app of yours and try again:
```
./delete-all-fly-apps.py
```

### Manual app creation

This is a little nicer, but sometimes doesn't work. So just follow the instructions above:

```
fly apps create --name $STAGING_APP_NAME --network iad
fly apps create --name $PRODUCTION_APP_NAME --network iad
```

Set-up postgres:
```
flyctl postgres create -n $STAGING_APP_NAME-db -r iad
flyctl postgres create -n $PRODUCTION_APP_NAME-db -r iad
```

Towards the end it will tell you your postgres credentials.
*IMPORTANT*: Copy-and-paste this information into `db.txt`, which
is `.gitignore`'d.

Attach postgres to your apps:
```
flyctl postgres attach --app $STAGING_APP_NAME --config fly-staging.toml $STAGING_APP_NAME-db
flyctl postgres attach --app $PRODUCTION_APP_NAME --config fly-production.toml $PRODUCTION_APP_NAME-db
```

### Digital Ocean apps

DEPRECATED. We are going to use fly.io

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
