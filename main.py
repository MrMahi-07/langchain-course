from config import GOOGLE_PROJECT_NAME
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI


@tool
def web_search(query: str) -> str:
    """
    Tool that searches over internet

    Args:
        query (str): The query to search for

    Returns:
        str: The search result
    """

    print(f"Searching in local for the query: {query}")

    return "Tokyo weather is sunny"


def main():
    prompt = input("You: ").strip()
    if not prompt:
        print("Please enter a prompt.")
        return

    llm = ChatGoogleGenerativeAI(
        project=GOOGLE_PROJECT_NAME,
        model="gemini-2.5-flash",
        temperature=0,
        vertexai=True,
    )
    tools = [web_search]

    agent = create_agent(model=llm, tools=tools)

    messages = {"messages": [HumanMessage(content=prompt)]}

    response = agent.invoke(messages)

    print(f"Gemini: {response['messages'][-1].content}")


if __name__ == "__main__":
    main()
