import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma





DATA_DIR = "../data/raw_pdfs"
DB_DIR = "../vector_storage/chroma_db"
MODEL_NAME = "BAAI/bge-large-en-v1.5"
MODEL_NAME2 = "BAAI/bge-m3"

def build_knowledge_index():
    print("1. extracting raw text from PDFs")
