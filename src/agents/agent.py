from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from src.agents.prompts.system_prompt import system_prompt
from src.utils.settings import Settings
from src.tools.rag_tool import query_store_policy_and_procedures
from src.tools.sql_tool import search_product_name_category_price, search_order_status

# Define global variables
settings = Settings()

# Declare agent
llm = ChatGoogleGenerativeAI(model=settings.MODEL, google_api_key=settings.google_key)

# Bind tools
tools = [query_store_policy_and_procedures, search_product_name_category_price, search_order_status]

# Create tool calling agent
agent = create_agent(model=llm,
                     tools=tools,
                     system_prompt=system_prompt,
                     checkpointer=InMemorySaver()
                    )


