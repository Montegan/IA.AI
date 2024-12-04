from firebase_admin import credentials
import firebase_admin
from firebase_admin import firestore
import os
import requests
import torch
import numpy as np
import re
import queue
import threading
from flask import Flask, request, jsonify, render_template, session
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
from dotenv import load_dotenv
import whisper
import openai
from operator import itemgetter

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
import warnings
from flask_cors import CORS
from openai_assistant import voice_main
from chromadab import pdf_embed_documents, web_embed_documents, youtube_embed_documents, vector_store

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Load API key from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI()
app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey'  # For session management
app.config['UPLOAD_FOLDER'] = 'uploads/'

openai.api_key = OPENAI_API_KEY

# firebase credentials
cred = credentials.Certificate(
    "C:\\Users\\H00422003\\Desktop\\SFBU\\2ndsem\\GenAI\\firebase_config_keys.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# Queues for handling audio and results
audio_queue = queue.Queue()
verbose = True
wake_word = "hey computer"

# Initialize chat history
chat_history = []
qa = None  # Initialized after document is loaded

# Load Whisper model
audio_model = whisper.load_model("base")

# Function to load and process the PDF document


# def load_db(file_path, chain_type="stuff", k=4):
#     loader = PyPDFLoader(file_path)
#     documents = loader.load()
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000, chunk_overlap=150)
#     docs = text_splitter.split_documents(documents)
#     embeddings = OpenAIEmbeddings()
#     llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
#     db = DocArrayInMemorySearch.from_documents(docs, embeddings)
#     retriever = db.as_retriever(
#         search_type="similarity", search_kwargs={"k": k})

#     global qa
#     qa = ConversationalRetrievalChain.from_llm(
#         llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
#         chain_type=chain_type,
#         retriever=retriever,
#         return_source_documents=True,
#         return_generated_question=True,
#     )

# Function to interact with OpenAI API


@app.route("/ragEndpoint", methods=['POST'])
def ask_chatgpt():
    data = request.get_json()  # Parse JSON data
    question = data.get("prompt")  # Extract the "prompt" key
    currentuser = data.get("currentuser")
    currentTab = data.get("currentTab")
    language = data.get("language")
    message = rag_endpoint(question, currentuser, currentTab, language)
    return jsonify({"message": message})
    # data = request.get_json()  # Parse JSON data
    # prompt = data.get("prompt")  # Extract the "prompt" key
    # currentuser = data.get("currentuser")
    # currentTab = data.get("currentTab")
    # headers = {
    #     'Content-Type': 'application/json',
    #     'Authorization': f'Bearer {OPENAI_API_KEY}',
    # }

    # payload = {
    #     "model": "gpt-3.5-turbo",
    #     "messages": [{"role": "user", "content": prompt}],
    #     "max_tokens": 300,
    #     "temperature": 0.7,
    # }

    # const send_ref = collection(
    #   db,
    #   "users",
    #   currentuser,
    #   "tab_id",
    #   currentTab,
    #   "messages"
    # );
    # addDoc(send_ref, {
    #   userId: currentuser,
    #   human_message: userInput,
    #   created_at: serverTimestamp(),
    # });

    # try:
    #     response = requests.post(
    #         'https://api.openai.com/v1/chat/completions', headers=headers, json=payload)
    #     response.raise_for_status()
    #     result = response.json()

    #     ai_message = result['choices'][0]['message']['content'].strip()
    #     send_ref = db.collection("users", currentuser,
    #                              "tab_id", currentTab, "messages").document()
    #     data = {
    #         "userId": currentuser,
    #         "ai_message": ai_message,
    #         "created_at": firestore.SERVER_TIMESTAMP,  # type: ignore
    #     }
    #     send_ref.set(data)

    #     return send_ref.id
    # except requests.exceptions.RequestException as e:
    #     return f"Error communicating with OpenAI API: {e}"


def rag_endpoint(question, currentuser, currentTab, language):
    print(language)
    try:
        system_prompt = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. give detailed answer.If you don't know the answer,just say you don't know in a respectfull manner. The answer should be in language :{language}. 
