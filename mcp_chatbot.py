from mcp.client.stdio import stdio_client
from typing import List 
import asyncio
import nest_asyncio
from mcp import StdioServerParameters,types, ClientSession
from dotenv import load_dotenv