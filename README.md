# audio-discrimination-crowdsource

Web service to crowd-source audio discrimination data

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

## FSD50K preprocess

Preprocess FSD50k once, and upload as Digital Ocean space.
(Don't worry about this, the lead dev does this.)

Run this on your laptop or whatever:
```
cd batch/
wget https://mcdermottlab.mit.edu/Reverb/IRMAudio/Audio.zip
mkdir -p data/MIT-McDermott-ImpulseResponse/ && pushd data/MIT-McDermott-ImpulseResponse/ && unzip ../../Audio.zip && rm ../../Audio.zip && popd
./get_fsd50.py
./preprocess.py
find data/preprocessed/ -name \*.wav | xargs rm
```

[Generate API key](https://cloud.digitalocean.com/settings/api/tokens).
```
brew install s3cmd
s3cmd --configure
```
Follow these [s3cmd on Digital Ocean space
instructions](https://www.digitalocean.com/community/questions/how-to-manage-digitalocean-spaces-using-s3cmd).
```
s3cmd mb s3://fsd50k-preprocessed
#s3cmd sync data/preprocessed/ s3://fsd50k-preprocessed
s3cmd put -r data/preprocessed/FSD50K.* s3://fsd50k-preprocessed
# Or
#s3cmd sync data/preprocessed/FSD50K.* s3://fsd50k-preprocessed

# We might not need this
s3cmd setacl s3://fsd50k-preprocessed --acl-public --recursive
