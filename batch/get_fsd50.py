#!/usr/bin/env python3
"""
Retrieve FSD50K.
"""

import os
import os.path

from tqdm.auto import tqdm

FILES = [
    "https://zenodo.org/record/4060432/files/FSD50K.dev_audio.zip",
    "https://zenodo.org/record/4060432/files/FSD50K.dev_audio.z01",
    "https://zenodo.org/record/4060432/files/FSD50K.dev_audio.z02",
    "https://zenodo.org/record/4060432/files/FSD50K.dev_audio.z03",
    "https://zenodo.org/record/4060432/files/FSD50K.dev_audio.z04",
    "https://zenodo.org/record/4060432/files/FSD50K.dev_audio.z05",
    "https://zenodo.org/record/4060432/files/FSD50K.eval_audio.zip",
    "https://zenodo.org/record/4060432/files/FSD50K.eval_audio.z01",
]


def get_fsd50k():
    if not os.path.exists("data"):
        os.makedirs("data/orig")
    if not os.path.exists("data/orig/"):
        os.makedirs("data/orig")
    for f in tqdm(FILES):
        os.system("cd data/orig/ && wget -c %s" % repr(f))
    # TODO: Check hashes
    os.system(
        "cd data/orig/ && zip -s 0 FSD50K.eval_audio.zip --out unsplit.zip && unzip unsplit.zip && rm unsplit.zip"
    )
    os.system(
        "cd data/orig/ && zip -s 0 FSD50K.dev_audio.zip --out unsplit.zip && unzip unsplit.zip && rm unsplit.zip"
    )


if __name__ == "__main__":
    get_fsd50k()
