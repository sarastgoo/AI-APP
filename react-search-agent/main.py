from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents.react.agent import create_react_agent
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from prompt import REACT_PROMPT_WITH_INSTRUCTIONS
from schemas import AgentResponse

load_dotenv()

tool = [TavilySearch()]
llm = ChatOpenAI(temperature=0, model="gpt-4")
react_prompt = hub.pull("hwchase17/react")
output_parser = PydanticOutputParser(pydantic_object=AgentResponse)
react_prompt_with_format_instructions = PromptTemplate(
    template= REACT_PROMPT_WITH_INSTRUCTIONS,
    input_variables=["input", "agent_scratchpad", "tool_names"]
).partial(format_instructions=output_parser.get_format_instructions())

agent = create_react_agent(
    llm= llm, 
    tools= tool, 
    prompt= react_prompt_with_format_instructions)

agent_executor = AgentExecutor(agent=agent, tools=tool, verbose=True)
extract_output = RunnableLambda(lambda x : x["output"])
parse_output = RunnableLambda(lambda x: output_parser.parse(x))

chain = agent_executor | extract_output | parse_output


def main():
    result = chain.invoke(
        input={
            "input": "search for 4 job pstings for an ai engineer using langchain in the bay area on linkedin and list their details",
        }
    )
    print(result)


if __name__ == "__main__":
    main()
