from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_PROJECT_NAME, DATA_ROOT_PATH, Path


def read_file(file_path: str | Path) -> str:
    file_path = Path(file_path)

    data = file_path.read_text(encoding="utf-8")

    return data


def main():
    ABOUT_FILE = DATA_ROOT_PATH / "about-elon.txt"
    print("Hello from langchain-course!")
    information = read_file(ABOUT_FILE)

    summary_template = """
    given the information {information} about a person I want you to create:
    1. A short summary
    2. two interesting facts about them
    """

    summary_prompt_template = PromptTemplate(
        input_variables=["information"], template=summary_template
    )

    llm = ChatGoogleGenerativeAI(
        project=GOOGLE_PROJECT_NAME,
        model="gemini-2.5-flash",
        temperature=0,
        vertexai=True,
    )

    chain = summary_prompt_template | llm

    response = chain.invoke(input={"information": information})
    print(response.content)


if __name__ == "__main__":
    main()
