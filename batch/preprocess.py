#!/usr/bin/env python3
"""
Preprocess the FSD50K corpus to MP3 (best for web.

For each file:
* Resample to mono, target SR
* For each audio length, randomly pad or trim
* Skip any audio that is almost all silence
"""

import glob
import json
import os.path
import random  # We don't seed, we just want something different every time

import librosa
import numpy as np
import resampy
import soundfile as sf
from tqdm.auto import tqdm

files = list(glob.glob("data/orig/FSD50K.dev_audio/*wav")) + list(
    glob.glob("data/orig/FSD50K.eval_audio/*wav")
)

CONFIG = json.loads(open("config.json").read())

LENGTH_SAMPLES = [
    (l, int(round(CONFIG["SAMPLE_RATE"] * l))) for l in CONFIG["AUDIO_LENGTHS"]
]


def ensure_length(x, length_in_samples, from_start=False):
    if len(x) < length_in_samples:
        npad = length_in_samples - len(x)
        if from_start:
            nstart = 0
        else:
            nstart = random.randint(0, npad)
        x = np.hstack([np.zeros(nstart), x, np.zeros(npad - nstart)])
    elif len(x) > length_in_samples:
        ntrim = len(x) - length_in_samples
        if from_start:
            nstart = 0
        else:
            nstart = random.randint(0, ntrim)
        x = x[nstart : nstart + length_in_samples]
    assert len(x) == length_in_samples
    return x


def preprocess_file(f):
    newf = f.replace("/orig/", "/preprocessed/")
    newd = os.path.split(newf)[0]
    if not os.path.exists(newd):
        os.makedirs(newd)

    # Skip files we have already done
    done = True
    for length, samples in LENGTH_SAMPLES:
        if not os.path.exists(f"{newf}-%.2f.{CONFIG['EXTENSION']}" % length):
            done = False
            break
    if done:
        return

    x, sr = sf.read(f)
    if len(x.shape) == 2:
        # Convert to mono
        x = np.mean(x, axis=1)
    # We use 48K since that is OpenL3's SR
    # TODO: Might be faster to use sox+ffmpeg?
    if sr != CONFIG["SAMPLE_RATE"]:
        print(f"Resampling {f}")
        x = resampy.resample(x, sr, CONFIG["SAMPLE_RATE"])
        sr = CONFIG["SAMPLE_RATE"]

    # Normalize audio to max peak BEFORE trimming.
    # Otherwise, low volume noise can become high volume!
    if np.max(np.abs(x)) == 0:
        # All silent :\
        return
    x /= np.max(np.abs(x))

    for length, samples in LENGTH_SAMPLES:
        # Try up to 100 times to find a snippet that is not too silent
        for i in range(100):
            xl = ensure_length(x, samples)
            rms = np.mean(librosa.feature.rms(xl))
            if rms < CONFIG["MIN_RMS"]:
                xl = None
            else:
                break
        if xl is not None:
            sf.write(newf + "-%.2f.wav" % length, xl, CONFIG["SAMPLE_RATE"])
            if CONFIG["EXTENSION"] == "mp3":
                # We could normalize here, but probably we don't want to
                # since it will change the RMS volume
                # lameenc is cooler but harder to use
                os.system(f"lame --quiet -V1 {newf}-%.2f.wav" % length)
            else:
                assert CONFIG["EXTENSION"] == "wav"
            assert os.path.exists(f"{newf}-%.2f.{CONFIG['EXTENSION']}" % length)


if __name__ == "__main__":
    for f in tqdm(files):
        preprocess_file(f)
