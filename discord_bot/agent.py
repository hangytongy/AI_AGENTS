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

class ConversationResponse(BaseModel):
    response: str
    emotion: str  # To track the emotional tone of response
    follow_up_questions: list[str]  # Potential follow-up questions to keep conversation going
    context_used: list[str]  # What context/tools were used to form response

llm = ChatOpenAI(model="gpt-4o-mini")

parser = PydanticOutputParser(pydantic_object=ConversationResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a friendly and engaging conversational partner who excels at natural dialogue.
            Maintain a warm, personable tone while engaging with the user's messages.
            Use tools when needed to provide accurate and relevant information.
            Your responses should feel natural and encourage further discussion.
            Your responses to answers should be as short and precise as possible.
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool, save_tool]

agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def call_agent(query):
    if query:
        raw_response = agent_executor.invoke({"query": query})

        try:
            structured_response = parser.parse(raw_response.get("output"))
            output_string = raw_response.get("output")
            data = json.loads(output_string)
            return data['response']
        except Exception as e:
            print(f"Error parsing response {e} \nRaw Response: {raw_response}")
            return f"lmao sorry what?"
    else:
        return "I didn't catch that. Could you please say something?"