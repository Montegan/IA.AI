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
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import ConversationalRetrievalChain
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Load API key from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For session management
app.config['UPLOAD_FOLDER'] = 'uploads/'

openai.api_key = OPENAI_API_KEY

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


def load_db(file_path, chain_type="stuff", k=4):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    db = DocArrayInMemorySearch.from_documents(docs, embeddings)
    retriever = db.as_retriever(
        search_type="similarity", search_kwargs={"k": k})

    global qa
    qa = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
        chain_type=chain_type,
        retriever=retriever,
        return_source_documents=True,
        return_generated_question=True,
    )

# Function to interact with OpenAI API


def ask_chatgpt(prompt):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}',
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.7,
    }

    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions', headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        return f"Error communicating with OpenAI API: {e}"

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
        predicted_text = result["text"].strip()

        if verbose:
            print(f"Transcription: {predicted_text}")
        return predicted_text


# Flask route for the main page
@app.route('/')
def index():
    if 'chat_history' not in session:
        session['chat_history'] = []  # Initialize chat history in session
    return render_template('index.html', chat_history=session['chat_history'])

# Flask route to handle PDF upload


@app.route('/load_db', methods=['POST'])
def load_document():
    file = request.files['file']
    if file:
        # Ensure the uploads directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.pdf')
        file.save(file_path)
        load_db(file_path)
        return jsonify({"message": "Document loaded successfully!"})
    return jsonify({"error": "No file uploaded!"}), 400

# Flask route to handle audio recording and processing


@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        # Record and process audio
        record_audio(audio_queue)
        question = transcribe_audio()

        # Send transcription to ChatGPT using the loaded PDF
        if not question or not qa:
            return jsonify({"error": "No valid question or document loaded!"}), 400

        result = qa({"question": question, "chat_history": chat_history})
        response = result["answer"]

        # Convert response to speech
        tts = gTTS(text=response, lang='en', slow=False)
        tts.save("response.mp3")  # Save audio file

        # Update chat history
        session['chat_history'].append({"user": question, "bot": response})
        session.modified = True  # Mark session as modified to save changes

        return jsonify({"transcription": question, "response": response, "chat_history": session['chat_history']})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
