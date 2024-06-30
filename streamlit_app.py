""".. include:: README.md

A simple demo of a data assistant using Streamlit.

to run locally please run the following command:
streamlit run streamlit_app.py
"""

import logging

import streamlit as st

from core.llmbackend.llm_backend import GptBackend
from core.services.db_query_service import DbQueryEngine
from core.services.pipelines import OrderData, run_system
from core.settings.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize the chatbot
def chatbot_response(query: str) -> OrderData:
    """Call the generic pipeline from a user query."""
    resp = run_system(query=query)
    return resp


def display_sidebar() -> None:
    """Display the schema of dataframes."""
    _llm = GptBackend(settings=Settings())
    engine = DbQueryEngine(_llm)
    st.sidebar.write("You may request simple dataviz, forecast, data fetches and simple RAG...")
    st.sidebar.header("Your data schema")
    dataframes = engine.table_router
    for table_name, df in dataframes.items():
        st.sidebar.write(f"**Table: {table_name}**\n", df.head(1))


# Streamlit app
display_sidebar()
st.header("Your data assistant...")
# User input
user_input = st.text_input("You:")
# Chatbot response
if user_input:
    response = chatbot_response(user_input)
    if response.llm_response:
        st.write("LLM response:", response.llm_response)
    if response.figure is not None:
        for fig in response.figure:
            st.pyplot(fig=fig)
    if response.table is not None:
        st.write("Table", response.table_name)
        st.write(response.table)
    st.write("Pipeline detected:", response.pipeline_name)

    # Log user input and response
    log_info = f"User input: {user_input}\n"
    log_info += str(response)
    logger.info(log_info)
