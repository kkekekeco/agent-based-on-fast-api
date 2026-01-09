"""
FastAPI Welcome Application & Agentic Search (Internal API)
===========================================================

This module implements a FastAPI application that:
1. Welcomes users by name.
2. Provides an agentic chat endpoint using `grok-4-fast` with an internal web search tool.

Usage:
    Run the server: fastapi dev main.py
    Access docs: http://127.0.0.1:8000/docs
"""

import os
import logging
import json
import re
import httpx
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app")

# Load environment variables
load_dotenv()

AI_BUILDER_TOKEN = os.getenv("AI_BUILDER_TOKEN")

# Initialize OpenAI client for AI Builder
client = OpenAI(
    base_url="https://space.ai-builders.com/backend/v1",
    api_key=AI_BUILDER_TOKEN
)

app = FastAPI(
    title="Agentic AI Welcome API",
    description="A FastAPI app with user welcome and agentic search capabilities using internal Search API.",
    version="3.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Pydantic Models ---

# Available models on AI Builder
AVAILABLE_MODELS = [
    "grok-4-fast",
    "deepseek",
    "supermind-agent-v1", 
    "gemini-2.5-pro",
    "gemini-3-flash-preview",
    "gpt-5"
]

class ChatRequest(BaseModel):
    query: str
    model: Optional[str] = "grok-4-fast"

class ChatResponse(BaseModel):
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None

# --- Tools ---

def web_search(query: str) -> str:
    """
    Search the web using the internal AI Builder Search API.
    
    Args:
        query: The search query string.
        
    Returns:
        JSON string of search results or error message.
    """
    url = "https://space.ai-builders.com/backend/v1/search/"
    headers = {
        "Authorization": f"Bearer {AI_BUILDER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "keywords": [query],
        "max_results": 3
    }
    
    logger.info(f"Executing internal web search for: {query}")
    try:
        # synchronous call for simplicity in this demo, ideally use async client
        with httpx.Client() as http_client:
            response = http_client.post(url, headers=headers, json=payload, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Search API response status: {response.status_code}")
            return json.dumps(data)
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        logger.error(error_msg)
        return error_msg

def read_page(url: str) -> str:
    """
    Fetch a URL and extract the main text content from HTML.
    
    Args:
        url: The URL to fetch.
        
    Returns:
        Extracted text content or error message.
    """
    logger.info(f"Fetching page: {url}")
    try:
        with httpx.Client() as http_client:
            response = http_client.get(url, timeout=15.0, follow_redirects=True)
            response.raise_for_status()
            html = response.text
            
            # Remove script and style elements
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', html)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            # Truncate to avoid token limits
            if len(text) > 8000:
                text = text[:8000] + "... [truncated]"
            
            logger.info(f"Page fetched successfully, extracted {len(text)} chars")
            return text
    except Exception as e:
        error_msg = f"Failed to read page: {str(e)}"
        logger.error(error_msg)
        return error_msg

# Tool definitions for the LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for real-time information, news, or specific facts. Use this tool when you need information that you don't have or to get the latest updates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on the internet."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_page",
            "description": "Fetch and read the content of a specific web page. Use this when you have a URL and need to extract detailed information from that page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The full URL of the web page to read."
                    }
                },
                "required": ["url"]
            }
        }
    }
]

# --- Endpoints ---

@app.get("/welcome/{name}")
async def welcome_user(name: str):
    """
    Welcome a user by their name.
    """
    return {"message": f"Hello, welcome {name} to this FastAPI"}

@app.get("/")
async def root():
    """
    Serve the chat frontend.
    """
    return FileResponse("static/index.html")

