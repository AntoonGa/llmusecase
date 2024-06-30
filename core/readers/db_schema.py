""".. include:: README.md

These ficticious schemas are injected into the LLM prompt to give it information about
the table generated from the Excel file.
"""

schema_transactions = {
    "columns": [
        "total_transactions",
        "enterprise",
        "mid_market",
        "a1",
        "marketplaces",
        "small+",
        "small",
        "local",
        "editions",
        "other",
    ],
    "rows": "Monthly Timestamps",
    "table_name": "Transactions_Table",
    "table_information": "Table containing number of transactions, monthly."
    "Columns represent a different type of transaction."
    "Total number of transaction is stored in "
    "'total_transactions' columns"
    "Rows are timestamps spanning from Jan 22 to Dec 23",
}

schema_revenues = {
    "columns": [
        "total_revenue",
        "enterprise",
        "mid_market",
        "a1",
        "marketplaces",
        "small+",
        "small",
        "local",
        "editions",
        "other",
    ],
    "rows": "Montly Timestamps",
    "table_name": "Revenues_Table",
    "table_information": "Table containing revenue splitted by transfaction type."
    "Columns represent a different type of transaction. "
    "Total revenue is stored in the 'total_revenue' column."
    "Rows are timestamps spanning from Jan 22 to Dec 23",
}

schema_service_costs = {
    "columns": [
        "total_cost_of_services",
        "enterprise",
        "mid_market",
        "a1",
        "marketplaces",
        "small+",
        "small",
        "local",
        "editions",
        "other",
    ],
    "rows": "Monthly Timestamps",
    "table_name": "Cost_Of_Service_Table",
    "table_information": "Table containing costs splitted by services types."
    "Columns represent a different type of transaction. "
    "The total cost of service is stored in column "
    "'total_cost_of_services'"
    "Rows are timestamps spanning from Jan 22 to Dec 23",
}

schema_creditcard_costs = {
    "columns": [
        "total_credit_card_fees",
        "enterprise",
        "mid_market",
        "a1",
        "marketplaces",
        "small+",
        "small",
        "local",
        "editions",
        "other",
    ],
    "rows": "Monthly Timestamps",
    "table_name": "Credit_Cards_Costs_Table",
    "table_information": "Table containing company credit card cost "
    "splitted by services. Each column "
    "represent a different type of transaction. "
    "Total credit cards fees is stored in the column "
    "'total_credit_card_fees'"
    "Rows are timestamps spanning from Jan 22 to Dec 23",
}

schema_profits = {
    "columns": [
        "total_gross_profit",
        "enterprise",
        "mid_market",
        "a1",
        "marketplaces",
        "small+",
        "small",
        "local",
        "editions",
        "other",
        "business_operations",
        "customer_service",
        "marketing_expenses",
        "staff_costs",
        "other_opex",
        "total_opex",
    ],
    "rows": "Timestamps",
    "table_name": "Profit_Centers_Table",
    "table_information": "Table containing all gross profit center of the company, "
    "splitted by service types. Each column "
    "represent a different type of transaction."
    "Total gross profit is stored in the total_gross_profit column "
    "Rows are timestamps spanning from Jan 22 to Dec 23",
}

schema_external_costs = {
    "columns": [
        "business_operations",
        "customer_service",
        "marketing_expenses",
        "staff_costs",
        "other_opex",
        "total_opex",
    ],
    "rows": "Timestamps",
    "table_name": "External_Cost_Centers_Table",
    "table_information": "Table containing all externalized cost such as "
    "marketing expenses or external staff."
    "Each column represents a different type of transaction."
    "Total external cost is stored in the total_opex column"
    "Rows are timestamps spanning from Jan 22 to Dec 23",
}

schema_net_income = {
    "columns": ["ebitda"],
    "rows": "Timestamps",
    "table_name": "EBITDA",
    "table_information": "Single columns table. EBITDA represent the net income "
    "of the company Each column "
    "Rows are timestamps spanning from Jan 22 to Dec 23",
}

if __name__ == "__main__":
    pass
