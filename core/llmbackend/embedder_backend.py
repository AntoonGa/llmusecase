""".. include:: README.md

Wrapper for embedding API (currently ony OpenAI Ada is implemented).
"""

import logging
import time
from abc import ABC, abstractmethod

import numpy as np
import openai

from core.settings.settings import Settings

MODELS = ["text-embedding-3-large", "text-embedding-ada-002"]
TIME_TO_RETRY = 0.05
MAX_RETRIES = 5


class EmbedderBackend(ABC):
    """Abstract class for embedding backends"""

    @abstractmethod
    def encode(self, query: str) -> np.ndarray | None:
        """Create an embedded vector of a string and return it as a numpy array"""
        raise NotImplementedError

    @abstractmethod
    def encode_list(self, strings: list[str]) -> list[np.ndarray | None]:
        """Embed all strings in a list."""
        raise NotImplementedError


class AdaBackend(EmbedderBackend):
    """backend to fetch embeddings from a string using openAI ada.

    Currently only supports Azure OpenAI deployments. If you wish to run on an OpenAI service,
    please change the self.client variable to your service.

    Args:
        model (str): choosen embedding model. Use only models deployed on the Azure service.
        list available models: MODELS
        settings (Settings): settings object containing your environment variables.

    Attributes:
        client (AzureOpenAI): client for Azure OpenAI API. The client is instantiated with
        your API credentials, contained in the Settings object.
    """

    def __init__(self, settings: Settings, model: str | None = None) -> None:
        if settings is None:
            error_message = "Settings object must be provided"
            logging.error(error_message)
            raise ValueError(error_message)

        # use default model if none is provided
        if model is None:
            model = settings.EMBEDDINGS_MODEL

        # check if model is valid
        if model not in MODELS:
            error_message = f"Invalid embedding model, use only: {MODELS}"
            logging.error(error_message)
            raise ValueError(error_message)

        # Azure deployment
        self.client = openai.AzureOpenAI(
            api_key=settings.OPENAI_API_KEY,
            api_version=settings.OPENAI_API_VERSION,
            azure_endpoint=settings.OPENAI_API_ENDPOINT,
        )
        self.model = model

    def encode(self, query: str) -> np.ndarray | None:
        """Create an embedded vector of a string and return it as a numpy array.

        Args:
            query (str): string to query

        Returns:
            np.ndarray or None: embedded string or None if the query is empty of if API failed
        """
        if not query:
            return None
        if not isinstance(query, str):
            return None
        if len(query) == 0:
            return None

        embeddings = None
        for retry in range(MAX_RETRIES):
            try:
                embeddings = self.client.embeddings.create(model=self.model, input=query)
                if embeddings:
                    break

            except Exception:
                logging.exception("API call failed")
                if retry == MAX_RETRIES - 1:
                    break

            # exponential wait between retries
            time.sleep(TIME_TO_RETRY * retry)

        if embeddings:
            return np.array(embeddings.data[0].embedding)
        return None

    def encode_list(self, strings: list[str]) -> list[np.ndarray | None]:
        """Embed all strings in a list."""
        return [self.encode(string) for string in strings]


if __name__ == "__main__":
    from core.settings.settings import Settings

    ENV = Settings()
    ada = AdaBackend(settings=ENV)

    _query = "What is the approximate number of dwellers in San Francisco?"
    response = ada.encode(query=_query)
    print(response)  # noqa: T201

    _list_query = ["", None, "hello", "my friend"]
    response = ada.encode_list(strings=_list_query)
    print(response)  # noqa: T201
