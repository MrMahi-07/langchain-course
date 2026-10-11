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
- Google Cloud credentials authorized for Vertex AI; `gcloud` is the recommended local setup, but it is not the only way to provide credentials

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

4. Configure Google Cloud access. The simplest local developer setup is to install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) and create Application Default Credentials (ADC):

   ```powershell
   gcloud auth application-default login
   gcloud services enable aiplatform.googleapis.com --project=YOUR_GOOGLE_CLOUD_PROJECT_ID
   ```

   The `gcloud config set project ...` command is optional for this app because it passes `GOOGLE_PROJECT_NAME` directly to the model. It changes the CLI's default project, not the ADC identity used by the app. Ensure the project has billing enabled and the signed-in identity has permission to use Vertex AI (for example, the Vertex AI User role).

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

### Do I Need `gcloud`?

No, not in every environment. It is the recommended straightforward method for a developer using their own Google account on a local computer: `gcloud auth application-default login` creates local ADC credentials. ADC is the authentication mechanism the application needs; `gcloud` is one way to supply those credentials.

Other supported ADC options include a `GOOGLE_APPLICATION_CREDENTIALS` file containing an external-account (Workload/Workforce Identity Federation) configuration, service-account impersonation credentials, or an attached service account when running on Google Cloud. Avoid service-account key files unless there is no safer option; never commit credential files. See Google's [ADC overview](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc), [local ADC setup](https://docs.cloud.google.com/docs/authentication/set-up-adc-local-dev-environment), and [ADC credential lookup order](https://docs.cloud.google.com/docs/authentication/application-default-credentials).

The Gemini Developer API is a separate backend and can use a Gemini API key without `gcloud`. Switching to that backend requires changing the current Vertex AI configuration; setting `GOOGLE_API_KEY` alone does not override `vertexai=True`. Its quota and billing terms are separate, so check the current [Gemini API documentation](https://ai.google.dev/gemini-api/docs) before choosing it.

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

