from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool
import json

load_dotenv()

class ResearchResponse(BaseModel):
    topic : str
    summary : str
    sources : list[str]
    tools_used : list[str]

llm = ChatOpenAI(model="gpt-4o-mini")

parser = PydanticOutputParser(pydantic_object=ResearchResponse) #output from LLM into a structured format defined by ResearchResponse

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research assistant that will help generate a research paper.
            Answer the user query and use neccessary tools. 
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions()) #partical -> fills in specific parts of the template with format_instructions

tools = [search_tool, save_tool]

#creates an agent that can call tools, in this case to use an LLM
agent = create_tool_calling_agent(
    llm=llm,
    prompt = prompt,
    tools = tools
) 

#AgentExecutor to present the agent and invoke to call the agent
agent_executor = AgentExecutor(agent=agent, tools = tools, verbose=True) #verbose to see the thought from the agent

query = input("what can i help you with : ")
raw_response = agent_executor.invoke({"query" : query})

try:
    structured_response = parser.parse(raw_response.get("output")) 
    print(structured_response)
except Exception as e:
    print(f"Error parsing response {e} \nRaw Response : {raw_response}")