# Conversational Agent for Empório da Música

A simple tool using agent to answer questions through WhatsApp for a music store.

## Requirements

Pre-requisits: Python 3.12 or above

Create a .env file following the example and add a valid Gemini API Key.

Install necessary dependencies.

```bash
pip install -r requirements.txt

```
If using uv.

```bash
uv sync

```

## Usage

In ```./src/notebooks/get_slash_conversation.ipynb```, connect to local virtual environment. Declare a phone number, a time of the day (HOURS:MINUTES) and a day of the week. Run as follows:

```python
conversation(CLIENT_PHONE, time, day_of_week)
```

To exit conversation, write "sair".

## Project Structure

```
├── README.md
├── data
│   ├── chroma_db_storage
│   ├── raw
│   └── sql_db
├── main.py
├── pyproject.toml
├── requirements.txt
├── src
│   ├── agents
│   │   ├── agent.py
│   │   └── prompts
│   ├── data_processing
│   │   ├── base.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── sql_database.py
│   │   └── vector_database.py
│   ├── notebooks
│   │   └── get_slash_conversation.ipynb
│   ├── tools
│   │   ├── rag_tool.py
│   │   └── sql_tool.py
│   └── utils
│       ├── settings.py
│       └── storage.py
└── uv.lock
```

Raw and processed data can be found in ```./data```. ```./src/agents/``` contains prompts and the agent declaration. ```./src/data_processing/``` contains scripts for creating the vector database and the SQL database. ```./src/tools/``` has the tools used by the agent. ```./src/utils/``` has useful classes for project settings and storage. ```./src/notebooks/``` has the executed conversations with the agent.
