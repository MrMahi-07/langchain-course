# Gemini Troubleshooting Context: LangChain Agent and Vertex AI

> Share this document with a coding assistant for diagnosis. It intentionally excludes credentials and exact account-specific configuration. Do not attach or paste `.env`, access tokens, API keys, service-account files, or credential-bearing logs.

## What I Need Help With

Please review this small LangChain agent's Gemini/Vertex AI setup against current Google and `langchain-google-genai` documentation. A live request now succeeds, but please identify any setup assumptions that might make the project fail for another developer or a fresh clone. Distinguish clearly between:

1. Keeping the current Google Cloud Vertex AI integration and fixing its project, billing, API, or IAM setup.
2. Changing to the Gemini Developer API with an API key, if that is appropriate for this project and supported by the installed integration version.

Do not suggest putting credentials in source code or committing `.env`. Explain which option is being used, which credentials it requires, and what account/project charges may apply. If recommending a code change, provide the exact minimal diff and a way to verify it without exposing credentials.

## Project Summary

This is a Python command-line learning project. It asks for one prompt, passes the prompt through a LangChain agent, and prints the final assistant response.

The intended model is Gemini 2.5 Flash. The app currently configures `ChatGoogleGenerativeAI` with `vertexai=True` and a Google Cloud project ID. This selects Google Cloud Vertex AI; it is not using the Gemini Developer API key authentication path.

The repository uses `uv` and tracks `uv.lock`. Its project metadata specifies Python 3.14 or newer and these direct dependency constraints:

- `langchain>=1.4.2`
- `langchain-core>=1.6.3`
- `langchain-google-genai>=4.4.0`
- `python-dotenv>=1.2.3`

`uv sync --locked` completed successfully locally. Python editor diagnostics were clean.

## Current Application Code

`main.py`:

```python
from config import GOOGLE_PROJECT_NAME
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI


@tool
def web_search(query: str) -> str:
    """Tool that searches over internet."""
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
```

`config.py`:

```python
from os import getenv as __getenv
from dotenv import load_dotenv as __load_env
from pathlib import Path

__load_env()


def get_env(name: str, default=None) -> str:
    value = __getenv(name, default)
    if not value:
        raise ValueError(f"Variable {name} not found.")
    return value


GOOGLE_PROJECT_NAME = get_env("GOOGLE_PROJECT_NAME")
PROJECT_ROOT_PATH = Path(get_env("PROJECT_ROOT", str(Path(__file__).resolve().parent)))
DATA_ROOT_PATH = PROJECT_ROOT_PATH / "data"
```

## Reproduction and Observed Result

Command run from the repository root:

```powershell
"What is 2 + 2? Answer briefly." | uv run python main.py
```

The initial test accepted the prompt and reached the Google model request, but failed before any model response or tool call was returned. The relevant error was:

```text
GooglePermissionDeniedError
Error calling model 'gemini-2.5-flash' (PERMISSION_DENIED)
403 PERMISSION_DENIED
reason: BILLING_DISABLED
service: aiplatform.googleapis.com
message: This API method requires billing to be enabled for the Google Cloud project.
```

The affected project ID is intentionally redacted here. The local run used Google Application Default Credentials (ADC). The error explicitly reported billing disabled for the selected project. It did not by itself establish whether IAM roles, API enablement, or other configuration were correct.

### Successful Retry

After the initial failure, the same prompt was retried using the same command and current local configuration:

```powershell
"What is 2 + 2? Answer briefly." | uv run python main.py
```

The retry succeeded with this application output:

```text
You: Gemini: 4
```

This verifies that the local application can currently make a successful Gemini request. The specific Google Cloud setting changed between the failed request and successful retry is not known from the application output, so do not assert which external setting resolved it. The initial billing error and successful retry should both be retained as troubleshooting history.

A separate blank-input check passed: pressing Enter without a prompt exits before making a model call.

## Environment and Credential Boundaries

The local `.env` contains a Google project ID and has also held several API-key variables for Google, LangSmith, Grok, and Tavily. Their values are private and intentionally omitted. Those credentials were accidentally exposed in a shared conversation and must be revoked/rotated; do not reuse them or include replacements in any shared document.

For the current Vertex AI path:

