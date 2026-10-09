# DocuRAG — Document-Grounded Question Answering

DocuRAG is a Retrieval-Augmented Generation (RAG) system that answers questions using information retrieved from user-provided documents. It combines semantic search, CrossEncoder reranking, and large language model generation to produce answers grounded in retrieved context.

The project explores the practical implementation of a RAG pipeline, from document ingestion and vector indexing to relevance ranking, answer generation, and evaluation.

## Key Features

- **Multi-format document ingestion:** Supports TXT, PDF, and DOCX documents.
- **Recursive text chunking:** Splits documents into smaller, overlapping chunks while preserving page metadata where available.
- **Semantic retrieval:** Uses Google Gemini embeddings to represent document chunks and queries as vectors.
- **Persistent vector storage:** Uses Qdrant for vector storage and similarity search.
- **Neural reranking:** Uses a Sentence Transformers CrossEncoder to rerank retrieved chunks by relevance.
- **Relevance filtering:** Applies a configurable reranking threshold before generating an answer.
- **Context-grounded generation:** Uses Gemini to generate answers from retrieved document context.
- **Source tracking:** Returns source document, page, and chunk information for retrieved context.
- **Retrieval evaluation:** Measures Recall@K to assess whether relevant chunks appear among the top-ranked results.
- **Groundedness evaluation:** Includes an evaluation script that checks whether generated answers are supported by retrieved context.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| LLM | Google Gemini API |
| Embedding model | `gemini-embedding-2` |
| Generation model | `gemini-3.1-flash-lite` |
| Vector database | Qdrant |
| Reranking model | `cross-encoder/ms-marco-MiniLM-L6-v2` |
| Data validation | Pydantic |
| PDF processing | PyMuPDF |
| DOCX processing | python-docx |
| Text chunking | LangChain text splitters |
| Environment configuration | python-dotenv |

## Architecture

```text
             TXT / PDF / DOCX
                     |
                     v
             Document Ingestion
                     |
                     v
               Text Chunking
          (overlap and metadata)
                     |
                     v
             Embedding Generation
                     |
                     v
              Qdrant Vector Store
                     |
                     v
              Semantic Retrieval
                     |
                     v
            CrossEncoder Reranking
                     |
                     v
            Relevance Thresholding
                     |
                     v
           Context-Grounded Generation
                     |
                     v
               Answer + Sources
```

The indexing and question-answering paths have distinct responsibilities:

- **Indexing:** Loads documents, splits them into chunks, generates embeddings, and stores the vectors and associated metadata in Qdrant.
- **Question answering:** Embeds a query, retrieves candidate chunks, reranks them, filters low-relevance results, and generates an answer from the remaining context.

If no results pass the configured relevance threshold, the pipeline returns a fallback response instead of generating an answer from the filtered results.

## How It Works

### 1. Document Ingestion

Documents are loaded from the configured `documents/` directory. The ingestion component supports TXT, PDF, and DOCX files.

### 2. Text Chunking

Documents are divided into smaller, overlapping chunks using a recursive text splitter. Page metadata is preserved where available to help identify the source of retrieved content.

### 3. Embedding Generation

The `gemini-embedding-2` model generates vector representations of document chunks and user queries. The configured vector size is 3072.

### 4. Vector Storage and Retrieval

Qdrant stores the embeddings alongside payload metadata, including the source filename, chunk ID, page number, and text content. Query embeddings are used to retrieve semantically similar chunks.

### 5. Reranking

The CrossEncoder model `cross-encoder/ms-marco-MiniLM-L6-v2` reranks retrieved candidates according to their relevance to the query. A configurable threshold is applied to filter the reranked results.

### 6. Answer Generation

The `gemini-3.1-flash-lite` model generates an answer using the remaining document context. The pipeline also returns source information for the retrieved chunks used in the response.

## Project Structure