@app.post("/agent/chat", response_model=ChatResponse)
async def agent_chat(request: ChatRequest):
    """
    Agentic chat endpoint with full execution loop.
    
    Uses `grok-4-fast` with the `web_search` tool.
    Loops up to max_turns times to handle multi-step reasoning.
    """
    max_turns = 3
    messages = [
        {
            "role": "system", 
            "content": "You are a helpful AI assistant with access to web search. When you need to search, preserve as much detail from the user's original question as possible in your search query. If the user asks for specific information (like version numbers, breaking changes, or features), include those details in your search query."
        },
        {
            "role": "user", 
            "content": request.query
        }
    ]
    all_tool_calls = []
    
    print(f"\n{'='*60}")
    print(f"[User] Query: {request.query}")
    print(f"[Model] Using: {request.model}")
    print(f"{'='*60}")

    try:
        for turn in range(max_turns):
            print(f"\n[Agent] Turn {turn + 1}/{max_turns} - Calling LLM...")
            
            response = client.chat.completions.create(
                model=request.model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason
            
            print(f"[Agent] Finish Reason: {finish_reason}")
            
            # If the model wants to call tools
            if message.tool_calls:
                print(f"[Agent] Decided to call {len(message.tool_calls)} tool(s)")
                messages.append(message)  # Add assistant message with tool_calls
                
                for tc in message.tool_calls:
                    function_name = tc.function.name
                    function_args = json.loads(tc.function.arguments)
                    query = function_args.get("query", "")
                    
                    print(f"[Agent] -> Tool: '{function_name}' | Query: '{query}'")
                    all_tool_calls.append({"name": function_name, "arguments": tc.function.arguments})
                    
                    if function_name == "web_search":
                        tool_output = web_search(function_args.get("query", ""))
                        # Truncate for display
                        display_output = tool_output[:200] + "..." if len(tool_output) > 200 else tool_output
                        print(f"[System] Tool Output (truncated): {display_output}")
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "name": function_name,
                            "content": tool_output
                        })
                    elif function_name == "read_page":
                        url = function_args.get("url", "")
                        print(f"[Agent] -> Tool: '{function_name}' | URL: '{url}'")
                        tool_output = read_page(url)
                        # Truncate for display
                        display_output = tool_output[:200] + "..." if len(tool_output) > 200 else tool_output
                        print(f"[System] Tool Output (truncated): {display_output}")
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "name": function_name,
                            "content": tool_output
                        })
                    else:
                        print(f"[System] Unknown tool: {function_name}")
                
                # If this was the last turn, force a final answer
                if turn == max_turns - 1:
                    print(f"\n[Agent] Final turn reached. Requesting synthesis...")
                    final_response = client.chat.completions.create(
                        model=request.model,
                        messages=messages + [{
                            "role": "system",
                            "content": "Based on the search results you just received, provide your best answer to the user's question now. If you don't have enough information, synthesize what you do know."
                        }]
                    )
                    final_answer = final_response.choices[0].message.content or ""
                    print(f"\n[Agent] Final Answer: {final_answer[:300]}..." if len(final_answer) > 300 else f"\n[Agent] Final Answer: {final_answer}")
                    print(f"{'='*60}\n")
                    
                    return ChatResponse(
                        response=final_answer,
                        tool_calls=all_tool_calls if all_tool_calls else None
                    )
                
                # Continue to next turn to process tool results
                continue
            
            # No tool calls - we have a final answer
            final_answer = message.content or ""
            print(f"\n[Agent] Final Answer: {final_answer[:300]}..." if len(final_answer) > 300 else f"\n[Agent] Final Answer: {final_answer}")
            print(f"{'='*60}\n")
            
            return ChatResponse(
                response=final_answer,
                tool_calls=all_tool_calls if all_tool_calls else None
            )
        
        # If we exhausted all turns without a final answer (shouldn't happen with the above logic)
        print(f"[Agent] Max turns reached without final answer. Returning fallback.")
        final_answer = "I apologize, but I couldn't complete the request within the allowed number of steps."
        print(f"{'='*60}\n")
        
        return ChatResponse(
            response=final_answer,
            tool_calls=all_tool_calls if all_tool_calls else None
        )

    except Exception as e:
        error_msg = f"Chat failed: {str(e)}"
        print(f"[Error] {error_msg}")
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=str(e))


