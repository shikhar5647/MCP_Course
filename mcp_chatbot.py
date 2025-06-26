from mcp.client.stdio import stdio_client
from typing import List, TypedDict , Dict
import asyncio
import nest_asyncio
from mcp import StdioServerParameters,types, ClientSession
from dotenv import load_dotenv
from google import genai 
from google.genai import types 
import os
from contextlib import AsyncExitStack
import json
from google.generativeai.types import GenerateContentConfig
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

class ToolDefinition(TypedDict):
    name: str
    description: str
    input_schema: dict

class MCP_Chatbot:
    def __init__(self):
        self.available_tools: List[ToolDefinition] = [] # new
        self.tool_to_session: Dict[str, ClientSession] = {} # new
        self.sessions: List[ClientSession] = [] # new
        self.exit_stack = AsyncExitStack() # new
        self.model = genai.GenerativeModel("gemini-2.5-pro-exp-03-25")
        
    