""".. include:: README.md

This engine is used to fetch data from the database (multiple pandas dataframes).
In general this engine should be replaced by your SQL engine.
"""

from datetime import datetime

import pandas as pd

from core.llmbackend.llm_backend import GptBackend, LlmBackend
from core.llmbackend.prompts.dataeng_prompt import DATAENG_PROMPT, DATAENG_TOOLS
from core.readers.db_schema import (
    schema_creditcard_costs,
    schema_external_costs,
    schema_net_income,
    schema_profits,
    schema_revenues,
    schema_service_costs,
    schema_transactions,
)
from core.readers.xlsx_readers import (
    fetch_creditcard_costs,
    fetch_external_costs,
    fetch_net_income,
    fetch_profits,
    fetch_revenues,
    fetch_service_costs,
    fetch_transactions,
)
from core.settings.settings import Settings
from core.utils import are_similar, clean_columns_names, find_closest_str, read_tooled_response


class DbQueryEngine:
    """This class is used to query the mock database.

    Database tables are represented by individual dataframes each having their own schema.
    A query is fullfilled by the request_tunnel() method which returns a single dataframe.
    An agent is tasked to find which tables, rows and columns to fetch from the database.

    Attributes:
        table_router (dict): a hashmap containing all tables of the mock database (pandas dataframe)
        with keys being the name of the table, values are the tables themselves.
    """

    def __init__(self, llm: LlmBackend) -> None:
        self.llm = llm
        # structured data are preloaded and set in a router hashmap at instantiation
        self.table_router = {
            schema_transactions["table_name"]: fetch_transactions(),
            schema_revenues["table_name"]: fetch_revenues(),
            schema_service_costs["table_name"]: fetch_service_costs(),
            schema_creditcard_costs["table_name"]: fetch_creditcard_costs(),
            schema_profits["table_name"]: fetch_profits(),
            schema_external_costs["table_name"]: fetch_external_costs(),
            schema_net_income["table_name"]: fetch_net_income(),
        }
        self.tables_names = list(self.table_router.keys())

    # =============================================================================
    # user functions
    # =============================================================================
    def request_tunnel(self, query: str) -> tuple[pd.DataFrame, str]:
        """Request data from a user query."""
        # Agent finds which table, rows and columns to request
        data_request = self.llm.get_completion(
            query=query, primer_prompt=DATAENG_PROMPT, tools=DATAENG_TOOLS
        )
        # Cleaning and correcting llm response
        table_name, columns, start_date, end_date = self._parse_llm_response(data_request)

        # Request the data
        requested_data, table_name = self._request(table_name, columns, start_date, end_date)
        return requested_data, table_name

    # =============================================================================
    # internal functions
    # =============================================================================
    def _request(
        self, table_name: str, columns: list[str], start_date: datetime, end_date: datetime
    ) -> pd.DataFrame | str:
        """Fullfills a simple request on a single pandas dataframe

        Argument of the request serve to identify which table to read from.
        Table name, columns and dates serve are infered from the query dictionnary.
        The columns, start and end date serve as filter to generete the output dataframe.

        If the table is not found, the closest table name is used.
        If the columns are not found, the closest column names are used.

        Args:
            table_name (str): name of the table from which to request data
            columns (list[str]): list of columns to request. ["all"] for all.
            start_date (datetime): yyyy-mm-dd start time
            end_date (datetime): yyyy-mm-dd end time

        Returns:
            pd.DataFrame containing the filtered values
            str containing the name of the table
        """
        # pick the requested dataframe after correcting table name
        if table_name not in self.table_router:
            table_name = find_closest_str(table_name, self.tables_names)
        dataframe = self.table_router[table_name]

        # filter by columns and dates
        try:
            # if "all" is in the columns list, we return the whole dataframe
            if any(are_similar(column, "all") for column in columns):
                values = dataframe.loc[start_date:end_date]
            else:
                columns = clean_columns_names(columns, dataframe.columns)
                values = dataframe[columns].loc[start_date:end_date]
        except Exception:
            msg = (
                f"Requested columns {columns} not in table. Existing columns "
                f"are {dataframe.columns}"
            )
            raise msg from ValueError
        return values, table_name

    def _parse_llm_response(self, query: dict) -> tuple[str, list[str], datetime, datetime]:
        """Clean the user query to match the requet() input

        Note that we expect the LLM to send a query must be json formatted,
        e.g.,   {
                "table_name": name of the table (str),
                "columns": names of the columns (list of str),
                "start_date": start datetime (str yyyy-mm-dd),
                "end_date": end datetime (str yyyy-mm-dd)
                }
        """
        # parse llm response in a dictionnary
        try:
            formatted_query = read_tooled_response(query)
        except Exception:
            msg = "Invalid _request: json not formatted correctly"
            raise msg from ValueError

        # parse table name as a str
        try:
            table = formatted_query["arguments"]["table_name"]
        except Exception:
            msg = "Invalid _request: tables names must be a strings"
            raise msg from ValueError

        # parse column names as a list[str]
        try:
            columns = formatted_query["arguments"]["columns"]
        except Exception:
            msg = "Invalid _request: columns names must be a list of strings"
            raise msg from ValueError
        if isinstance(columns, str):
            columns = [columns]

        # parse start and end date
        try:
            start_date = pd.to_datetime(formatted_query["arguments"]["start_date"])
        except Exception:
            start_date = pd.to_datetime("2022-01-01")

        try:
            end_date = pd.to_datetime(formatted_query["arguments"]["end_date"])
        except Exception:
            end_date = pd.to_datetime("2023-12-31")

        return table, columns, start_date, end_date


if __name__ == "__main__":
    _llm = GptBackend(settings=Settings())
    engine = DbQueryEngine(_llm)

    _query = "What is the highest source of credit card cost in 2023 ?"
    resp = engine.request_tunnel(_query)
    print(resp)  # noqa: T201
