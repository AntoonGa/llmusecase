""".. include:: README.md

Pipelines are the core of the application.
They use the services APIs (which would be your backend APIs) to generate forcasts,
and dataviz.
The pipelines are called by the Router agents. Each pipeline may use an LLM to generate the correct
requests on your backend APIs.

Add more pipelines as you see fit, make sure to implement their requiered backend functions and
add the pipeline list and description to the prompt of the routing LLM.

A pipeline must return an instance of the OrderData class which contains all the relevent
This Dataclass acts as the payload and response of a REST API. It contains all the relevant
information to the user. You must use this OrderData class to display the results in your UI.
"""

from dataclasses import dataclass
from typing import Optional

import pandas as pd
from matplotlib import pyplot as plt

from core.llmbackend.embedder_backend import AdaBackend
from core.llmbackend.llm_backend import GptBackend
from core.services.dataviz_service import (  # noqa: F401
    dataviz_tunnel,
    display_histogram,
    display_pie_chart,
    plot_timeseries,
)
from core.services.db_query_service import DbQueryEngine
from core.services.forecast_service import ForecastService
from core.services.rag_service import RagService
from core.services.router_service import RouterService
from core.settings.settings import Settings
from core.utils import are_similar

LLM = GptBackend(settings=Settings())
EMBEDDER = AdaBackend(settings=Settings())
DB_QUERY_ENGINE = DbQueryEngine(LLM)
VECTOR_STORE_PATH = Settings().VECTOR_STORE_PATH


@dataclass
class OrderData:
    """Dataclass containing the input and output of the pipelines.

    Each pipeline must return an instance of this class.
    """

    user_query: Optional[str] = None
    llm_response: Optional[str] = None
    table: Optional[pd.DataFrame] = None
    table_name: Optional[str] = None
    figure: Optional[list[plt.figure]] = None
    figure_name: Optional[str] = None
    pipeline_name: Optional[str] = None

    def __repr__(self) -> str:
        """Representation of the class, also prints the figures"""
        _repr = f"Pipeline name: {self.pipeline_name}\n"
        _repr += f"User query: {self.user_query}\n"
        _repr += "*_" * 55 + "\n"
        if self.llm_response:
            _repr += f"LLM response:\n{self.llm_response}\n"
            _repr += "*_" * 55 + "\n"
        if self.table_name:
            _repr += f"Table name:\n{self.table_name}\n"
            _repr += "\n" + str(self.table) + "\n"
            _repr += "*_" * 55 + "\n"
        # plots eventual figures
        if self.figure:
            _repr += f"\n Figure: {self.figure}"
            for fig in self.figure:
                fig.show()
        return _repr


def run_system(query: str) -> OrderData:
    """Entry point for the entire system.

    Calls the llm routing agent and calls the appropriate pipeline using the routing agent response.

    Args:
        query (str): user-input query

    Returns:
        OrderData: response from the pipeline
    """
    router = RouterService(LLM)
    pipe = router.route(query)

    order_data = OrderData(user_query=query, pipeline_name=pipe)
    order_data = call_pipeline(order_data)
    return order_data


def call_pipeline(order_data: OrderData) -> OrderData:
    """Call the appropriate pipeline using the routing agent response.

    These pipelines must fill and return the OrderData class.
    The pipelines are selected using the routing agent response (with fuzzy matching).
    """
    if are_similar(order_data.pipeline_name, "spam"):
        order_data = _spam_pipeline(order_data)
    elif are_similar(order_data.pipeline_name, "analyst"):
        order_data = _forecast_pipeline(order_data)
    elif are_similar(order_data.pipeline_name, "data engineering"):
        order_data = _request_data(order_data)
    elif are_similar(order_data.pipeline_name, "data visualization"):
        order_data = _dataviz_pipeline(order_data)
    elif are_similar(order_data.pipeline_name, "financial consulting"):
        order_data = _rag_pipeline(order_data)
    else:
        order_data.pipeline_name = "Requested service not found"
    return order_data


##########################
# PIPELINES, IMPLEMENTED #
##########################
def _forecast_pipeline(order_data: OrderData) -> OrderData:
    """Run the entire forecasting pipeline from a user query."""
    # request data
    forecast_service = ForecastService(LLM)
    query = order_data.user_query
    requested_data, table_name, figs = forecast_service.forecast_tunnel(query)
    # fills the OrderData class
    order_data.llm_response = "Past Performance is Not Indicative of Future Results."
    order_data.table = requested_data
    order_data.table_name = table_name
    order_data.figure = figs
    return order_data


def _dataviz_pipeline(order_data: OrderData) -> OrderData:
    """Run a simple dataviz pipeline from a user query."""
    # request data
    query = order_data.user_query
    requested_data, table_name, figs = dataviz_tunnel(query, LLM)
    # fills the OrderData class
    order_data.table = requested_data
    order_data.table_name = table_name
    order_data.figure = figs
    return order_data


def _request_data(order_data: OrderData) -> OrderData:
    """Request data from a user query."""
    # request data
    query = order_data.user_query
    request_service = DbQueryEngine(LLM)
    requested_data, table_name = request_service.request_tunnel(query)
    # fills the OrderData class
    order_data.table = requested_data
    order_data.table_name = table_name
    return order_data


def _rag_pipeline(order_data: OrderData) -> OrderData:
    """Call the RAG pipeline."""
    # request data
    query = order_data.user_query
    rag_service = RagService(embedder=EMBEDDER, llm=LLM, vector_store_path=VECTOR_STORE_PATH)
    agent_answer = rag_service.rag_tunnel(query=query)
    # fills the OrderData class
    order_data.llm_response = agent_answer
    return order_data


def _spam_pipeline(order_data: OrderData) -> OrderData:
    """Spam pipeline."""
    order_data.llm_response = "Please do not spam me"
    return order_data


if __name__ == "__main__":
    _query = "Explain me the concept of ROI and PNL"
    _resp = run_system(query=_query)
    print(_resp)  # noqa: T201
    _query = "Show me the time evolution of our total profits. Take the entire data."
    _resp = run_system(query=_query)
    print(_resp)  # noqa: T201
    _query = "Show me the forecast of our total profits. Take the entire data. optimistic scenario"
    _resp = run_system(query=_query)
    print(_resp)  # noqa: T201
    _query = (
        "I want to see the composition of our credit card costs, without the total cost, "
        "for may 2022."
    )
    _resp = run_system(query=_query)
    print(_resp)  # noqa: T201
    _query = "I need a histogram of the number of transactions in the small business in 2022."
    _resp = run_system(query=_query)
    print(_resp)  # noqa: T201
    _query = "WAZAAAAA"
    _resp = run_system(query=_query)
    print(_resp)  # noqa: T201
