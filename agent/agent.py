from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools.odata_tool import query_odata, get_odata_schema, search_odata_data

def build_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [query_odata, get_odata_schema, search_odata_data]

    # Create agent with proper configuration
    agent = create_react_agent(
        llm,
        tools=tools
    )
    return agent
