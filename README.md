# Knowledge Assistant API

A Retrieval-Augmented Generation (RAG) backend powered by Django, OpenAI, and Pinecone.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture & Approach](#architecture--approach)
- [Features](#features)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [API Endpoints](#api-endpoints)
  - [Upload Document](#upload-document)
  - [Ask Question](#ask-question)
- [Swagger/OpenAPI Documentation](#swaggeropenapi-documentation)
- [Design Decisions & Implementation Details](#design-decisions--implementation-details)
- [Extending the Project](#extending-the-project)
- [Notes](#notes)
- [License](#license)

---

## Project Overview

This project implements a backend API that allows users to upload documents (PDF/Text), index them using OpenAI embeddings in Pinecone, and then ask natural-language questions. The system returns answers grounded in the uploaded content, along with cited sources (document name and page).

---

## Architecture & Approach

- **Framework:** Django + Django REST Framework (DRF)
- **Vector Store:** Pinecone for fast similarity search
- **LLM:** OpenAI GPT (configurable)
- **API Documentation:** drf-spectacular (OpenAPI 3/Swagger UI)
- **File Uploads:** Handled via DRF's `MultiPartParser` and custom serializer
- **RAG Pipeline:**
  1. **Ingestion:** Uploaded documents are chunked, embedded, and indexed in Pinecone.
  2. **Retrieval:** When a question is asked, the system embeds the query, retrieves relevant chunks, and constructs a context.
  3. **Generation:** The context and question are sent to the LLM, which generates an answer.

---

## Features
- Upload PDF/Text documents and index them for semantic search.
- Ask questions and get answers grounded in your uploaded content.
- Returns answers with cited sources (document name + page).
- Interactive API documentation with Swagger UI, including file upload support.

---

## Setup & Installation

1. **Clone & Install**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=sk-...
   PINECONE_API_KEY=...
   PINECONE_ENVIRONMENT=YOUR_PINECONE_ENV
   PINECONE_CLOUD=aws
   PINECONE_REGION=us-east-1
   PINECONE_INDEX_NAME=knowledge-index
   DJANGO_SECRET_KEY=replace-me
   ```

3. **Run Migrations & Server**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

---

## API Endpoints

### Upload Document
- **Endpoint:** `POST /api/upload-doc/`
- **Description:** Upload a PDF or text file to be indexed.
- **Request:** `multipart/form-data` with a `file` field.
- **Response:** `{ "detail": "File uploaded and ingested." }`

### Ask Question
- **Endpoint:** `POST /api/ask-question/`
- **Description:** Ask a question about the uploaded documents.
- **Request:**
  ```json
  { "question": "What is photosynthesis?" }
  ```
- **Response:**
  ```json
  {
    "answer": "Photosynthesis is the process ...",
    "sources": ["document.pdf - Page 2"]
  }
  ```

---

## Swagger/OpenAPI Documentation

- **Docs URL:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Schema URL:** [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)
- The Swagger UI allows you to interactively test all endpoints, including file uploads.

### File Upload Fix in Swagger
To ensure the file upload endpoint displays the file picker in Swagger UI, the following was added to the view:
```python
@extend_schema(
    request={'multipart/form-data': FileUploadSerializer},
    responses={200: MessageSerializer},
)
```
This explicitly tells drf-spectacular to treat the request as `multipart/form-data`, fixing the Swagger UI file upload issue ([Swagger file upload docs](https://swagger.io/docs/specification/v2_0/file-upload/)).

---

## Design Decisions & Implementation Details

- **Chunking & Embedding:** Documents are split into overlapping chunks for better retrieval. Each chunk is embedded using OpenAI and stored in Pinecone with metadata (source, page, etc).
- **Retrieval:** When a question is asked, its embedding is used to query Pinecone for the most relevant chunks.
- **Prompting:** Retrieved context is combined with the question in a prompt template, instructing the LLM to answer only from the provided context.
- **Citations:** The API returns both the answer and a list of sources, making it easy to trace the answer back to the original document and page.
- **Extensibility:** The ingestion pipeline can be extended to support more file types by modifying `knowledge/ingest.py`.
- **Security:** By default, the API is open (for demo). For production, add authentication and HTTPS.

---

## Extending the Project
- **Add support for more file types:** Extend `knowledge/ingest.py`.
- **Improve chunking:** Use smarter chunking for better context.
- **Add authentication:** Use DRF's authentication classes.
- **Scale to production:** Use a production-ready DB, configure static/media, and secure secrets.

---

## Notes
- Default LLM is GPT-3.5-Turbo; configurable in `settings.py`.
- Only PDFs are supported out of the box.
- For production, secure your API and use HTTPS.

---
