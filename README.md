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
