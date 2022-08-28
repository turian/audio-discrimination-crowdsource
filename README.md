# audio-discrimination-crowdsource

Web service to crowd-source audio discrimination data

## Local dev

Based upon https://docs.digitalocean.com/tutorials/app-deploy-django-app/

### Getting started

```
mkdir .venv
python3 -m venv .venv
source .venv/bin/activate
pip install django gunicorn psycopg2-binary dj-database-url
```

### Running locally

```
export DEVELOPMENT_MODE=True
#python manage.py startapp polls
```

## FSD50K preprocess

Preprocess FSD50k once, and upload as Digital Ocean space.

Run this on your laptop or whatever:
```
cd batch/
wget https://mcdermottlab.mit.edu/Reverb/IRMAudio/Audio.zip
mkdir -p data/MIT-McDermott-ImpulseResponse/ && pushd data/MIT-McDermott-ImpulseResponse/ && unzip ../../Audio.zip && rm ../../Audio.zip && popd
./get_fsd50.py
./preprocess.py
```
