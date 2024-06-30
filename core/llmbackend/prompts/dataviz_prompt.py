""".. include:: README.md

Prompts and tools for the data visualisation agent
"""
from core.llmbackend.llm_backend import GptBackend
from core.settings.settings import Settings
from core.utils import parse_json

DATAVIZ_PROMPT = """
# You are an expert in data visualization.

# Our customer will request us to create a chart for them.
Your task is to understand which APIs and tools will be required to generate the data visualization.
The data will be provided to other members ot the team who will create the visualisation.

# The list of available data visualisation are provided to you as an API documentation.

# Use only :the provided API to create the visualisation.
**plot_timeseries: usefull to plot timeseries, see trend, see evolutions.**
**display_histogram: usefull to see distributions**
**display_pie_chart: usefull to see composition, decomposition, see proportions. Note that pie
chart should never include the total value, but the values of each category.**

# Make sure to place keys and values in quotes.
"""

DATAVIZ_TOOLS = parse_json(Settings().DATAVIZ_TOOLS)

if __name__ == "__main__":
    from core.settings.settings import Settings

    ENV = Settings()
    gpt = GptBackend(settings=ENV)

    _system_function = "You are an efficient assistant.."
    _query = "show me a piechart of the transaction composition."
    response = gpt.get_completion(query=_query, primer_prompt=DATAVIZ_PROMPT, tools=DATAVIZ_TOOLS)
    print(response)  # noqa: T201
