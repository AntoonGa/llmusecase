""".. include:: README.md

Run this script once to prepare the data for RAG.
"""
from core.llmbackend.embedder_backend import AdaBackend
from core.readers.pdf_readers import pdf_ingestion_pipeline
from core.settings.settings import Settings

if __name__ == "__main__":
    save_path = r"data/ada3_1200len"
    pdf_path = r"data/book.pdf"
    ada3 = AdaBackend(settings=Settings())
    pdf_ingestion_pipeline(file_path=pdf_path, save_path=save_path, embedder=ada3, max_len=1200)
