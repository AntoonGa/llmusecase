""".. include:: README.md

Columns-holding class for the RAG pandas dataframe.
This class simply serves to avoid magic strings in code and help your IDE linter.
"""


class RagSchema:
    """This class hold the columns of the RAG data dataframes."""

    DOC_ID = "doc_id"
    PAGE = "page"
    PAGE_METADATA = "page_metadata"
    PAGE_NUMBER = "page_number"

    CHUNK_ID = "chunk_id"
    CHUNK = "chunk"
    CHUNK_EMBEDDING = "chunk_embedding"
    PAGE_METADATA_EMBEDDING = "page_metadata_embedding"
    CHUNK_W_METADATA_EMBEDDING = "chunk_with_metadata_embedding"
    CHUNK_LENGTH = "chunk_length"


if __name__ == "__main__":
    pass
