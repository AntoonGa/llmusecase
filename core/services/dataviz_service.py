""".. include:: README.md

Use this service to create simple data visualizations out of the database.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from core.llmbackend.llm_backend import LlmBackend
from core.llmbackend.prompts.dataviz_prompt import DATAVIZ_PROMPT, DATAVIZ_TOOLS
from core.services.db_query_service import DbQueryEngine
from core.utils import read_tooled_response


def dataviz_tunnel(query: str, llm: LlmBackend) -> tuple[pd.DataFrame, str, list[plt.Figure]]:
    """Run a simple dataviz pipeline from a user query.

    Args:
        query (str): user-input query in natural language
        llm (LlmBackend): backend llm

    Returns:
        requested_data: pd.DataFrame containing data from the query
        table_name: name of the pd.DataFrame
        figs: list of figure objects
        display_tools: tools used to generate the figures
    """
    # request data from db using the query service
    request_service = DbQueryEngine(llm)
    requested_data, table_name = request_service.request_tunnel(query)
    # find which dataviz function to call
    display_tools = llm.get_completion(
        query=query, primer_prompt=DATAVIZ_PROMPT, tools=DATAVIZ_TOOLS
    )

    # call the dataviz function with llm-generated arguments
    function_name = read_tooled_response(display_tools)["function_name"]
    function = globals().get(function_name)
    figs = function(requested_data, table_name)
    return requested_data, table_name, figs


def plot_timeseries(df: pd.DataFrame, title: str | None = None) -> list[plt.Figure]:
    """Generate a timeseries plot of the given data and returns a list of figure objects"""
    fig, ax = plt.subplots()

    if title:
        ax.set_title(title, fontsize=12)

    for column in df.columns:
        ax.plot(df.index, df[column], label=column)

    ax.legend()
    ax.set_xlabel("Value [a.u.]")
    ax.set_ylabel("Time [mo]")

    return [fig]


def display_histogram(df: pd.DataFrame, title: str | None = None) -> list[plt.Figure]:
    """Generate a histogram of the given data and returns a list of figure objects"""
    figures = []

    for column in df.columns:
        arr = np.array(df[column])
        # Set the number of bins using Sturge's rule +1
        n_bin = int(np.ceil(np.log2(len(arr))) + 2)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_title(f"{title}, {column}", fontsize=12)
        ax.hist(arr, bins=n_bin, edgecolor="black")
        ax.set_xlabel(f"Value of {column} [a.u]")
        ax.set_ylabel("Frequency")

        figures.append(fig)

    return figures


def display_pie_chart(df: pd.DataFrame, title: str | None = None) -> list[plt.Figure]:
    """Generate a pie chart of the given data and returns a list of figure objects"""
    figures = []

    for index, row in df.iterrows():
        abs_row = row[row != 0].abs()  # Use absolute values

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(abs_row, labels=abs_row.index, autopct="%1.1f%%", startangle=90)
        ax.set_title(f"{title}, {index}", fontsize=12)
        ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

        figures.append(fig)

    return figures
