# DocuRAG — Document-Grounded Q&A and Study Assistant

DocuRAG is a Retrieval-Augmented Generation (RAG) application that allows users to ask questions about their documents and generate study materials from their content.

It combines semantic retrieval, CrossEncoder reranking, and Google Gemini generation to produce answers grounded in retrieved document context. Its Streamlit interface also provides study tools for generating quizzes, flashcards, and concise bullet-point summaries from indexed documents.

## Key Features

### Document Processing and Retrieval
- **Multi-format ingestion:** Supports TXT, PDF, and DOCX documents.
- **Recursive text chunking:** Splits documents into smaller, overlapping chunks while preserving relevant metadata.
- **Semantic search:** Generates document and query embeddings using Google's `gemini-embedding-2`.
- **Vector storage:** Stores embeddings and document metadata in Qdrant.
- **CrossEncoder reranking:** Reorders retrieved chunks using `cross-encoder/ms-marco-MiniLM-L6-v2`.
- **Relevance filtering:** Filters low-relevance results using a configurable threshold.
- **Incremental indexing:** Detects added, modified, and removed documents to avoid unnecessarily reindexing unchanged files.
- **Source tracking:** Retains document filenames, page numbers, and chunk identifiers for source attribution.

### Document Q&A
- Generates answers using retrieved document context.
- Supports contextualized follow-up questions using conversation history.
- Returns source information associated with retrieved results.
- Uses a fallback response when no retrieved results pass the relevance threshold.

### Study Mode

Study Mode provides four document-based learning features:

- **Document Q&A:** Ask questions about your indexed documents.
- **Quiz:** Generate multiple-choice questions with answer options, correct answers, explanations, and score calculation.
- **Flash Cards:** Generate question-and-answer cards with individually revealable answers.
- **Bullet Points:** Generate concise summaries highlighting important concepts and information.

Quiz, Flash Cards, and Bullet Points use the chunks belonging to the selected indexed document as their input context.

### Evaluation and Testing
- Retrieval evaluation using Recall@K.
- Groundedness evaluation for generated answers.
- Automated tests for indexing, chunking, metadata, and generator response validation.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| User interface | Streamlit |
| LLM | Google Gemini API |
| Embedding model | `gemini-embedding-2` |
| Generation model | `gemini-3.1-flash-lite` |
| Vector database | Qdrant |
| Reranking model | `cross-encoder/ms-marco-MiniLM-L6-v2` |
| PDF processing | PyMuPDF |
| DOCX processing | python-docx |
| Text chunking | LangChain text splitters |
| Environment configuration | python-dotenv |
| Automated testing | pytest |

## Architecture

### Indexing Pipeline

```text
TXT / PDF / DOCX
       |
       v
Document Ingestion
       |
       v
Text Chunking + Metadata
       |
       v
Embedding Generation
       |
       v
Qdrant Vector Store
```

The indexing pipeline loads documents, splits them into chunks, generates embeddings, and stores the vectors with their associated metadata.

Incremental indexing compares document metadata and content hashes to identify changes. Stale indexed documents can also be removed from the vector store.

### Question-Answering Pipeline

```text
User Query + Conversation History
              |
              v
      Query Contextualization
              |
              v
       Semantic Retrieval
              |
              v
      CrossEncoder Reranking
              |
              v
       Relevance Filtering
              |
              v
   Context-Grounded Generation
              |
              v
        Answer + Sources
```

The pipeline retrieves candidate chunks, reranks them according to query relevance, filters low-relevance results, and generates an answer using the remaining context.

### Study Mode Pipeline

```text
Select Indexed Document
           |
           v
Retrieve Document Chunks
           |
           v
Combine Chunk Content
           |
           v
       Gemini LLM
           |
           v
  Quiz / Flash Cards /
     Bullet Points
```

The study generators operate on the selected document's chunks. The current implementation combines those chunks into one prompt, so very large documents may require a more scalable context-management strategy.

## How It Works

### 1. Document Ingestion

The ingestion component loads supported TXT, PDF, and DOCX documents from the configured documents directory.

### 2. Text Chunking

Documents are divided into smaller, overlapping chunks. Relevant metadata, including page information where available, is retained for downstream retrieval and source attribution.

### 3. Embedding Generation

The `gemini-embedding-2` model generates vector representations of document chunks and user queries. The configured vector size is 3072 dimensions.

### 4. Vector Storage and Retrieval

Qdrant stores embeddings alongside payload metadata such as filename, chunk ID, page number, and text content. Query embeddings are used to retrieve semantically similar chunks.

### 5. Reranking and Relevance Filtering