- `GOOGLE_PROJECT_NAME` is loaded from `.env` and passed to the model client as `project`.
- `GOOGLE_API_KEY` is not read by the current app and should not be assumed to authenticate this Vertex AI request.
- The app requires credentials discoverable by Google Application Default Credentials (ADC); installing the Google Cloud CLI is not a universal runtime requirement.
- For local user-account development, Google's documented route is `gcloud auth application-default login`. ADC can also use supported external-account credential configuration via `GOOGLE_APPLICATION_CREDENTIALS`, direct credentials, or an attached service account in a supported Google Cloud runtime.
- The local ADC identity must have access to the selected project.
- The project needs Vertex AI enabled, billing enabled, and appropriate IAM access. Do not assume enabling the API alone enables billing.

The repository has `.env.example` with placeholders for `GOOGLE_PROJECT_NAME` and optional `PROJECT_ROOT`. `.env` is Git-ignored and is not tracked. The local `.env` also contains optional variables for other tools/integrations, but those are not required or read by this app's current configuration. Never commit `.env`, keys, ADC credential files, or service-account JSON.

### Authentication Research (Checked 2026-10-11)

The current code explicitly sets `vertexai=True`, so it uses the Google Cloud Vertex AI backend. The official LangChain integration documentation says ADC is supported for this backend and demonstrates `gcloud auth application-default login`; it also documents supplying service-account credentials directly. The Google ADC documentation lists credentials from `GOOGLE_APPLICATION_CREDENTIALS`, a local ADC file created with `gcloud auth application-default login`, and an attached service account as ADC lookup sources. Therefore, `gcloud` is the normal/recommended local user-credential setup in these docs, but it is not mandatory for all ways of running this application.

For deployed workloads on Google Cloud, an attached service account is the preferred credential source. For external environments, Google recommends Workload Identity Federation over long-lived service-account keys. Service-account keys are sensitive and should be avoided when possible.

The Gemini Developer API is a different backend. LangChain supports API-key authentication for it, but this app's current `vertexai=True` setting selects Vertex AI; adding `GOOGLE_API_KEY` alone will not change the backend. The Developer API has its own quota and billing rules.

Official references:

- [Google: Set up ADC](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc)
- [Google: ADC for local development](https://docs.cloud.google.com/docs/authentication/set-up-adc-local-dev-environment)
- [Google: How ADC finds credentials](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
- [LangChain: `ChatGoogleGenerativeAI` authentication and backend selection](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai)

## Questions to Resolve

Please answer with references to current official documentation where possible:

1. Given the initial billing error followed by a successful retry, what does the error establish, and which Google Cloud project/API/IAM checks should still be verified for reproducibility?
2. Is `project=...` the correct project parameter for `ChatGoogleGenerativeAI` with Vertex AI in the specified integration release range? Is a Vertex AI location required or recommended, and what is the smallest valid configuration?
3. If the developer instead wants Gemini Developer API authentication, what exact constructor arguments and environment variable are supported by `langchain-google-genai` version `>=4.4.0`? What should change in the code, and how can the app avoid accidentally mixing Developer API and Vertex AI credentials?
4. Does the Gemini Developer API route avoid this specific Vertex AI billing requirement, or does it have separate quota, billing, or availability requirements that must be stated? Do not promise that it is free or available without checking current policy.
5. The interactive LangChain agent now returns `4` for a basic arithmetic prompt. What is the shortest useful direct-model smoke test to isolate model authentication from agent/tool wiring if this fails for another developer?
6. Identify any other concrete code issue in the snippet that would prevent a successful response after authentication and billing are fixed. Avoid unrelated redesign.

Please separate confirmed facts from assumptions. A successful live model response has been observed locally, but successful setup for another user's Google identity/project has not been verified.

## Current Tool and Data Limitations

`web_search` is a demonstration stub, not a real internet search integration. It prints the query and always returns the fixed sample text `Tokyo weather is sunny`. It is registered with the agent, but whether it is invoked depends on Gemini's tool selection.

`data/about-elon.txt` exists in the repository but is not loaded or used by the current application. The project does not currently implement file reading, retrieval, or RAG. These are separate from the present billing failure.

## Local Setup Outline

A teammate cloning the repository needs `uv`, Python 3.14 or newer, the tracked `uv.lock`, a local `.env` based on `.env.example`, and their own Google Cloud authentication/configuration. The usual local dependency setup is:

```powershell
uv sync --locked
```

Then configure ADC and the selected Google Cloud project using the organization's approved process. Never share ADC files or credentials. Once the project is properly configured, run:

```powershell
uv run python main.py
```
