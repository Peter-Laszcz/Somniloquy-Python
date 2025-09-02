from contextlib import suppress
import sounddevice as sd
import torch


class AudioSetup:
    @staticmethod
    def mic_setup():
        filename = "mic_options.json"
        profiles = []
        rates = [192000, 128000, 96000, 48000, 44100, 32000, 16000, 8000]

        for rate in rates:
            with suppress(Exception):
                sd.check_output_settings(device=sd.default.device, samplerate=rate)
                for ch in (1, 2):
                    try:
                        with sd.InputStream(samplerate=rate, channels=ch):
                            profiles.append([rate, ch])
                            break
                    except Exception:
                        continue
        return profiles

class AudioUtil:
    def __init__(self):
        import data.Preferences
        prefs = data.Preferences.Preferences()

        self.chunk_duration = 5
        self.chunk_size = int(prefs.sample_rate * self.chunk_duration)
        self.buffer = torch.tensor([], dtype=torch.float32)
        self.active = False
        self.sample_rate = prefs.sample_rate
    def set_buffer(self, buffer):
        self.buffer = buffer
    def activate(self):
        self.active = True
    def deactivate(self):
        self.active = False
    def get_length(self):
        return self.buffer.shape[-1]/self.sample_rate