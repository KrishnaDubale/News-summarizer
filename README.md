# AI News Summarizer

A local-first FastAPI app with a lightweight chat UI that fetches topic-based articles from NewsAPI and returns either a Groq-generated summary or an extractive fallback.

## Features

- Natural-language topic input such as `give me IPL news`
- Rule-based topic parsing to keep topic detection cheap
- NewsAPI integration with normalized article output
- Groq summarization with extractive fallback and deduplication
- Simple web interface served by FastAPI

## Project structure

- `app/main.py` starts the FastAPI app and serves the UI
- `app/query_parser.py` interprets user prompts into search terms
- `app/newsapi.py` fetches and normalizes articles from NewsAPI
- `app/summarizer.py` ranks and summarizes the article set
- `app/service.py` coordinates parsing, fetching, and response formatting
- `static/` contains the web UI
- `tests/` contains local unit tests

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a local `.env` file from the example and add your keys there:

```bash
cp .env.example .env
```

The app loads `.env` automatically at startup.

4. Start the app:

```bash
uvicorn app.main:app --reload
```

5. Open `http://127.0.0.1:8000`

## API

`POST /summarize-news`

Request:

```json
{
  "query": "give me IPL news"
}
```

Response shape:

```json
{
  "query": "give me IPL news",
  "topic": "IPL",
  "summary": "Here is a quick summary...",
  "highlights": ["..."],
  "articles": [],
  "mode": "extractive",
  "error": null
}
```

## Notes

- `GROQ_API_KEY` enables LLM summarization through Groq chat completions.
- If Groq is unavailable, the app automatically falls back to extractive summarization.
- If the query is vague, the app asks the user for a more specific topic instead of calling NewsAPI.
- If NewsAPI fails or the API key is missing, the UI shows a safe error response.
