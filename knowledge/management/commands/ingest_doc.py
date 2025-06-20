from django.core.management.base import BaseCommand, CommandParser
from knowledge.ingest import ingest_document


class Command(BaseCommand):
    help = "Ingest a document (PDF) into Pinecone index."

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("file_path", type=str, help="Path to PDF file")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        self.stdout.write(f"Ingesting {file_path} ...")
        ingest_document(file_path)
        self.stdout.write(self.style.SUCCESS("Done.")) 