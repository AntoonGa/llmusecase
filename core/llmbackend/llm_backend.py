""".. include:: README.md

Wrapper for llm calling API (currently only OpenAI implementation).
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any

import openai

from core.settings.settings import Settings

MODELS = ["gpt-35-turbo-16k", "gpt-4"]
TEMPERATURE = 0.000000001  # This tends to be more stable than zero...
TOP_P = 0.95
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0
STOP = None
REQUEST_TIMEOUT = 30
TIME_TO_RETRY = 0.05
MAX_RETRIES = 5


class LlmBackend(ABC):
    """Abstract class for llm backends.

    All child must implement the get_completion public method.
    """

    @abstractmethod
    def get_completion(
        self, query: str, primer_prompt: str, tools: dict | None = None
    ) -> str | Any:
        """Send message to the llm and receive the response

        This method follows the standard openAI API format:
        The query is a string containing the query to send to the llm.
        The primer_prompt is a string used to "prime" the model (system prompt).
        Optionnal tools are dictionnaries describing an external API that the llm must "use".

        The response is a string containing the response of the llm or a "Function" object if
        the llm is using the tools.

        Args:
            query (str): main query string
            primer_prompt (str): system or "primer" query string
            tools (Optional[dict]): dictionnary describing an external API

        Returns:
            str | dict: response of the llm
        """
        msg = "Please implement the get_completion method"
        raise msg from NotImplementedError


class GptBackend(LlmBackend):
    """backend for simple queries with the OpanAI GPT llm. Use only: get_completion

    Currently only supports Azure OpenAI deployments. If you wish to run on an OpenAI service,
    please change the self.client variable to your service.

    Args:
        max_token_in_response (int): maximum number of tokens in the response.
        settings (Settings): settings object containing your environment variables.

    Attributes:
        client (AzureOpenAI): client for Azure OpenAI API. The client is instantiated with
        your API credentials, contained in the Settings object.
    """

    def __init__(
        self,
        max_token_in_response: int = 500,
        settings: Settings = None,
        llm_model: str | None = None,
    ) -> None:
        if settings is None:
            error_message = "Settings object is required"
            logging.error(error_message)
            raise ValueError(error_message)

        # overwrite default model
        if llm_model is None:
            llm_model = settings.LLM_MODEL

        # check llm model
        if llm_model not in MODELS:
            error_message = f"Invalid GPT llm_model, use only: {MODELS}"
            logging.error(error_message)
            raise ValueError(error_message)

        # Azure deployment
        self.client = openai.AzureOpenAI(
            api_key=settings.OPENAI_API_KEY,
            api_version=settings.OPENAI_API_VERSION,
            azure_endpoint=settings.OPENAI_API_ENDPOINT,
        )

        # get llm chatbot model
        self.model = llm_model
        self.max_tokens = max_token_in_response

    # =============================================================================
    # user functions
    # =============================================================================
    def get_completion(
        self, query: str, primer_prompt: str, tools: dict | None = None
    ) -> str | Any:
        """Send message to the llm and receive the response"""
        payload = self._make_payload(query, primer_prompt)
        response_message = self._send_payload(payload, tools)
        return response_message

    # =============================================================================
    # internal functions
    # =============================================================================
    def _make_payload(self, query: str, system_function: str) -> list[dict]:
        """Generate the payload list[hashmap] according to openAI format"""
        payload = [
            {"role": "system", "content": system_function},
            {"role": "user", "content": query},
        ]
        return payload

    def _send_payload(self, payload: list[dict], tools: dict | None = None) -> str | Any:
        """Send payload via API .create() function. The response is a string or a "Function".

        This function will retry several times if the API call fails, using time sleeps
        between retries.

        Args:
            payload (list[dict]): payload list generated by _make_payload
            tools (dict | None, optional): OpenAI tools. Defaults to None.

        Returns:
            str: response of the llm
        """
        response_string = ""
        tools_call = None
        if tools:
            tools_call = "auto"

        for retry in range(MAX_RETRIES):
            try:
                rsp = self.client.chat.completions.create(
                    model=self.model,
                    messages=payload,
                    tools=tools,
                    tool_choice=tools_call,
                    temperature=TEMPERATURE,
                    max_tokens=self.max_tokens,
                    top_p=TOP_P,
                    frequency_penalty=FREQUENCY_PENALTY,
                    presence_penalty=PRESENCE_PENALTY,
                    stop=STOP,
                    timeout=REQUEST_TIMEOUT,
                )
                if tools_call is None:
                    response_string = rsp.choices[0].message.content
                else:
                    response_string = rsp.choices[0].message.tool_calls[0].function
                # exit the retry loop if the llm response is not None
                if response_string:
                    break
                # force pause for API safety
                time.sleep(TIME_TO_RETRY)

            except Exception as exc:
                logging.exception("API call failed")
                if retry == MAX_RETRIES - 1:
                    msg = f"API call failed after {MAX_RETRIES} retries."
                    raise RuntimeError(msg) from exc
                # wait before retrying
                time.sleep(TIME_TO_RETRY * retry)
        return response_string


if __name__ == "__main__":
    from core.settings.settings import Settings

    ENV = Settings()
    gpt = GptBackend(settings=ENV)

    _system_function = "You are an efficient assistant.."
    _query = "What is the approximate number of dwellers in San Francisco?"
    response = gpt.get_completion(query=_query, primer_prompt=_system_function)
    print(response)  # noqa: T201
