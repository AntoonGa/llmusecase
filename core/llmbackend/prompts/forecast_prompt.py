""".. include:: README.md

Prompt for the forecasting agent
"""
from core.llmbackend.llm_backend import GptBackend

FORECAST_QUERY = """
# Customer query:
{query}
"""

FORECAST_PROMPT = """
# You are an expert in data forecasting.
Our customer will request us to create a forecast for them.
Your task is to understand if the user wishes to generate an optimisic, pessimistic and mosty-likely
forecast.
# In case of doubt, return the mosty-likely forecast.

# You may only choose one of the following:

optimisic
pessimistic
mosty-likely

Only return the forecast. Do not answer the question. Your answer will be passed into our
forecasting engine.
This engine only accepts the following strings:
optimisic
pessimistic
mosty-likely

# API documentation example:
query: "I need to see a Prophet forcast of my credit card fees for 2024"
response: mosty-likely

query: "Display a pessimistic ARIMA forecast of my credit card fees for 2024"
response: pessimistic

query: "My boss needs an optimistic forecast of our profits for the whole season"
response: optimisic

query: "Display a worst-case scenario forecast of this dataset"
response: pessimistic
"""

if __name__ == "__main__":
    from core.settings.settings import Settings

    ENV = Settings()
    gpt = GptBackend(settings=ENV)

    _system_function = "You are an efficient assistant.."
    _query = FORECAST_QUERY.replace("{query}", "show me a forecast of the transaction composition.")
    response = gpt.get_completion(query=FORECAST_QUERY, primer_prompt=FORECAST_PROMPT)
    print(response)  # noqa: T201
