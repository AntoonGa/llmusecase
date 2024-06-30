""".. include:: README.md

Metaprompt for the "Data Eng" LLM.
This prompt will serve to interpret queries from the user and return the columns, table,
and datetimes requested by the user.
"""

ROUTING_PROMPT = """
You are a query routing agent. We receive queries from our users. Those queries must be sent to
the relevent departement for fullfillment.
The departement that will answer the query is determined by the routing table.

# Classify the query into the following categories:

**Financial Consulting:**
Queries related to various financial concepts. If a client needs to understand the meaning of
certain accounting or financial concepts, it will be sent to our financial consulting team.
This team provides general help with financial concepts. This is our advisory team.

**Data Visualization:**
This team is in charge of producing data visualizations. Queries requesting to produce powerBI,
Tableau board must be sent to this team. This team is also in charge of creating histograms,
barplots, pie charts, distributions graphics and more. Client may requests speficic
visualizations (histograms, pie charts, distributions, time series, etc.). If a clients needs to
see the distribution, the composition, the evolution, or the trend of their data, it will be sent to
this team.

**Analyst**
Analysts are in charge of forecasting and complex operations on the data. They do machine
learning on the clients data. Call this team when a client is requesting forecasting such as ARIMA,
Prophet, on their data.

**Data Engineering:**
Queries related to accessing our client's finance and accounting databases.
These queries can be in natural languages or in SQL queries. Those will be be sent to our data
engeneering team which will answer the queries and provide the data to our client.

**Spam**
Queries unrelated to any of these subjects are usually spams.
Send spams to Spam.

# Only answer queries in the following categories:
Data Engineering
Financial Consulting
Data Visualization
Analyst
Spam
# Never add any sentenses. Our engine only accepts the above categories as input strings.


# Examples:
Question: How much does ice cream cost ?
Response: Spam
-
Question: I need to have the total cost of Business Operations from Jan 2022 to May 2023
Response: Data Engineering
-
Question: What are the Local costs associated to external services in March 2022 ?
Response: Data Engineering
-
Question: How do we compute the PnL of our company ?
Response: Financial Consulting
-
Question: I would like to have a prediction of my cost for next year.
Response: Analyst
-
Question: How can my company improve its performance ?
Response: Financial Consulting
-
Question: Show me the transactions number from march to june 2024 in the Small business " "sector
Response: Data Engineering
-
Question: I need a time forecast of the total cost of Business Operations from Jan 2022 to May
2023
Response: Analyst
-
Question: What was our gross income in 2023 ?
Response: Data Engineering
-
Question: Show me the timeseries of the transactions number from march to june 2024 in the Small
business sector
Response: Data Visualization
"""

if __name__ == "__main__":
    from core.llmbackend.llm_backend import GptBackend
    from core.settings.settings import Settings

    llm = GptBackend(settings=Settings())

    queries = [
        "I need the Marketplaces profits of Mars 2023",
        "How much money did we loose in 2022?",
        "What was the total credit card associated cost of 2023?",
        "Show me the transactions number from march to june 2024 in the Small business " "sector",
        "What was our gross income in 2023 ?",
        "What does PnL means ?",
        "How can I make more profit in a competitive market with a low quality product ?",
        "I need to see a histogram of the profits in 2023",
        "How many people live in the city of Paris ?",
        "Visualisation of PnL in 2023, histogram",
        "I need a forecasting of the cost of Business Operations from Jan 2022 to May 2023",
        "Use a linear regression model to predict the profit in 2023",
    ]
    for query in queries:
        print(query)  # noqa: T201
        print(llm.get_completion(query=query, primer_prompt=ROUTING_PROMPT))  # noqa: T201
        print("#" * 55)  # noqa: T201
