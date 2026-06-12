from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from services import ingest_pdf_directory, ingest_pdf_directory_pymupdf



DATA_DIR = "../data/raw_pdfs"
DB_DIR = "../vector_storage/chroma_db"
MODEL_NAME = "BAAI/bge-large-en-v1.5"
MODEL_NAME2 = "BAAI/bge-m3"
CHIPSET = {
    'GPUBinding':"cuda",
    'CPUBinging':'cpu',
    'Apple_silicon':"mps",
}


def build_knowledge_index():
    print("1. extracting raw text from PDFs")
    docs = ingest_pdf_directory_pymupdf(DATA_DIR)
    # print(docs)

    print("2. chunking text for optimal embeddings resolutions")
    splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    # print(chunks)

    print("3. Initialising local embedding transformers ...")
    embedding = HuggingFaceEmbeddings(model_name=MODEL_NAME, model_kwargs={'device': CHIPSET['Apple_silicon']})
    # print(embedding)

    print("4. constructing and persisting vector Database ... ")
    db = Chroma.from_documents(documents=chunks, embedding=embedding, persist_directory=DB_DIR)
    print("Success! Database secured on local storage")

    print("5. persisting vector Database ... ")
    results = db.similarity_search("What is the documents?", k=5)

    for result in results:
        print(result)
        print("\n")



if __name__ == "__main__":
    build_knowledge_index()


