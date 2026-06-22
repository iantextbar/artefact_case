from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor

from src.agents.prompts import PROMPT_TEMPLATE
from src.utils.settings import Settings
# from src.tools.rag_tool import 
# from src.tools.sql_tool import

# Define global variables
settings = Settings()

# Declare agent
llm = ChatGoogleGenerativeAI(model=settings.MODEL, google_api_key=settings.google_key)

# Bind tools


