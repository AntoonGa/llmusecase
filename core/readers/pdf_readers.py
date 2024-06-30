""".. include:: README.md

Simple parser, chunker and embedder for pdf files using pymupdf.
Parsing can be improved in many ways, this is just an example.

Area of improvement:
- First line of each page is always the title book title or chapter title, use this to add
metadata to the output.
- quadrule k's are present when text is inside a box
- full-text pages contain almost always less than 500 tokens, which could be an upper limit for
the chunk size if it needed be dynamic
"""

import pandas as pd
import pymupdf
from tqdm import tqdm

from core.llmbackend.embedder_backend import AdaBackend, EmbedderBackend
from core.readers.rag_schema import RagSchema
from core.settings.settings import Settings
from core.utils import are_similar


# =============================================================================
# user functions
# =============================================================================
def pdf_ingestion_pipeline(
    file_path: str,
    save_path: str,
    embedder: EmbedderBackend,
    min_len: int = 500,
    max_len: int = 700,
) -> pd.DataFrame:
    """Pipeline for ingesting pdf files.

    Args:
        max_len (int): maximum size of chunks in characters
        min_len (int): minimum size of chunks in characters
        file_path (str): Path to your pdf file
        save_path (str): Path to save your output dataframe containing chunks, metas and embeddings
        embedder (Any): Embeddings engine. Must implement the `encode` method

    Returns:
        pd.DataFrame: Output dataframe containing chunks, metas and embeddings.
        This dataframe follows the RagSchema
    """
    pages = _parse_pages(file_path=file_path)
    chunks = _chunk_pages(pages=pages, min_len=min_len, max_len=max_len)
    final = _embed_chunks(chunks=chunks, embedder=embedder)
    save_df(df=final, file_path=save_path)
    return final


# =============================================================================
# support functions
# =============================================================================

PAGE_START = 26
PAGE_END = 592
NEW_CHAPTER_MARK = "CHAPTER INTRODUCTION"
BOOK_TITLE = "Financial Planning & Analysis and Performance Management"
DROP_PAGE_MARKS = ["TABLE", "FIGURE", "Trim Size"]


def _parse_pages(file_path: str) -> pd.DataFrame:
    """Parse pdf into pages and return as a dataframe.

    This ignores pages that are out of bounds.
    This removes chapters and book names on top of pages.
    This removes pages containing a figure, table or noisy box data
    """
    output_pages = {
        RagSchema.DOC_ID: [],
        RagSchema.PAGE: [],
        RagSchema.PAGE_METADATA: [],
        RagSchema.PAGE_NUMBER: [],
    }

    with pymupdf.open(file_path) as doc:
        pages = [page.get_text() for page in doc]

    current_chapter = "INTRODUCTION"
    for idx, page in enumerate(pages):
        # ignore out of bound pages
        if idx < PAGE_START or idx > PAGE_END:
            continue
        # define the current chapter (for metadata)
        if NEW_CHAPTER_MARK in page:
            current_chapter = page.split(NEW_CHAPTER_MARK)[0].strip()
            current_chapter = current_chapter.split("\n")[1:]
            current_chapter = " ".join(current_chapter).lower()

        # strip current page of chapter and book title
        cleaned_page = []
        current_page = page.split("\n")
        current_page = [line for line in current_page if line != ""]
        for line in current_page:
            if are_similar(line, BOOK_TITLE, threshold=0.8):
                continue
            if are_similar(line, current_chapter, threshold=0.8):
                continue
            cleaned_page.append(line)
        # group into pages
        cleaned_page = "\n".join(cleaned_page)
        # drop empty pages
        if len(cleaned_page) == 0:
            continue
        # drop pages containing drop marks
        if any(mark in cleaned_page for mark in DROP_PAGE_MARKS):
            continue

        output_pages[RagSchema.DOC_ID].append(0)
        output_pages[RagSchema.PAGE].append(cleaned_page)
        output_pages[RagSchema.PAGE_METADATA].append(current_chapter)
        output_pages[RagSchema.PAGE_NUMBER].append(idx)

    # convert to dataframe
    output_pages = pd.DataFrame.from_dict(output_pages, orient="columns")
    return output_pages


def _chunk_pages(pages: pd.DataFrame, min_len: int = 500, max_len: int = 700) -> pd.DataFrame:
    """Explode the page dataframe to add chunks.

    Chunks are created using the _split_string_approx() function.
    """
    output_chunks = {
        RagSchema.DOC_ID: [],
        RagSchema.PAGE_METADATA: [],
        RagSchema.PAGE_NUMBER: [],
        RagSchema.CHUNK: [],
        RagSchema.CHUNK_LENGTH: [],
    }

    for row in pages.iterrows():
        chunk_list = _split_string_approx(row[1][RagSchema.PAGE], min_len, max_len)
        for chunk in chunk_list:
            output_chunks[RagSchema.DOC_ID].append(row[1][RagSchema.DOC_ID])
            output_chunks[RagSchema.PAGE_METADATA].append(row[1][RagSchema.PAGE_METADATA])
            output_chunks[RagSchema.PAGE_NUMBER].append(row[1][RagSchema.PAGE_NUMBER])
            output_chunks[RagSchema.CHUNK].append(chunk)
            output_chunks[RagSchema.CHUNK_LENGTH].append(len(chunk))

    output_chunks = pd.DataFrame.from_dict(output_chunks, orient="columns")
    return output_chunks


