""".. include:: README.md

Use this engine to generate forcast on data.
In general this engine would be your ML pipeline APIs.
"""

import time
import warnings

import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from core.llmbackend.llm_backend import LlmBackend
from core.llmbackend.prompts.forecast_prompt import FORECAST_PROMPT, FORECAST_QUERY
from core.services.db_query_service import DbQueryEngine
from core.utils import are_similar

warnings.filterwarnings("ignore")

SCENARIOS = ["mosty-likely", "pessimistic", "optimistic"]


class ForecastService:
    """Time-series forcasting agent using ARIMA.

    The query agent is tasked to find which tables, columns and rows to fetch.
    A second agent is tasked to choose the forecasting scenario.

    Args:
        llm (LlmBackend): llm backend

    Attributes:
        llm (LlmBackend): llm backend
        db_query_engine (DbQueryEngine): db query engine
        scenarios (list[str]): list of scenarios
    """

    def __init__(self, llm: LlmBackend) -> None:
        self.llm = llm
        self.db_query_engine = DbQueryEngine(self.llm)
        self.scenarios = SCENARIOS

    def forecast_tunnel(self, query: str) -> tuple[pd.DataFrame, str, list[plt.Figure]]:
        """Run the entire forecasting pipeline from a user query."""
        # Use the data engine to request data from the user query
        requested_data, table_name = self.db_query_engine.request_tunnel(query)
        # Use the forecasting agent to choose between forcasting scenarios
        scenario = self._get_scenario(query=query)
        # Call the ARIMA forecast function
        figs = self._arima_forecast_and_plot(
            df=requested_data, title=table_name, steps=10, scenario=scenario
        )
        return requested_data, table_name, figs

    def _get_scenario(self, query: str) -> str:
        """Get the scenario from the user query."""
        forecast_query = FORECAST_QUERY.replace("{query}", query)
        scenario = self.llm.get_completion(query=forecast_query, primer_prompt=FORECAST_PROMPT)
        if are_similar(scenario, self.scenarios[0]):
            scenario = self.scenarios[0]
        elif are_similar(scenario, self.scenarios[1]):
            scenario = self.scenarios[1]
        elif are_similar(scenario, self.scenarios[2]):
            scenario = self.scenarios[2]
        else:
            scenario = self.scenarios[0]
        return scenario

    def _arima_forecast_and_plot(
        self,
        df: pd.DataFrame,
        title: str | None = None,
        steps: int = 5,
        scenario: str = SCENARIOS[0],
    ) -> list[plt.Figure]:
        """ARIMA forecast for each column and returns a list of figure objects."""
        figures = []

        for column in df.columns:
            # Fit the ARIMA model
            data = df[column].dropna()
            model = ARIMA(data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
            model_fit = model.fit()

            # Make forecast
            forecast_result = model_fit.get_forecast(steps=steps)
            forecast = forecast_result.predicted_mean
            conf_int = forecast_result.conf_int()

            # Pick the scenario-related data
            if scenario == self.scenarios[1]:
                forecast = conf_int.iloc[:, 0]
            elif scenario == self.scenarios[2]:
                forecast = conf_int.iloc[:, 1]

            # Plot the forecast
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.set_title(f"ARIMA Forecast of {title}: {column} | {scenario}", fontsize=12)
            ax.plot(data, label="Observed")
            ax.plot(forecast, label="Forecast", color="red")
            ax.fill_between(
                conf_int.index, conf_int.iloc[:, 0], conf_int.iloc[:, 1], color="pink", alpha=0.3
            )
            ax.set_xlabel("Time [mo]")
            ax.set_ylabel("Value [a.u.]")
            ax.legend()

            figures.append(fig)

            # this sleep is required because displaying too fast seems to kill my pc
            time.sleep(0.1)

        return figures
