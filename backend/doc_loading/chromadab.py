import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, YoutubeLoader, WikipediaLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


_ = load_dotenv()
# pdfPath = "C:\\Users\\H00422003\\Desktop\\SFBU\\2ndsem\\GenAI\\langchain_rag\\data\\sfbu-2024-2025-university-catalog-8-20-2024.pdf"
# textPath = "C:\\Users\\H00422003\\Desktop\\SFBU\\2ndsem\\GenAI\\langchain_rag\\data\\stateUnion.txt"
# web = "https://www.sfbu.edu/student-health-insurance"
# youtubeLink = "https://www.youtube.com/watch?v=kuZNIvdwnMc&ab"

# docs = pdfLoaders(pdfPath)
# text_docs = text_loaders(textPath)
# web_docs = web_loaders(web)
# youtube_docs = youtube_loder(youtubeLink)
api_key = os.getenv("OPENAI_API_KEY")
splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " ", ""],
                                          chunk_size=1000,
                                          chunk_overlap=200,
                                          length_function=len, is_separator_regex=False)
if not api_key:
    raise ValueError("API key not found. Please check your .env file.")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large", api_key=api_key)  # type: ignore

vector_store = Chroma(collection_name="my_chroma",
                      embedding_function=embeddings,
                      persist_directory="./chroma_sfbu")


def pdf_embed_documents(pdfPath):
    loadpdf = PyPDFLoader(pdfPath)
    pdf_loaded = loadpdf.load()
    splitted_pdf = splitter.split_documents(pdf_loaded)
    vector_store.add_documents(documents=splitted_pdf)
    return ("pdf docs embeded")


def web_embed_documents(web_link):
    webdocs = WebBaseLoader(web_link)
    webdocs_loaded = webdocs.load()
    splitted_web = splitter.split_documents(webdocs_loaded)
    vector_store.add_documents(documents=splitted_web)
    return ("web docs embeded")


def youtube_embed_documents(youtube_link):
    load_youtube = YoutubeLoader.from_youtube_url(youtube_link)
    youtube_loaded = load_youtube.load()
    splited_youtube = splitter.split_documents(youtube_loaded)
    vector_store.add_documents(splited_youtube)
    return ("youtube docs embeded")
