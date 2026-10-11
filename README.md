# Gemini Tool-Calling Agent

A small LangChain agent that sends a prompt to Gemini 2.5 Flash through Google Cloud Vertex AI. The agent can decide to call a registered LangChain tool before returning its answer.

## How It Works

```text
Prompt in terminal -> LangChain agent -> Gemini 2.5 Flash on Vertex AI
                           |                   |
                           +-- registered tools <-+ (when Gemini requests a tool)
```

The app uses `ChatGoogleGenerativeAI` with `vertexai=True`, then passes that model and the registered tools to LangChain's `create_agent`. User input is sent as a `HumanMessage`; `agent.invoke` runs the model/tool loop and the app prints the final response.

The `web_search` tool is currently a stub: it prints the query and always returns the sample text `Tokyo weather is sunny`. It does not access the internet. The file `data/about-elon.txt` is present as sample data, but this version of the app does not load it or implement file search/RAG.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)
- A Google Cloud project with billing enabled and the Vertex AI API enabled
- Google Cloud CLI (`gcloud`) for local Application Default Credentials

## Local Setup

1. Clone the repository and enter its directory:

   ```powershell
   git clone <repository-url>
   cd langchain-course
   ```

2. Create your local environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

   On macOS or Linux, use:

   ```bash
   cp .env.example .env
   ```

   Set `GOOGLE_PROJECT_NAME` in `.env` to your Google Cloud project ID. `PROJECT_ROOT` is optional; by default, the repository directory is used.

3. Install the project dependencies:

   ```powershell
   uv sync
   ```

4. Configure Google Cloud access. In a terminal where `gcloud` is installed, sign in and select the project:

   ```powershell
   gcloud auth application-default login
   gcloud config set project YOUR_GOOGLE_CLOUD_PROJECT_ID
   gcloud services enable aiplatform.googleapis.com --project=YOUR_GOOGLE_CLOUD_PROJECT_ID
   ```

   Ensure billing is enabled for the project and your account has permission to use Vertex AI (for example, the Vertex AI User role). The Google Cloud project ID in `.env` must be the project you have configured access to.

5. Start the agent:

   ```powershell
   uv run python main.py
   ```

   Enter a prompt when asked. Each run sends a request to Gemini through Vertex AI and may incur charges under your Google Cloud billing account. Press Enter on a blank prompt to exit that run without sending a request.

## Configuration

| Variable | Required | Purpose |
| --- | --- | --- |
| `GOOGLE_PROJECT_NAME` | Yes | Google Cloud project ID used by Vertex AI |
| `PROJECT_ROOT` | No | Repository root used to derive the `data` directory; defaults to this project directory |

Authentication uses Google Cloud Application Default Credentials (ADC). This Vertex AI setup does **not** use `GOOGLE_API_KEY`; do not put credentials or API keys in source control. The local `.env` file is ignored by Git.

## Project Files

| Path | Description |
| --- | --- |
| `main.py` | Gemini model setup, the sample tool, and the interactive agent invocation |
| `config.py` | Loads environment variables and defines project/data paths |
| `data/about-elon.txt` | Sample text file; not yet consumed by the agent |
| `pyproject.toml` / `uv.lock` | Project metadata, dependencies, and locked dependency versions |
| `.env.example` | Safe configuration template to copy to `.env` |

## Troubleshooting

- **`GOOGLE_PROJECT_NAME` not found:** copy `.env.example` to `.env` and set the project ID.
- **ADC credentials not found:** run `gcloud auth application-default login`.
- **`BILLING_DISABLED` / billing required:** enable billing on the selected Google Cloud project, then retry after the change propagates.
- **Vertex AI permission or API errors:** verify that the Vertex AI API is enabled, the project ID is correct, and your Google account has the required IAM role.

## Development Status

This is a learning/demo project. The Gemini/Vertex AI call is implemented; the search tool is only a placeholder, and the sample data file is not yet connected to the agent. No automated test suite is currently included.

