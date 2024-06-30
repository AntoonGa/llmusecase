"""Used to store private and public env variables and enables the linter to know the variables.

You should access env variable from this object only (rather than do get.env())

How to use:
- add env variables to your secrets.env or public.env
- secrets.env should never be commited/pushed to git (contains secrets)
- public.env should be commited/pushed to git
- in this class, add the env variable and assign it to the object
- after loading in post init, Settings will read the env variable and assign it to the object
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


class SingletonMeta(type):
    """Singleton metaclass

    Class inheriting from this one will be a singleton.
    Singletons can only be instantiated once.
    """

    _instances = {}  # noqa: RUF012

    def __call__(cls, *args, **kwargs) -> "SingletonMeta":  # noqa: D102
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


@dataclass
class Settings(metaclass=SingletonMeta):
    """Settings class

    This object is used to store private and public env variables.
    This has the added benefit of enabling the linter to know which variables exist.

    This class can be used as a singleton.

    Arg:
        secrets_path (str): path to .env files
        public_path (str): path to .env files
    """

    secrets_path: str = r"core/settings/secrets.env"
    public_path: str = r"core/settings/public.env"

    def __post_init__(self) -> None:
        """After init, read the env variable and assign it to the object"""
        # assign private and public variables to environment variables
        load_dotenv(self.secrets_path)
        load_dotenv(self.public_path)
        # secrets
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_API_ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
        self.OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
        self.OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE")
        if self.OPENAI_API_KEY is None:
            msg = "OPENAI_API_KEY is not set"
            raise ValueError(msg)
        if self.OPENAI_API_ENDPOINT is None:
            msg = "OPENAI_API_ENDPOINT is not set"
            raise ValueError(msg)
        if self.OPENAI_API_VERSION is None:
            msg = "OPENAI_API_VERSION is not set"
            raise ValueError(msg)
        if self.OPENAI_API_TYPE is None:
            msg = "OPENAI_API_TYPE is not set"
            raise ValueError(msg)
        # repo-wide config
        self.EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL")
        self.LLM_MODEL = os.getenv("LLM_MODEL")
        self.VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH")
        self.XLSX_PATH = os.getenv("XLSX_PATH")
        self.DE_PROMPT = os.getenv("DE_PROMPT")
        self.DE_TOOLS = os.getenv("DE_TOOLS")
        self.DATAVIZ_PROMPT = os.getenv("DATAVIZ_PROMPT")
        self.DATAVIZ_TOOLS = os.getenv("DATAVIZ_TOOLS")
        self.FORECAST_PROMPT = os.getenv("FORECAST_PROMPT")
        self.RAG_PROMPT = os.getenv("RAG_PROMPT")


if __name__ == "__main__":
    config = Settings()
    # access the object using its instance.attribute
    print(config.OPENAI_API_ENDPOINT)  # noqa: T201
    # instantiation of a second object yields the same object (singleton)
    config2 = Settings()
    print(id(config), id(config2))  # noqa: T201
