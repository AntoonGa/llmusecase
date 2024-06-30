""".. include:: README.md

These are supporting functions to improve readability of the notebooks
"""

# Settings up the bunka pipeline
import pandas as pd
import umap
from bunkatopics import Bunka
from plotly.graph_objs import Figure
from sklearn.cluster import KMeans

from core.readers.pdf_readers import load_df


def format_to_bunka(
    chunks_df: pd.DataFrame, col_to_embed: str
) -> tuple[list[dict[str, str]], list, list[str]]:
    """Format the chunks to fit the Bunka API.

    Args:
        chunks_df (pd.DataFrame): dataframe containing the chunks and embeddings vectors
        col_to_embed (str): embeddings columns name
    """
    # preparing documents and embeddings WITHOUT METADATA
    docs = list(chunks_df["chunk"])
    embedding = list(chunks_df[col_to_embed])
    # if passing embeddings, bunka requires a list of ids... we fake it here
    ids = [str(ii) for ii in range(len(embedding))]
    # if passing embeddings, bunka requieres them as a list[dict]:
    bunka_formatted_embedding = [
        {"doc_id": str(ii), "embedding": embedding[ii]} for ii in range(len(embedding))
    ]

    return bunka_formatted_embedding, docs, ids


def bunka_viz(
    bunka_formatted_embedding: list[dict[str, str]], docs: list, ids: list[str]
) -> Figure:
    """Run umap projection, then kmean clustering"""
    # Setting up umap model
    projection_model = umap.UMAP(n_components=2, random_state=42)
    # Instantiate bunka object
    bunka = Bunka(embedding_model=None, projection_model=projection_model)
    # cluster topics and define topics names
    clustering_model = KMeans(n_clusters=10)
    # fit the model
    bunka.fit(docs=docs, ids=ids, pre_computed_embeddings=bunka_formatted_embedding)
    bunka.get_topics(name_length=10, custom_clustering_model=clustering_model)
    # visualize topics
    fig = bunka.visualize_topics(width=900, height=900, colorscale="Blues")
    return fig


def bunka_pipeline(file_path: str) -> None:
    """Runs the entire pipeline on chunk and chunk+metadata embeddings"""
    title = {"text": None, "y": 0.05, "x": 0.5, "xanchor": "center", "yanchor": "top"}
    chunks_df = load_df(file_path)

    # create umap visualisation on chunk embeddings
    title["text"] = f"{file_path} | chunk_embedding"
    formatted_vectors, docs, ids = format_to_bunka(chunks_df, "chunk_embedding")
    fig = bunka_viz(formatted_vectors, docs, ids)
    fig.update_layout(title=title)
    fig.show()

    # create umap visualisation on chunk+metadata embeddings
    title["text"] = f"{file_path} | chunk_with_metadata_embedding"
    formatted_vectors, docs, ids = format_to_bunka(chunks_df, "chunk_with_metadata_embedding")
    fig = bunka_viz(formatted_vectors, docs, ids)
    fig.update_layout(title=title)
    fig.show()


if __name__ == "__main__":
    pass
