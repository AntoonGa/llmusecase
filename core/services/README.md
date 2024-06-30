# Data operators
These are simple tools to simulate a set of backend services.
Those services can be used to query an internal database, manipulate data with forecasting or
data visualisation APIs.
In general those services must be choosen and called by a routing agent depending on the user query.

## Available services

### 1. Request data
Used to fetch data from our ficticious database

### 2. Data visualization
Visualise data (histograms, pie charts, time-series evolution) - Also uses the request data service

### 3. Data forecasting
Perform Arima forcast on time-series - Also uses the request data service

### 4. RAG
A simple RAG on the provided pdf files

### 5. Pipelines
Assembly used to launch services from a single entry point (user input)
