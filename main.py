import os
import threading
import time as t
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Progressbar

import pandas as pd
import sounddevice as sd
import torch
import torchaudio
import whisper
from silero_vad import load_silero_vad, get_speech_timestamps


from data.Preferences import Preferences
from util.Audio import AudioSetup as auinit
from util.Audio import AudioUtil
from util.DataFrame import DataFrameUtility as data
from util.DataFrame import DataBrowser as browser


mic_options = auinit.mic_setup()
au = AudioUtil()
prefs = Preferences()
vad_model = load_silero_vad()

sample_rate, channels = prefs.sample_rate, prefs.channels

isrunning = False


def audio_callback(indata, frames, time, status):
    audio_torch = torch.from_numpy(indata[:, 0].copy()).float()  # Audio as array
    speech_timestamps = get_speech_timestamps(audio_torch, vad_model, sampling_rate=sample_rate)

    if not au.active:  # Case where stop button is pressed
        if au.buffer is not None:
            file = (os.getcwd() + "/data/clips/" + str(prefs.clip_index) + ".wav")
            if channels == 1:
                torchaudio.save(file, au.buffer.unsqueeze(0), sample_rate)
            else:
                torchaudio.save(file, au.buffer, sample_rate)

    if speech_timestamps:
        if au.buffer is not None:
            au.set_buffer(torch.cat([au.buffer, audio_torch], dim=0))
        else:
            au.set_buffer(audio_torch)
    else:
        if au.buffer is not None:
            file = (os.getcwd() + "/data/clips/" + str(prefs.clip_index) + ".wav")
            if channels == 1:
                torchaudio.save(file, au.buffer.unsqueeze(0), sample_rate)
            else:
                torchaudio.save(file, au.buffer, sample_rate)

            data.add_entry(au.get_length(),False, "", file)
            prefs.increment_clip_index()
            au.set_buffer(None)


def start():
    au.activate()

    sleep_window = Toplevel(r)
    sleep_window.title("Sleeping...")
    sleep_window.geometry("200x50")
    Label(sleep_window, text="Sleeping for " + str(prefs.sleep_time / 1000 / 60) + " minutes...").pack()

    def run_recording():
        sleep_window.destroy()

        def rec_loop():
            with sd.InputStream(samplerate=sample_rate, channels=channels,
                                blocksize=au.chunk_size, callback=audio_callback):
                print("Listening... press Stop to end")
                while isrunning:
                    t.sleep(0.1)

        threading.Thread(target=rec_loop, daemon=True).start()

    sleep_window.after(prefs.sleep_time, run_recording)


def stop():
    au.deactivate()


def options():
    options_dialog = Toplevel(r)
    options_dialog.geometry("250x400")
    options_dialog.title("Options")

    mic_dialog = []
    mic_options = auinit.mic_setup()
    for item in mic_options:
        mic_dialog.append("Sample Rate: " + str(item[0]) + " ; Channels: " + str(item[1]))

    # Microphones drop-down
    mic_opt = StringVar(
        value=("Sample Rate: " + str(prefs.sample_rate) + " ; Channels: " + str(prefs.channels)))
    Label(options_dialog, text="Microphone Settings:").pack(anchor="w", padx=10, pady=(10, 0))
    OptionMenu(options_dialog, mic_opt, *mic_dialog).pack()

    models = prefs.get_models()
    languages = prefs.get_langs()

    # Transcription models drop-down
    trans_opt = StringVar(value=prefs.transcript_model)
    Label(options_dialog, text="Transcription Model:").pack(anchor="w", padx=10, pady=(10, 0))
    OptionMenu(options_dialog, trans_opt, *models).pack()

    # Transcription model language drop-down
    trans_lang_opt = StringVar(value=prefs.transcript_lang)
    Label(options_dialog, text="Transcription Language:").pack(anchor="w", padx=10, pady=(10, 0))
    OptionMenu(options_dialog, trans_lang_opt, *languages).pack()

    # Sleep time dialog
    Label(options_dialog, text="Sleep Time (Mins):").pack(anchor="w", padx=10, pady=(10, 0))
    sleep_time_var = StringVar(value=str(prefs.sleep_time / (1000 * 60)))
    sleep_entry = Entry(options_dialog, textvariable=sleep_time_var, validate="key")
    sleep_entry.pack(padx=10, pady=(0, 10))

    # Check we receive a positive integer for sleep time
    def validate_int(new_value):
        return new_value.isdigit() or new_value == ""

    vcmd = (options_dialog.register(validate_int), "%P")
    sleep_entry.config(validatecommand=vcmd)

    def apply_options():
        prefs.set_transcript_model(trans_opt.get())
        prefs.set_transcript_lang(trans_lang_opt.get())
        prefs.set_sleep_time(
            (int(sleep_time_var.get()) * 60000) if sleep_time_var.get().isdigit() else prefs.sleep_time)

        mic_qual = mic_options[mic_dialog.index(mic_opt.get())]
        prefs.set_sample_rate(mic_qual[0])
        prefs.set_channels(mic_qual[1])

        prefs.save_prefs()
        options_dialog.destroy()

    bottom = Frame(options_dialog)
    bottom.pack(side=BOTTOM, fill=BOTH, expand=True)
    Button(options_dialog, text="Save", command=apply_options).pack(pady=10, in_=bottom)
    Button(options_dialog, text="Cancel", command=options_dialog.destroy).pack(pady=10, in_=bottom)


