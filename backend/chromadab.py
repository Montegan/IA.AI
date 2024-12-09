import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, YoutubeLoader, TextLoader, UnstructuredExcelLoader, UnstructuredPowerPointLoader, UnstructuredWordDocumentLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
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


def text_embed_documents(txt_path):
    load_text = TextLoader(txt_path)
    txt_loaded = load_text.load()
    splietted_txt = splitter.split_documents(txt_loaded)
    vector_store.add_documents(splietted_txt)
    return ("text docs embeded")


def csv_embed_documents(csv_path):
    load_csv = CSVLoader(csv_path)
    csv_loaded = load_csv.load()
    splitted_csv = splitter.split_documents(csv_loaded)
    vector_store.add_documents(splitted_csv)
    return ("csv docs embeded")


def excel_embed_documents(excel_path):
    load_excel = UnstructuredExcelLoader(excel_path)
    excel_loaded = load_excel.load()
    splitted_excel = splitter.split_documents(excel_loaded)
    vector_store.add_documents(splitted_excel)
    return ("excel docs embeded")


def powerpoint_embed_documets(ppt_path):
    load_ppt = UnstructuredPowerPointLoader(ppt_path)
    ppt_loaded = load_ppt.load()
    splitted_ppt = splitter.split_documents(ppt_loaded)
    vector_store.add_documents(splitted_ppt)
    return ("ppt docs embeded")


def docs_embed_documents(docs_path):
    load_docs = UnstructuredWordDocumentLoader(docs_path)
    docs_loaded = load_docs.load()
    splitted_docs = splitter.split_documents(docs_loaded)
    vector_store.add_documents(splitted_docs)
    return ("docs embeded")
