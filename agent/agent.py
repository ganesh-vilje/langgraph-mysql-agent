from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools.mysql_tool import query_mysql, get_schema

def build_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [query_mysql, get_schema]

    # Create agent with proper configuration
    agent = create_react_agent(
        llm,
        tools=tools
    )
    return agent