def _split_string_approx(text: str, min_length: int = 500, max_length: int = 700) -> list[str]:
    """Cut a string into chunks.

    The function attempts to cut at triple, double and single linebreaks with priority in this
    order. This is just an attempt at replacing Lanchain's text splitters
    """
    chunks = []
    start = 0
    end = max_length

    while start < len(text):
        if end < len(text):
            # Find the nearest triple, double, or single line break within specified length range
            triple_break = text.rfind("\n\n\n", start, end)
            double_break = text.rfind("\n\n", start, end)
            single_break = text.rfind("\n", start, end)

            if triple_break != -1 and triple_break - start >= min_length:
                end = triple_break
            elif double_break != -1 and double_break - start >= min_length:
                end = double_break
            elif single_break != -1 and single_break - start >= min_length:
                end = single_break

        sliced_chunk = text[start:end].strip()
        chunks.append(sliced_chunk)

        start = end
        end += max_length

    return chunks


def _embed_chunks(chunks: pd.DataFrame, embedder: EmbedderBackend) -> pd.DataFrame:
    """Add embeddings vectors to chunks dataframe.

    This function also computes the embeddings of metadata, and of metadata+chunk
    """
    output_embeddings = {
        RagSchema.DOC_ID: [],
        RagSchema.PAGE_METADATA: [],
        RagSchema.PAGE_NUMBER: [],
        RagSchema.CHUNK_ID: [],
        RagSchema.CHUNK: [],
        RagSchema.CHUNK_LENGTH: [],
        RagSchema.CHUNK_EMBEDDING: [],
        RagSchema.PAGE_METADATA_EMBEDDING: [],
        RagSchema.CHUNK_W_METADATA_EMBEDDING: [],
    }
    # iterate through rows and embed chunks, metadata and chunks + metadata
    for idx, row in tqdm(enumerate(chunks.iterrows())):
        # place misc values in output
        output_embeddings[RagSchema.DOC_ID].append(row[1][RagSchema.DOC_ID])
        output_embeddings[RagSchema.PAGE_METADATA].append(row[1][RagSchema.PAGE_METADATA])
        output_embeddings[RagSchema.PAGE_NUMBER].append(row[1][RagSchema.PAGE_NUMBER])
        output_embeddings[RagSchema.CHUNK_ID].append(idx)
        output_embeddings[RagSchema.CHUNK].append(row[1][RagSchema.CHUNK])
        output_embeddings[RagSchema.CHUNK_LENGTH].append(row[1][RagSchema.CHUNK_LENGTH])

        # embed chunk and place vector in output
        chunk_embedding = embedder.encode(row[1][RagSchema.CHUNK])
        output_embeddings[RagSchema.CHUNK_EMBEDDING].append(chunk_embedding)

        # embed metadata and place vector in output
        page_metadata_embedding = embedder.encode(row[1][RagSchema.PAGE_METADATA])
        output_embeddings[RagSchema.PAGE_METADATA_EMBEDDING].append(page_metadata_embedding)

        # embed chunk+metadata and place vector in output
        chunk_w_metadata = row[1][RagSchema.PAGE_METADATA] + "\n" + row[1][RagSchema.CHUNK]
        chunk_w_metadata_embedding = embedder.encode(chunk_w_metadata)
        output_embeddings[RagSchema.CHUNK_W_METADATA_EMBEDDING].append(chunk_w_metadata_embedding)

    output_embeddings = pd.DataFrame.from_dict(output_embeddings, orient="columns")
    return output_embeddings


def save_df(df: pd.DataFrame, file_path: str) -> None:
    """Save dataframe to parquet."""
    df.to_parquet(file_path, index=False, compression=None)


def load_df(file_path: str) -> pd.DataFrame:
    """Load dataframe from parquet."""
    loaded_df = pd.read_parquet(file_path)
    return loaded_df


if __name__ == "__main__":
    _file_path = r"data/book.pdf"
    _save_path = r"data/book_ada.parquet"
    _embedder = AdaBackend(settings=Settings())
    # _df = pdf_ingestion_pipeline(file_path=_file_path,
    #                              save_path=_save_path,  # noqa: ERA001
    #                              embedder=_embedder)
    _df = load_df(file_path=_save_path)
    print(_df)  # noqa: T201
