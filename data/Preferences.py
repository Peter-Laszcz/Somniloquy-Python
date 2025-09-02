import json
import os
from util.Audio import AudioSetup as audio
from util.DataFrame import DataFrameUtility as data


class Preferences:
    def __init__(self):
        data.setup()
        if os.path.isfile("preferences.json"):
            with open("preferences.json", "r") as f:
                preferences = json.load(f)
                self.sample_rate = int(preferences["sample_rate"])
                self.channels = int(preferences["channels"])
                self.sleep_time = int(preferences["sleep_time"])
                self.clip_index = int(preferences["clip_index"])
                self.transcript_model = preferences["transcript_model"]
                self.transcript_lang = preferences["transcript_lang"]
        else:
            self.sample_rate = audio.mic_setup()[0][0]
            self.channels = audio.mic_setup()[0][1]
            self.sleep_time = 1800000
            self.transcript_model = "None Selected"
            self.transcript_lang = "en"
            self.clip_index = 0
            self.first_time_preferences = {
                "sample_rate": self.sample_rate,
                "channels": self.channels,
                "sleep_time": self.sleep_time,
                "transcript_model": self.transcript_model,
                "transcript_lang": self.transcript_lang,
                "clip_index": self.clip_index,
            }

            with open(os.path.join("data", "preferences.json"), "w") as f:
                json.dump(self.first_time_preferences, f)


        self.supported_langs = ['en', 'zh', 'de', 'es', 'ru', 'ko', 'fr', 'ja', 'pt', 'tr', 'pl', 'ca', 'nl', 'ar', 'sv',
                              'it', 'id', 'hi', 'fi', 'vi', 'he', 'uk', 'el', 'ms', 'cs', 'ro', 'da', 'hu', 'ta', 'no',
                              'th', 'ur', 'hr', 'bg', 'lt', 'la', 'mi', 'ml', 'cy', 'sk', 'te', 'fa', 'lv', 'bn', 'sr',
                              'az', 'sl', 'kn', 'et', 'mk', 'br', 'eu', 'is', 'hy', 'ne', 'mn', 'bs', 'kk', 'sq', 'sw',
                              'gl', 'mr', 'pa', 'si', 'km', 'sn', 'yo', 'so', 'af', 'oc', 'ka', 'be', 'tg', 'sd', 'gu',
                              'am', 'yi', 'lo', 'uz', 'fo', 'ht', 'ps', 'tk', 'nn', 'mt', 'sa', 'lb', 'my', 'bo', 'tl',
                              'mg', 'as', 'tt', 'haw', 'ln', 'ha', 'ba', 'jw', 'su', 'yue']
        self.supported_models = ["None Selected", "tiny", "base", "small", "medium", "large", "turbo"]

    def save_prefs(self):
        with open("preferences.json", "w") as f:
            json.dump({
                "sample_rate": str(self.sample_rate),
                "channels": str(self.channels),
                "sleep_time": str(self.sleep_time),
                "clip_index": str(self.clip_index),
                "transcript_model": self.transcript_model,
                "transcript_lang": self.transcript_lang
            }, f)

    def get_langs(self):
        return self.supported_langs
    def get_models(self):
        return self.supported_models
    def increment_clip_index(self):
        self.clip_index += 1
        self.save_prefs()

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
    def set_channels(self, channels):
        self.channels = channels
    def set_sleep_time(self, sleep_time):
        self.sleep_time = sleep_time
    def set_transcript_model(self, model):
        self.transcript_model = model
    def set_transcript_lang(self, lang):
        self.transcript_lang = lang





class WorkingPrefs:
    def __init__(self, wdir, isRunning):
        self.wdir = wdir
        self.isRunning = isRunning
