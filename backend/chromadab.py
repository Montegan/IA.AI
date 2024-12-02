import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, YoutubeLoader, WikipediaLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


_ = load_dotenv()


splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " ", ""],
                                          chunk_size=1000,
                                          chunk_overlap=200,
                                          length_function=len, is_separator_regex=False)


embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

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