The CrossEncoder model `cross-encoder/ms-marco-MiniLM-L6-v2` reranks retrieved candidates. A configurable threshold determines which results proceed to answer generation.

### 6. Grounded Answer Generation

The `gemini-3.1-flash-lite` model generates answers using the filtered document context. The pipeline returns source metadata associated with the retrieved results.

### 7. Study Material Generation

Study Mode uses the selected document's content to generate quizzes, flashcards, and bullet-point summaries. Generated responses are parsed and validated before being used by the application.

## Project Structure

```text
DocuRAG/
├── app/
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
│   ├── contextualizer.py
│   ├── pipeline.py
│   ├── indexer.py
│   ├── index_metadata.py
│   ├── quiz_generator.py
│   ├── flashcard_generator.py
│   └── bullet_points_generator.py
├── Evaluation/
│   ├── evaluate_retrieval.py
│   ├── evaluate_generation.py
│   └── dataset.json
├── Documents/
├── tests/
├── index_metadata.json
├── rag.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```

Runtime data, including local Qdrant storage and indexing metadata, may be created or updated as the application runs. These files should be managed separately from source code where appropriate.

## Setup and Usage

### Prerequisites

- Python
- Git
- A Google Gemini API key

### 1. Clone the Repository

```bash
git clone https://github.com/mahendrasidhu/DocuRAG.git
cd DocuRAG
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the Gemini API

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with your own API key.

**Security:** Never commit your real `.env` file, API keys, or other credentials to GitHub.

### 5. Add Documents

Place your TXT, PDF, or DOCX files in the directory configured by `DOCUMENTS_DIR` in `app/config.py`.

Use only documents you own or have permission to process and distribute. Avoid publishing confidential or restricted documents in a public repository.

Ensure the directory name matches the configured value, particularly when running on case-sensitive operating systems.

### 6. Index Documents

Run the indexing module from the project root:

```bash
python -m app.indexer
```

This invokes the indexing workflow and closes the vector-store client when the standalone indexing process finishes.

Ensure indexing completes successfully before querying documents or using Study Mode.

### 7. Run the Streamlit Application

```bash
streamlit run streamlit_app.py
```

Open the local URL printed by Streamlit in your browser.

The application provides document upload and indexing functionality, document Q&A, and the Study Mode tools.

### 8. Run the Command-Line Example

```bash
python rag.py
```

This executes the predefined example query in `rag.py`.

### 9. Run Automated Tests

Run the full test suite from the project root:

```bash
python -m pytest -v
```

The existing suite and the generator validation tests cover indexing, chunking, metadata, and response validation. The tests do not yet constitute comprehensive coverage of all API failures or generation behavior.

## Evaluation Results

### Retrieval Evaluation

The current retrieval experiment used six answerable questions. Recall@K measures whether a relevant chunk appears among the top K retrieved results.

| Metric | Dense Retrieval | After Reranking |
|---|---:|---:|
| Recall@1 | 33.3% | 50.0% |
| Recall@3 | 83.3% | 83.3% |
| Recall@5 | 100.0% | 100.0% |

**Observations**

- Recall@1 increased from 33.3% to 50.0% after reranking.
- Recall@3 remained at 83.3%.
- Recall@5 remained at 100.0%.

These are preliminary results from a small evaluation dataset and should not be interpreted as a guarantee of performance on larger or different datasets.

### Answer Groundedness

In a separate experiment involving ten questions, the current groundedness evaluator classified all ten answers as supported by the supplied context.

**Observed result: 10/10 answers classified as grounded.**

This result reflects the evaluator's classifications on the current test set. It does not establish that the system is free from hallucinations or that every future answer will be correctly grounded.

## Limitations and Future Improvements

- Improve handling of very large documents in Study Mode.
- Expand the evaluation dataset to include more documents and diverse query types.
- Evaluate quiz accuracy, flashcard quality, and summary faithfulness more comprehensively.
- Expand automated tests to cover generation behavior, API failures, and additional edge cases.
- Improve source attribution and evidence inspection.
- Investigate ways to reduce latency and resource consumption during reranking and generation.
- Improve fresh-install reproducibility and document the runtime requirements of the application.

## Learning Outcomes

This project explores practical engineering challenges involved in building a RAG application, including:

- Document preprocessing and metadata preservation.
- Text chunking and embedding generation.
- Vector similarity search with Qdrant.
- Neural reranking and relevance filtering.
- Context-grounded LLM generation.
- Contextualized follow-up questions.
- Incremental document indexing.
- LLM-powered quiz, flashcard, and summary generation.
- Retrieval and groundedness evaluation.
- Automated testing and environment configuration.
