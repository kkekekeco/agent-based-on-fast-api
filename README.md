# Agent-Based FastAPI Chat Application

A FastAPI application featuring agentic AI chat capabilities with web search tools.

## Features

- 🤖 **Agentic Chat**: AI-powered chat using multiple LLM models (grok-4-fast, deepseek, gemini-2.5-pro, gpt-5, etc.)
- 🔍 **Web Search Tool**: Real-time web search integration via AI Builder Search API
- 📄 **Page Reader Tool**: Fetch and extract content from web pages
- 🎨 **Modern UI**: Beautiful chat interface with model switcher and chat history
- 🐳 **Docker Ready**: Includes Dockerfile for containerized deployment

## Tech Stack

- **Backend**: FastAPI, Python 3.x
- **AI Integration**: OpenAI-compatible API (AI Builder)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **HTTP Client**: httpx

## Getting Started

### Prerequisites

- Python 3.8+
- AI Builder Token

### Installation

1. Clone the repository:
```bash
git clone https://github.com/kkekekeco/agent-based-on-fast-api.git
cd agent-based-on-fast-api
```

2. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```
AI_BUILDER_TOKEN=your_token_here
```

5. Run the server:
```bash
fastapi dev main.py
```

6. Open http://127.0.0.1:8000 in your browser

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Chat UI |
| GET | `/welcome/{name}` | Welcome message |
| POST | `/agent/chat` | Agentic chat endpoint |

## Docker Deployment

```bash
docker build -t fastapi-agent .
docker run -p 8000:8000 -e AI_BUILDER_TOKEN=your_token fastapi-agent
```

## License

MIT
