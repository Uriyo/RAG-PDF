import os

from openai import OpenAI
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, parsers
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiRequest
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers as drf_serializers

from knowledge.serializers import (
    QuestionSerializer,
    AnswerSerializer,
    FileUploadSerializer,
    MessageSerializer,
)
from knowledge.ingest import init_pinecone, embed_texts
from knowledge.models import Document


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TEMPLATE = (
    "You are a knowledgeable assistant who answers questions using ONLY the given context.\n"
    "If the answer is not contained within the context, say 'I don't know based on the provided information.'\n\n"
    "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
)


@extend_schema(
    request=QuestionSerializer,
    responses=AnswerSerializer,
)
class AskQuestionView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data["question"]

        # Retrieve relevant chunks via Pinecone
        index = init_pinecone()

        # Embed question
        q_embedding = embed_texts([question])[0]

        # Query index
        res = index.query(vector=q_embedding, top_k=settings.TOP_K, include_metadata=True)
        matches = res.matches if hasattr(res, "matches") else res.get("matches", [])

        if not matches:
            return Response({"answer": "I don't know."})

        context_parts = []
        sources = []
        for m in matches:
            metadata = m.metadata if hasattr(m, "metadata") else m["metadata"]
            text = metadata.get("text") or (m.id if hasattr(m, "id") else m["id"])  # fallback
            if not text and isinstance(metadata, dict):
                # Provide fallback using ID but we actually stored no text; we'll need to fetch differently
                text = ""
            context_parts.append(text)
            source_label = f"{metadata.get('source')} - Page {metadata.get('page')}"
            sources.append(source_label)

        context = "\n\n".join(context_parts)

        prompt = PROMPT_TEMPLATE.format(context=context, question=question)

        resp = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        answer_text = resp.choices[0].message.content.strip()

        return Response({"answer": answer_text, "sources": sources})


@extend_schema(
    request={'multipart/form-data': FileUploadSerializer},
    responses={200: MessageSerializer},
)
class UploadDocumentView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        ser = FileUploadSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=400)

        uploaded_file = ser.validated_data["file"]

        # Save to Document model
        doc = Document.objects.create(title=uploaded_file.name, file=uploaded_file)

        # Ingest asynchronously? For demo, do sync ingest.
        file_path = doc.file.path
        from knowledge.ingest import ingest_document

        ingest_document(file_path, source_name=uploaded_file.name)

        return Response({"detail": "File uploaded and ingested."}) 