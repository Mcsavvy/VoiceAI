# ruff: noqa: E402

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
import os
import sys

import nltk
from melo.api import TTS

# TODO: Fix the import error
# from django.conf import settings
from app.settings import base as settings
from utils import download_file

nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("averaged_perceptron_tagger_eng")


if False:
    print("Downloading uniDic...")
    os.system(f"{sys.executable} -m unidic download")


if not os.path.exists(
    settings.OPENVOICE_V2_CHECKPOINT_PATH,
):
    print("Downloading OpenVoice V2 checkpoint...")
    zip_filename = settings.OPENVOICE_V2_CHECKPOINT_PATH + ".zip"
    download_file(
        settings.OPENVOICE_V2_CHECKPOINT_URL,
        zip_filename,
    )
    # unzip the checkpoint
    os.system(f"unzip {zip_filename} -d {settings.BASE_DIR}")
    os.remove(zip_filename)


print("Downloading TTS model...")
device = "auto"  # Will automatically use GPU if available
for language in ["EN", "ES", "FR", "ZH", "JP", "KR"]:
    print(f"Downloading {language} model...")
    model = TTS(language=language, device=device)
