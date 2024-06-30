""".. include:: README.md

Generate split dataframes from the raw xlsx file provided.
The data is split into multiple dataframes representing various subsections such as cost,
infracost, profits, etc.
Data is transposed to represent the data as timeseries (time spans are set as index).
"""

import pandas as pd

from core.settings.settings import Settings

pd.set_option("future.no_silent_downcasting", True)
# we set this as a constant since a single file is used
XLSX_PATH = Settings().XLSX_PATH


def _read_xlsx() -> pd.DataFrame:
    """Read raw data from xlsx file.

    We transpose and set the index as datatime to represent the data as timeseries.
    """
    _df = pd.read_excel(XLSX_PATH, index_col=0)
    _df = _df.T
    _df.columns = _df.columns.str.lower()
    _df.columns = _df.columns.str.replace(" ", "_")
    _df = _df.rename(
        columns={
            "transactions": "total_transactions",
            "cost_of_services": "total_cost_of_services",
            "credit_card_fees": "total_credit_card_fees",
            "gross_profit": "total_gross_profit",
        }
    )
    _df.index = pd.to_datetime(_df.index, format="%b %y")
    _df = _df.apply(pd.to_numeric, errors="coerce")
    return _df.fillna(0.0)


def fetch_transactions() -> pd.DataFrame:
    """Filter and return transactions counts."""
    _df = _read_xlsx()
    transactions = _df.iloc[:, 1:11]
    return transactions


def fetch_revenues() -> pd.DataFrame:
    """Filter revenues data"""
    _df = _read_xlsx()
    revenues = _df.iloc[:, 11:21]
    return revenues


def fetch_service_costs() -> pd.DataFrame:
    """Filter service costs data"""
    _df = _read_xlsx()
    service_costs = _df.iloc[:, 21:31]
    return service_costs


def fetch_creditcard_costs() -> pd.DataFrame:
    """Filter creditcard costs data"""
    _df = _read_xlsx()
    creditcard_costs = _df.iloc[:, 31:41]
    return creditcard_costs


def fetch_profits() -> pd.DataFrame:
    """Filter profits data"""
    _df = _read_xlsx()
    profits = _df.iloc[:, 41:51]
    return profits


def fetch_external_costs() -> pd.DataFrame:
    """Filter external costs data"""
    _df = _read_xlsx()
    external_costs = _df.iloc[:, 51:57]
    return external_costs


def fetch_net_income() -> pd.DataFrame:
    """Filter net income data"""
    _df = _read_xlsx()
    net_income = _df[["ebitda"]]
    return net_income


if __name__ == "__main__":
    _transactions = fetch_transactions()
    _revenues = fetch_revenues()
    _service_costs = fetch_service_costs()
    _creditcard_costs = fetch_creditcard_costs()
    _profits = fetch_profits()
    _external_costs = fetch_external_costs()
    _net_income = fetch_net_income()
