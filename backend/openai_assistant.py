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
from langchain_core.prompts import ChatPromptTemplate
from chromadab import pdf_embed_documents, web_embed_documents, youtube_embed_documents, vector_store, docs_embed_documents, powerpoint_embed_documets, excel_embed_documents, csv_embed_documents, text_embed_documents
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
from langchain_openai import ChatOpenAI

from Moderations import anti_promptInjection

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


def rag_endpoint(question):
    # print(language)
    response = anti_promptInjection(question)
    client = ChatOpenAI()
    if response == "N":
        try:
            system_prompt = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. give detailed answer.If you don't know the answer,just say you don't know in a respectfull manner.
            Context: {context}
            Answer:"""

            main_prompt = ChatPromptTemplate.from_messages(
                [("system", system_prompt), ("user", "{question}")])
            retriver = vector_store.as_retriever(search_kwargs={"k": 4})
            string_parser = StrOutputParser()

            main_chain = {"context": itemgetter("question") | retriver,
                          "question": itemgetter("question")} | main_prompt | client

            answer = main_chain.invoke(
                {"question": question})

            ai_message = answer.content
            # ['choices'][0]['message']['content'].strip()
            # ai_message = answer
            # send_ref = db.collection("users", currentuser,
            #                          "tab_id", currentTab, "messages").document()
            # data = {
            #     "userId": currentuser,
            #     "ai_message": ai_message,
            #     "created_at": firestore.SERVER_TIMESTAMP,  # type: ignore
            # }
            # send_ref.set(data)
            return ai_message
        except:
            return f"OpenAI API limit!"
    elif response == "Y":
        ai_message = "Your input contains potentially malicious content and cannot be processed. Please ensure your input follows safe and appropriate guidelines. If you believe this is an error, please revise your input and try again."
        return ai_message
        # ['choices'][0]['message']['content'].strip()
        # ai_message = answer
        # send_ref = db.collection("users", currentuser,
        #                          "tab_id", currentTab, "messages").document()
        # data = {
        #     "userId": currentuser,
        #     "ai_message": ai_message,
        #     "created_at": firestore.SERVER_TIMESTAMP,  # type: ignore
        # }
        # send_ref.set(data)
        # return send_ref.id


def reply(result_queue, llm):
    while not stop_event.is_set():
        result = result_queue.get()
        print(result)
        # data = llm.chat.completions.create(
        #     model="gpt-4o-mini", messages=[{"role": "system", "content": "You are a helpfull voice assistant. your task is to prepare answers to user questions in a format that is easy to be read by a text to speech model. the response should feel like a natural conversations."}, {"role": "user", "content": result}], temperature=0, max_tokens=150)
        # answer = data.choices[0].message.content
        answer = rag_endpoint(result)
        mp3_obj = llm.audio.speech.create(
            model="tts-1", voice="alloy", input=answer)  # type: ignore
        mp3_obj.stream_to_file("reply.mp3")
        reply_audio = AudioSegment.from_mp3("reply.mp3")
        play(reply_audio)
        os.remove("reply.mp3")
