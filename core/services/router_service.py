""".. include:: README.md"""

from core.llmbackend.llm_backend import LlmBackend
from core.llmbackend.prompts.routing_prompts import ROUTING_PROMPT


class RouterService:
    """A simple agent to route user queries to the right pipeline.

    Args:
        llm (LlmBackend): llm backend to use for routing.
    """

    def __init__(self, llm: LlmBackend) -> None:
        self.llm = llm

    def route(self, query: str) -> str:
        """Route user query to the proper pipeline.

        Args:
            query (str): User input query

        Returns:
            str: pipeline name
        """
        pipeline = self.llm.get_completion(query=query, primer_prompt=ROUTING_PROMPT)
        return pipeline


if __name__ == "__main__":
    pass
