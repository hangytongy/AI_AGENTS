from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime



search = DuckDuckGoSearchRun()

#create a search tool, the description will allow the agent to know when to use the tool, in this case, to use when needing to search the web
search_tool = Tool(
    name="search_web",
    func=search.run,
    description="Search the web for infomation"
)


api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=10000)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

#must include the datatype in the function so that the model knows what data type to use
def save_to_txt(data: str, filename: str = "research_output.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ---\nTimestamp : {timestamp}\n\n{data}\n\n"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    
    return f"Data successfully saved to {filename}"

save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Save structured Research Data into a text file"
)