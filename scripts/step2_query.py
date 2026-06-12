from langchain_huggingface import HuggingFaceEmbeddings
from scripts import CHIPSET
from langchain_chroma import Chroma

DB_DIR = "../vector_storage/chroma_db"
MODEL_NAME = "BAAI/bge-large-en-v1.5"


#Mount the offline model and connect to the existing database
embedding = HuggingFaceEmbeddings(model_name=MODEL_NAME, model_kwargs={'device': CHIPSET['Apple_silicon']})
vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embedding)


def query_knowledge_base(user_query):
    print(f"Searching  for {user_query}.......")
    # Execute a cosine similarity search over the vector space
    result = vector_db.similarity_search(user_query, k=3)

    for i, doc in enumerate(result):
        source = doc.metadata.get('source', 'Unknown')
        page = doc.metadata.get('page', '?')
        print(f"\n[Match {i+1}] Source: {source} (Page {page+1})")
        print(f"Content: {doc.page_content.strip()}")
        print("-"*60)


if(__name__ == "__main__"):
    while True:
        user_query = input("Search for something: ")
        if user_query.lower() == "exit":
            break
        query_knowledge_base(user_query)