```text
DocuRAG/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── ingestion.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── knowledge_base.py
│   ├── vector_store.py
│   ├── retrieval.py
│   ├── reranking.py
│   ├── models.py
│   ├── generation.py
│   ├── pipeline.py
│   └── index_metadata.py
├── Evaluation/
│   ├── __init__.py
│   ├── evaluate_retrieval.py
│   ├── evaluate_generation.py
│   └── dataset.json
├── documents/
├── qdrant_storage/
├── index_metadata.json
├── rag.py
├── requirements.txt
└── README.md
```

The `qdrant_storage/` directory and local index metadata are runtime data. They may be generated or updated during indexing and should not be treated as source code.

## Setup and Usage

### Prerequisites

- Python
- Git
- A Google Gemini API key

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/DocuRAG.git
cd DocuRAG
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation because of its execution policy, use a terminal configured to allow virtual-environment activation or activate the environment using the appropriate command for your shell.

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the Gemini API

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with your own API key. The application loads this value through `python-dotenv`.

**Security:** Never commit your real `.env` file, API keys, or other credentials to GitHub.

### 5. Add Your Documents

Place TXT, PDF, or DOCX documents in the configured `documents/` directory.

Use only documents that you own or have permission to process and distribute. Do not publish confidential or restricted documents in a public repository.

### 6. Index Documents

Before querying a fresh installation, ensure that the documents have been indexed into the local Qdrant collection.

The repository includes functions for building the knowledge base and indexing its embeddings. The indexing workflow must be executed before querying if the collection is empty.

> Note: A standalone first-time indexing command has not yet been documented here because the current entry point for invoking the complete indexing workflow has not been verified.

### 7. Run the Application

```bash
python rag.py
```

The current `rag.py` entry point executes a predefined example question and prints the answer and source information. To test a different question, update the query string in `rag.py`.

### 8. Run the Evaluation Scripts

Evaluate retrieval performance:

```bash
python -m Evaluation.evaluate_retrieval
```

Evaluate answer groundedness:

```bash
python -m Evaluation.evaluate_generation
```

These scripts use the configured evaluation dataset and project components to assess retrieval quality and answer grounding.

## Evaluation Results

The project includes separate evaluations for retrieval and answer groundedness.

### Retrieval Evaluation

In the current experiment, Recall@K was measured on six answerable questions. Recall@K measures whether a relevant chunk appears among the top K retrieved results.

| Metric | Dense Retrieval | After Reranking |
|---|---:|---:|
| Recall@1 | 33.3% | 50.0% |
| Recall@3 | 83.3% | 83.3% |
| Recall@5 | 100.0% | 100.0% |

**Observations:**

- Recall@1 increased from 33.3% to 50.0% after reranking.
- Recall@3 remained at 83.3%.
- Recall@5 remained at 100.0%.

These are preliminary results from a small evaluation set. They demonstrate the behavior observed in this experiment and should not be interpreted as a guarantee of performance on larger or different datasets.

### Answer Groundedness

In a separate experiment involving 10 questions, the current groundedness evaluator classified all 10 answers as supported by the supplied context.

**Observed result: 10/10 answers classified as grounded.**

This result reflects the evaluator's classifications on the current test set. It does not establish that the system is free from hallucinations or that every answer will be correctly grounded in future use.

## Limitations and Future Improvements

- Expand the evaluation dataset with more questions, document types, and query difficulty levels.
- Improve retrieval quality for ambiguous questions and documents with overlapping information.
- Evaluate groundedness on a larger and more diverse set of generated answers.
- Add automated tests for document ingestion, chunking, indexing, retrieval, reranking, and generation.
- Provide a clear first-time indexing command and improve fresh-install reproducibility.
- Improve source attribution and make it easier to inspect the evidence behind generated answers.
- Investigate ways to reduce latency and resource consumption during reranking and generation.

## Learning Outcomes

This project explores the practical engineering challenges involved in building a RAG application, including:

- Document preprocessing and metadata preservation.
- Text chunking and embedding generation.
- Vector similarity search with Qdrant.
- Neural reranking and relevance filtering.
- Context-grounded LLM generation.
- Retrieval and groundedness evaluation.
- Environment configuration and persistent local vector storage.

