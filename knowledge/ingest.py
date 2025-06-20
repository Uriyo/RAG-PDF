import os
import uuid
from typing import List, Tuple

from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec, VectorType
from PyPDF2 import PdfReader
from django.conf import settings


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def init_pinecone():
    """Return an Index client, creating the index if needed (Pinecone v2 SDK)."""
    api_key = settings.PINECONE_API_KEY
    if not api_key:
        raise ValueError("PINECONE_API_KEY is not set")

    pc = Pinecone(api_key=api_key)

    index_name = settings.PINECONE_INDEX_NAME

    # Create index if missing
    if not pc.has_index(index_name):
        cloud = settings.PINECONE_CLOUD
        region = settings.PINECONE_REGION
        spec = ServerlessSpec(cloud=cloud, region=region)
        pc.create_index(
            name=index_name,
            dimension=settings.EMBEDDING_DIM,
            metric="cosine",
            vector_type=VectorType.DENSE,
            spec=spec,
        )

    # Get host to build Index client
    host = pc.describe_index(index_name).host
    return pc.Index(host=host)


def load_pdf_text(file_path: str) -> List[Tuple[str, int]]:
    """Load pdf and return list of (page_text, page_number)."""
    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append((text, i))
    return pages


def chunk_text(text: str, chunk_size: int = settings.CHUNK_SIZE, overlap: int = settings.CHUNK_OVERLAP):
    """Yield overlapping chunks from text."""
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        yield text[start:end]
        start += chunk_size - overlap


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Call OpenAI embedding API for list of texts."""
    resp = client.embeddings.create(model=settings.OPENAI_EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in resp.data]


def ingest_document(file_path: str, source_name: str | None = None):
    """Parse PDF, embed chunks, and upsert to Pinecone."""
    if not source_name:
        source_name = os.path.basename(file_path)

    index = init_pinecone()

    pages = load_pdf_text(file_path)
    chunks = []
    metadatas = []

    for page_text, page_num in pages:
        for chunk in chunk_text(page_text):
            chunks.append(chunk)
            metadatas.append({"source": source_name, "page": page_num, "text": chunk})

    if not chunks:
        print("No text found in document.")
        return

    embeddings = embed_texts(chunks)

    # Prepare vectors with unique ids
    vectors = [(str(uuid.uuid4()), emb, meta) for emb, meta in zip(embeddings, metadatas)]

    # Upsert in batches
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        index.upsert(vectors=batch)

    print(f"Ingested {len(chunks)} chunks from {source_name}.") 