def dataview():
    browser(r, pd.read_parquet('dataframe.parquet'))


def transcribe():
    transcribe_options = Toplevel(r)
    transcribe_options.geometry("250x250")
    transcribe_options.title("Options")

    models = prefs.get_models()
    langs = prefs.get_langs()

    trans_opt = StringVar(value=prefs.transcript_model)
    Label(transcribe_options, text="Transcription Model:").pack(anchor="w", padx=10, pady=(10, 0))
    OptionMenu(transcribe_options, trans_opt, *models).pack()

    trans_lang_opt = StringVar(value=prefs.transcript_lang)
    Label(transcribe_options, text="Transcription Language:").pack(anchor="w", padx=10, pady=(10, 0))
    OptionMenu(transcribe_options, trans_lang_opt, *langs).pack()

    bottom = Frame(transcribe_options)

    def run_transcribe():
        global sr_model
        if trans_opt.get() == "None Selected":
            no_model = Toplevel(transcribe_options)

            bottom = Frame(no_model)
            bottom.pack(side=BOTTOM, fill=BOTH, expand=True)

            no_model.geometry("250x250")
            no_model.title("Please select a transcription model!")

            Label(no_model, text="Please select a transcription model!").pack()
            Button(no_model, text="OK", command=no_model.destroy).pack(pady=10, in_=bottom)
        else:
            transcribing = Toplevel(transcribe_options)
            transcribing.geometry("250x250")
            transcribing.title("Loading transcription model...")

            sr_model = whisper.load_model(trans_opt.get())
            transcribing.destroy()

            to_transcribe = data.get_untranscribed_files()

            if (to_transcribe):

                progress_fraction = 100 // len(to_transcribe)
                transcribing_progress = Toplevel(transcribe_options)
                transcribing_progress.geometry("250x250")
                transcribing_progress.title("Transcribing...")
                progress = Progressbar(transcribing_progress, orient=HORIZONTAL,
                                       length=200, mode='determinate')
                progress.pack(pady=10)
                progress['value'] = 0
                for audio in to_transcribe:
                    result = sr_model.transcribe(audio, language=trans_lang_opt.get())
                    data.add_transcript(result["text"])
                    progress['value'] = progress['value'] + progress_fraction
                transcribing_progress.destroy()

    bottom.pack(side=BOTTOM, fill=BOTH, expand=True)
    Button(transcribe_options, text="Transcribe", command=run_transcribe).pack(pady=10, in_=bottom)
    Button(transcribe_options, text="Cancel", command=transcribe_options.destroy).pack(pady=10, in_=bottom)


r = Tk()
r.title('Somniloquy')
r.geometry("150x125")
start_button = ttk.Button(r, text='Start', width=25, command=start).pack()
stop_button = ttk.Button(r, text='Stop', width=25, command=stop).pack()
options_button = ttk.Button(r, text='Options', width=25, command=options).pack()
dataview_button = ttk.Button(r, text='Browse Clips', width=25, command=dataview).pack()
transcribe_button = ttk.Button(r, text='Transcribe', width=25, command=transcribe).pack()

r.mainloop()
