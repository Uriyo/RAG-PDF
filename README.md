# Knowledge Assistant API

This project provides a Retrieval-Augmented Generation (RAG) backend powered by Django, OpenAI, and Pinecone.

## Features

* Upload PDF/Text documents and index them with OpenAI embeddings in Pinecone.
* Ask natural-language questions and get answers grounded in the uploaded content.
* Returns answer and list of cited sources (document name + page).

## Quick Start

1. **Clone & Install**

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Variables**

Create a `.env` file in the project root (or export vars some other way):

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

4. **Ingest a Document**

```bash
python manage.py ingest_doc path/to/your/document.pdf
```

5. **Ask a Question**

Send a POST request:

```bash
curl -X POST http://127.0.0.1:8000/api/ask-question/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is photosynthesis?"}'
```

Response:

```json
{
  "answer": "Photosynthesis is the process ...",
  "sources": ["document.pdf - Page 2"]
}
```

---

### Notes
* Default uses GPT-3.5-Turbo; tweak in `settings.py`.
* Supports only PDFs out of the box. Extend `knowledge/ingest.py` to handle other formats.
* For production, configure authentication and HTTPS. 