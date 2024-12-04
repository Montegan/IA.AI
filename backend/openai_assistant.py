import os
import re
import time
import speech_recognition as sr
import torch
import string
import numpy as np
import queue
from openai import OpenAI
import whisper
import threading
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv

load_dotenv()


def voice_main(clicked):

    model = "tiny"
    english = True
    energy = 200
    pause = 0.8
    dynamic_energy = False
    wake_word = "hello"
    verbose = True

    if model != "large" and english:
        model = model + ".en"
    audio_model = whisper.load_model(model)
    audio_queue = queue.Queue()
    result_queue = queue.Queue()
    llm = OpenAI()

    global stop_event

    stop_event = threading.Event()

    if (clicked):
        if stop_event.is_set():
            stop_event.clear()
        else:
            stop_event.set()

    threading.Thread(target=record_audio, args=(
        audio_queue, energy, pause, dynamic_energy,)).start()
    threading.Thread(target=transcribe_forever, args=(
        audio_queue, result_queue, audio_model, english, wake_word, verbose,)).start()
    threading.Thread(target=reply, args=(result_queue, llm,)).start()

    while not stop_event.is_set():
        time.sleep(1)


def record_audio(audio_queue, energy, pause, dynamic_energy):
    r = sr.Recognizer()
    r.energy_threshold = energy
    r.pause_threshold = pause
    r.dynamic_energy_threshold = dynamic_energy
    if not stop_event.is_set():
        with sr.Microphone(sample_rate=16000) as source:
            print("Listening...")
            i = 0
            while not stop_event.is_set():
                audio = r.listen(source)
                torch_audio = torch.from_numpy(np.frombuffer(
                    audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0)  # type: ignore
                audio_data = torch_audio
                print(audio_data)
                audio_queue.put_nowait(audio_data)
                i += 1


def transcribe_forever(audio_queue, result_queue, audio_model, english, wake_word, verbose):
    while not stop_event.is_set():
        audio_data = audio_queue.get()
        if english:
            result = audio_model.transcribe(
                audio_data, language='english', fp16=False)
        else:
            result = audio_model.transcribe(audio_data, fp16=False)

        predicted_text = result["text"]

        if predicted_text.strip().lower().startswith(wake_word.strip().lower()):
            pattern = re.compile(re.escape(wake_word), re.IGNORECASE)
            predicted_text = pattern.sub("", predicted_text).strip()
            punc = string.punctuation
            predicted_text = predicted_text.translate(
                {ord(i): None for i in punc})
            if verbose:
                print("You said the wake word.. Processing {}...".format(
                    predicted_text))

            result_queue.put_nowait(predicted_text)
        else:
            if verbose:
                print("You did not say the wake word.. Ignoring")


def reply(result_queue, llm):
    while not stop_event.is_set():
        result = result_queue.get()
        print(result)
        data = llm.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "system", "content": "You are a helpfull voice assistant. your task is to prepare answers to user questions in a format that is easy to be read by a text to speech model. the response should feel like a natural conversations."}, {"role": "user", "content": result}], temperature=0, max_tokens=150)
        answer = data.choices[0].message.content
        mp3_obj = llm.audio.speech.create(
            model="tts-1", voice="alloy", input=answer)  # type: ignore
        mp3_obj.stream_to_file("reply.mp3")
        reply_audio = AudioSegment.from_mp3("reply.mp3")
        play(reply_audio)
        os.remove("reply.mp3")
