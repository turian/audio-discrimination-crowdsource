# FSD50K preprocess

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

