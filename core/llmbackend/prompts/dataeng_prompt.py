""".. include:: README.md

Prompt for the "Data Eng" LLM.
This prompt will serve to interpret queries from the user and return the columns, table,
and datetimes requested by the user.

"""
from core.llmbackend.llm_backend import GptBackend
from core.readers.db_schema import (
    schema_creditcard_costs,
    schema_external_costs,
    schema_net_income,
    schema_profits,
    schema_revenues,
    schema_service_costs,
    schema_transactions,
)
from core.settings.settings import Settings
from core.utils import parse_json

system_prefix = """
# Your task is to identify which data is required to answer the query.
The query will be answered by our specialists and analytics teams.
Your task is only to provide the requested data using our APIs.
Your task is not to answer the query.
To provide the data you must use our database API.

# **Company accounting database schema**
The following is a description of the company accounting database tables schemas
This database is composed of multiple tables each describing different cost and revenue centers.
Columns describe types and domains of activity, rows span monthly from January 2022 to December
2023.
# This database needs to be accessed by our costumers using its API.
Customers generally request data for visualisation, forecasting or analysis.
"""

system_schema = f"""
**
{schema_transactions["table_name"]} : {schema_transactions}
**
{schema_revenues["table_name"]} : {schema_revenues}
**
{schema_service_costs["table_name"]} : {schema_service_costs}
**
{schema_creditcard_costs["table_name"]} : {schema_creditcard_costs}
**
{schema_profits["table_name"]} : {schema_profits}
**
{schema_external_costs["table_name"]} : {schema_external_costs}
**
{schema_net_income["table_name"]} : {schema_net_income}
**
"""

system_suffix = """
To make requests to any of these table, you must send the name of the table (table_name),
the row you wish to access (described in the schema of each table, see above), the start and end
time in datatime format yyyy-mm-dd.


# **How to use the search engine API:**
**Format of the return in a python dictionnary**:
{
"table_name": name of the table (str)
"columns": names of the columns (list of str), # You may use ["all"] if you want all columns
"start_date": start datetime (str yyyy-mm-dd),
"end_date": end datetime (str yyyy-mm-dd)
}

Never return sentenses, strictly return the python dictionnary.
If a table or columns does not exists, return None.
The engine will not accept any other format of response.
The table your request must exist in the above schema.
The columns you request must exists in the tables.
If the start date is not mentionned use "2022-01-01".
If the end date is not mentionned use "2023-12-31".

**Example documentation**
Question: I need the total cost of Business Operations from Jan 2022 to May 2023
Return:
{
"table_name": "External_Cost_Centers_Table"
"columns": ["business_operations"],
"start_date": "2022-01-01",
"end_date": "2023-05-31"
}

Question: I need a forcasting of the profit of A1 starting December 2022
Return:
{
"table_name": "Profit_Centers_Table"
"columns": ["a1"],
"start_date": "2022-12-01",
"end_date": "2023-12-31"
}

Question: I need the Enterprise credit card cost for the entire year 2024
Return:
{
"table_name": "Credit_Cards_Costs_Table"
"columns": ["enterprise"],
"start_date": "2024-01-01",
"end_date": "2024-12-31"
}

Question: Show me sources of costs by sectors
Return:
{
"table_name": "External_Cost_Centers_Table"
"columns": ["all"],
"start_date": "2024-01-01",
"end_date": "2024-12-31"
}

Question: I need the staff and marketing expenses in March 2022 ?
Return:
{
"table_name": "External_Cost_Centers_Table
"columns": ["marketing_expenses", "staff_costs"]
"other_opex", "total_opex"],
"start_date": "2022-03-01",
"end_date": "2022-03-31"
}

Question: How many transaction did we do in the first quarter of 2022 ?
Return:
{
"table_name": "Transactions_Table"
"columns": ["total_transactions"],
"start_date": "2022-01-01",
"end_date": "2022-03-31",
}

Question: What is the distribution of our profit in 2023 ?
Return:
{
"table_name": "Profit_Centers_Table"
"columns": ["all"],
"start_date": "2023-01-01",
"end_date": "2023-12-31",
}
"""

DATAENG_PROMPT = system_prefix + system_schema + system_suffix
DATAENG_TOOLS = parse_json(Settings().DE_TOOLS)


if __name__ == "__main__":
    from core.settings.settings import Settings

    ENV = Settings()
    gpt = GptBackend(settings=ENV)

    _system_function = "You are an efficient assistant.."
    _query = "show me the total transactions for the month of may 2022."
    response = gpt.get_completion(query=_query, primer_prompt=DATAENG_PROMPT, tools=DATAENG_TOOLS)
    print(response)  # noqa: T201