Context: {context}
Answer:"""

        main_prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("user", "{question}")])
        retriver = vector_store.as_retriever(search_kwargs={"k": 4})
        string_parser = StrOutputParser()

        main_chain = {"context": itemgetter("question") | retriver,
                      "question": itemgetter("question"), "language": itemgetter("language")} | main_prompt | llm

        answer = main_chain.invoke(
            {"question": question, "language": language})

        ai_message = answer.content
        # ['choices'][0]['message']['content'].strip()
        # ai_message = answer
        send_ref = db.collection("users", currentuser,
                                 "tab_id", currentTab, "messages").document()
        data = {
            "userId": currentuser,
            "ai_message": ai_message,
            "created_at": firestore.SERVER_TIMESTAMP,  # type: ignore
        }
        send_ref.set(data)
        return send_ref.id
    except requests.exceptions.RequestException as e:
        return f"Error communicating with OpenAI API: {e}"


# Flask route for the main page
# @app.route('/')
# def index():
#     if 'chat_history' not in session:
#         session['chat_history'] = []  # Initialize chat history in session
#     return render_template('index.html', chat_history=session['chat_history'])


# Flask route to handle PDF upload
@app.route('/load_db', methods=['POST'])
def load_document():
    file = request.files['file']
    if file:
        # Ensure the uploads directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.pdf')
        file.save(file_path)
        message = pdf_embed_documents(file_path)
        return jsonify({"message": message})
    return jsonify({"error": "No file uploaded!"}), 400


# Flask route to handle web upload
@app.route('/load_web', methods=['POST'])
def load_website():
    data = request.get_json()
    weblink = data.get("webUrl")
    stringlink = str(weblink)
    message = web_embed_documents(stringlink)
    return jsonify({"message": message})


# Flask route to handle youtube upload
@app.route('/load_youtube', methods=['POST'])
def load_youtube():
    data = request.get_json()
    weblink = data.get("webUrl")
    stringlink = str(weblink)
    message = youtube_embed_documents(stringlink)
    return jsonify({"message": message})


# Audio recording function
def record_audio(audio_queue, energy=300, pause=0.8, dynamic_energy=False):
    r = sr.Recognizer()
    r.energy_threshold = energy
    r.pause_threshold = pause
    r.dynamic_energy_threshold = dynamic_energy

    with sr.Microphone(sample_rate=16000) as source:
        print("Listening...")
        audio = r.listen(source)
        torch_audio = torch.from_numpy(np.frombuffer(
            audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0)  # type: ignore
        audio_queue.put_nowait(torch_audio)
        if verbose:
            print("Audio recorded.")


# Transcription function
def transcribe_audio():
    while not audio_queue.empty():
        audio_data = audio_queue.get()
        result = audio_model.transcribe(audio_data, language='english')
        predicted_text = result["text"].strip()  # type: ignore

        if verbose:
            print(f"Transcription: {predicted_text}")
        return predicted_text


# Flask route to handle audio recording and processing
@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        data = request.get_json()  # Parse JSON data
        currentuser = data.get("currentuser")
        currentTab = data.get("currentTab")
        language = "English"

        # Record and process audio
        record_audio(audio_queue)
        question = transcribe_audio()

        human_message = question
        send_ref = db.collection("users", currentuser,
                                 "tab_id", currentTab, "messages").document()
        data = {
            "userId": currentuser,
            "human_message": human_message,
            "created_at": firestore.SERVER_TIMESTAMP,  # type: ignore
        }
        send_ref.set(data)

        rag_endpoint(question, currentuser, currentTab, language)

        # # Send transcription to ChatGPT using the loaded PDF
        # if not question or not qa:
        #     return jsonify({"error": "No valid question or document loaded!"}), 400

        # result = qa({"question": question, "chat_history": chat_history})
        # response = result["answer"]

        # # Convert response to speech
        # tts = gTTS(text=response, lang='en', slow=False)
        # tts.save("response.mp3")  # Save audio file

        # # Update chat history
        # session['chat_history'].append({"user": question, "bot": response})
        # session.modified = True  # Mark session as modified to save changes

        # return jsonify({"transcription": question, "response": response, "chat_history": session['chat_history']})
        return jsonify({"data": question})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/vtv', methods=['POST'])
def voice_to_voice():
    items = request.get_json()
    clicked = items.get("clicked")
    voice_main(clicked)
    return jsonify({"Message": "Voice activated"})


if __name__ == "__main__":
    app.run(debug=True)
