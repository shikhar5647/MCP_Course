from mcp.client.stdio import stdio_client
from typing import List 
import asyncio
import nest_asyncio
from mcp import StdioServerParameters,types, ClientSession
from dotenv import load_dotenv
from google import genai 
from google.genai import types 
import os
nest_asyncio.apply()
load_dotenv()
client = genai.Client(os.getenv['GEMINI_API_KEY'])

class MCP_Chatbot:
    def __init__(self):
        self.available_tools: List[dict] = []
        self.session: ClientSession = None
        
    async def process_query(self, query):
        messages = [{'role':'user', 'content':query}]
        response = client.models.generate_content(
                model="gemini-2.5-pro-exp-03-25",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    tools=available_tools,
                ),
            )
        process_query = True
    