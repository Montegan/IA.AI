from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, YoutubeLoader, WikipediaLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " ", ""],
                                          chunk_size=1000,
                                          chunk_overlap=200,
                                          length_function=len, is_separator_regex=False)


def pdfLoaders(file_path):
    loadpdf = PyPDFLoader(file_path)
    pdf_loaded = loadpdf.load()
    splitted_pdf = splitter.split_documents(pdf_loaded)
    return splitted_pdf


def text_loaders(file_path):
    load_text = TextLoader(file_path, encoding='utf-8')
    text_loaded = load_text.load()
    splitted_text = splitter.split_documents(text_loaded)
    return splitted_text


def web_loaders(web_link):
    webdocs = WebBaseLoader(web_link)
    webdocs_loaded = webdocs.load()
    splitted_web = splitter.split_documents(webdocs_loaded)
    return splitted_web


def wikipedia_loader():
    userInput = input("enter search query: ")
    load_wiki = WikipediaLoader(query=userInput, load_max_docs=2)
    wiki_loaded = load_wiki.load()
    splitted_wiki = splitter.create_documents([wiki_loaded[0].page_content])
    return splitted_wiki


def youtube_loder(youtube_link):
    load_youtube = YoutubeLoader.from_youtube_url(youtube_link)
    youtube_loaded = load_youtube.load()
    splited_youtube = splitter.split_documents(youtube_loaded)
    return splited_youtube
