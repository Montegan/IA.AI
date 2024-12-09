from flask_mail import Mail, Message
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
from email_service import compose_email
from openai_assistant import voice_main
from chromadab import pdf_embed_documents, web_embed_documents, youtube_embed_documents, vector_store, docs_embed_documents, powerpoint_embed_documets, excel_embed_documents, csv_embed_documents, text_embed_documents
import magic
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Load API key from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
appMAIL_SERVER = os.getenv("appMAIL_SERVER")
appMAIL_PORT = int(os.getenv("appMAIL_PORT"))  # type: ignore
appMAIL_USE_TLS = os.getenv("appMAIL_USE_TLS")
appMAIL_USE_SSL = os.getenv("appMAIL_USE_SSL")
appMAIL_USERNAME = os.getenv("appMAIL_USERNAME")
appMAIL_PASSWORD = os.getenv("appMAIL_PASSWORD")
appMAIL_DEFAULT_SENDER = os.getenv("appMAIL_DEFAULT_SENDER")
certificates = os.getenv("certificates")


llm = ChatOpenAI()
app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey'  # For session management
app.config['UPLOAD_FOLDER'] = 'uploads/'

openai.api_key = OPENAI_API_KEY

# firebase credentials
cred = credentials.Certificate(certificates)
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

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = appMAIL_SERVER
app.config['MAIL_PORT'] = appMAIL_PORT
app.config['MAIL_USE_TLS'] = appMAIL_USE_TLS
# app.config['MAIL_USE_SSL'] = appMAIL_USE_SSL
# Replace with your email
app.config['MAIL_USERNAME'] = appMAIL_USERNAME
# Replace with your app password
app.config['MAIL_PASSWORD'] = appMAIL_PASSWORD
# Replace with your email
app.config['MAIL_DEFAULT_SENDER'] = appMAIL_DEFAULT_SENDER


# Initialize Flask-Mail
mail = Mail(app)


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
# @app.route('/load_db', methods=['POST'])
# def load_document(pdf_doc):
#     file = pdf_doc
#     print(file)
#     if file:
#         # Ensure the uploads directory exists
#         os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.pdf')
#         file.save(file_path)
#         print(file_path)
#         message = pdf_embed_documents(file_path)
#         return jsonify({"message": message})
#     return jsonify({"error": "No file uploaded!"}), 400


# def upload_file():
#     if 'file' not in request.files:
#         return "No file uploaded", 400

#     file = request.files['file']
#     file_data = file.read()  # Read file content

#     # Detect MIME type
#     mime = magic.Magic(mime=True)
#     file_type = mime.from_buffer(file_data)
#     print(file_type)

@app.route('/load_db', methods=['POST'])
def load_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded!"}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({"error": "No file selected!"}), 400

    # Save file temporarily
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Detect MIME type using magic
    mime = magic.Magic(mime=True)
    with open(file_path, 'rb') as f:
        file_type = mime.from_buffer(f.read())
        print(file_type)

    # Check file type and process accordingly
    if 'pdf' in file_type:
        message = pdf_embed_documents(file_path)  # Process PDF file
        return jsonify({"message": f"PDF detected. {message}"}), 200
    elif 'msword' in file_type or 'officedocument.wordprocessingml' in file_type:
        message = docs_embed_documents(file_path)
        return jsonify({"message": f"{message}"}), 200
    elif 'officedocument.spreadsheetml' in file_type:
        message = excel_embed_documents(file_path)
        return jsonify({"message": f"{message}"}), 200
    elif 'officedocument.presentationml' in file_type:
        message = powerpoint_embed_documets(file_path)
        return jsonify({"message": f"{message}"}), 200
    elif 'csv' in file_type or 'text/plain' in file_type:
        message = csv_embed_documents(file_path)
        return jsonify({"message": f"{message}"}), 200
    else:
        return jsonify({"message": "Unsupported file type!"}), 400


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


# Email Endpoint
@app.route('/composeEmail', methods=['POST'])
def create_email():
    data = request.get_json()
    draft = data.get('comment')
    language = data.get('language')
    email = compose_email(draft, language)
    return (jsonify(email))


# Send email to user


# @app.route('/sendmail', methods=['POST'])
# def send_email():
#     # Get form data
#     # recipient = request.form['recipient']
#     # subject = create_subject(subject)
#     # message = request.form['message']
#     data = request.get_json()
#     final_email = data.get('final_email')
#     subject = data.get('subject')
#     if not subject:
#         subject = "Email from SFBU"
#     try:
#         msg = Message(subject=subject, recipients=[
#                       "fasilsimon8@gmail.com"], body=final_email)
#         mail.send(msg)
#         return "Email sent successfully!"
#     except Exception as e:
#         return str(e)


@app.route('/sendmail', methods=['POST'])
def send_email():
    data = request.get_json()  # Get the JSON payload
    final_email = data.get('final_email')  # Extract the email body
    # Extract the subject
    mail_subject = data.get('subject').strip()
    reciever_address = data.get('reciver').strip()
    print(reciever_address)

    if not mail_subject:  # Fallback subject if none is provided
        mail_subject = "Email from SFBU"
    try:
        # print(f"{mail_subject}, Email Content: {
        #       final_email}")  # Debugging logs
        msg = Message(subject=mail_subject,  # Use the subject received from ChatGPT
                      # Replace with dynamic or fixed recipient
                      recipients=[reciever_address],
                      body=final_email)
        mail.send(msg)  # Send the email
        return "Email sent successfully!"
    except Exception as e:
        return str(e)  # Return the exception message for debugging

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
