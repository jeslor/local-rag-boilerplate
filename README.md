# 🧠 Local RAG Boilerplate (Universal Vector Engine)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Framework](https://img.shields.io/badge/LangChain-Integration-green.svg)](https://python.langchain.com/)
[![Database](https://img.shields.io/badge/VectorStore-ChromaDB-orange.svg)](https://github.com/chroma-core/chroma)
[![Embeddings](https://img.shields.io/badge/Model-BAAI%2Fbge--m3-purple.svg)](https://huggingface.co/BAAI/bge-m3)
[![Security](https://img.shields.io/badge/Security-Air--Gapped-red.svg)]()

An entirely local, secure, and domain-agnostic Retrieval-Augmented Generation (RAG) framework. 

Designed as a foundational boilerplate, this pipeline ingests dense technical manuals, corporate policies, legal contracts, or medical guidelines into a searchable mathematical vector space. By running 100% offline, it guarantees strict data privacy, zero cloud exposure, and sub-second semantic retrieval for any industry.

---

## 🏗️ Architectural Overview

Handling sensitive enterprise data requires zero tolerance for data leaks. This system operates on a cleanly **decoupled dual-pipeline architecture**, ensuring heavy ingestion tasks do not block runtime retrieval, and data never leaves the local machine.

```text
                      [ Raw Domain PDFs ]
                                 │
                      ┌──────────▼──────────┐
                      │  01_ingest.py (ETL) │
                      └──────────┬──────────┘
                                 │  (Recursive Token Splitting: 750/100)
                      ┌──────────▼──────────┐
                      │  BAAI/bge-m3 Engine │ ◄─── High-Dimensional Normalization
                      └──────────┬──────────┘
                                 │  (1024-Dim Dense Vector Map)
                      ┌──────────▼──────────┐
                      │ Persistent ChromaDB │
                      └──────────▲──────────┘
                                 │  (Low-Latency Cosine Similarity Search)
                      ┌──────────┴──────────┐
                      │  02_query.py (API)  │
                      └──────────▲──────────┘
                                 │
                         [ User Semantic Query ]

```
### Core Technologies
* **Embeddings:** Utilizes `BAAI/bge-m3` (8,192 token context window) for state-of-the-art semantic mapping of complex nomenclature across any language or domain.
* **Vector Storage:** Local, SQLite-backed `ChromaDB` for persistent, high-speed vector retrieval.
* **Orchestration:** `LangChain` framework for document loading, recursive chunking, and pipeline management.

---

## 📁 Repository Structure

```text
local-rag-boilerplate/
├── .venv/                      # Isolated Python virtual environment
├── data/
│   └── raw_pdfs/               # Source ingestion directory (drop target PDFs here)
├── scripts/
│   ├── __init__.py
│   ├── step1_ingest.py         # Document extraction, processing, and DB embedding pipeline
│   └── step2_query.py          # Standard command-line semantic search interface
├── services/
│   ├── __init__.py
│   ├── house_keeping.py        # Storage maintenance, indices clearance, and resets
│   └── services.py             # Shared application components and core logic
├── vector_storage/
│   └── chroma_db/              # Auto-generated persistent vector database
│       ├── f5e25dda-.../       # Vector index segments and hash tables
│       └── chroma.sqlite3      # Metadata mapping registry
├── .gitignore                  # Prevents staging environments and databases to version control
├── main.py                     # Primary runtime orchestration entry-point
└── README.md                   # System architecture and deployment documentation
```

## 🛠️ Installation & Setup
### Prerequisites

- Python 3.10+
- Minimum 8GB RAM (16GB+ recommended for massive PDF ingestion)

### 1. Clone & Navigate

```
    git clone [https://github.com/jeslor/local-rag-boilerplate.git](https://github.com/jeslor/local-rag-boilerplate.git)
    cd local-rag-boilerplate
```

### 2. Install Dependencies
Install your system dependencies:
```
    pip install -r requirements.txt
```

## 🚀 Execution Guide
### Phase 1: Data Ingestion (ETL)
Place your target PDFs into data/raw_pdfs/. Then process them into your vector store:
````
    python scripts/step1_ingest.py
````
Note: The initial run requires an internet connection to securely cache the BAAI/bge-m3 model weights (~1.2GB) locally. All subsequent execution layers operate completely standalone and 100% offline.

### Phase 2: Semantic Retrieval
Once your local SQLite matrix database is compiled, execute queries instantly without rebuilding indices:
````
    python scripts/step2_query.py
````
