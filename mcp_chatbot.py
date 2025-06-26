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
        
    async def connect_to_server(self, server_name: str, server_config: dict) -> None:
        """Connect to a single MCP server."""
        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            ) # new
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            ) # new
            await session.initialize()
            self.sessions.append(session)
            
            # List available tools for this session
            response = await session.list_tools()
            tools = response.tools
            print(f"\nConnected to {server_name} with tools:", [t.name for t in tools])
            
            for tool in tools: # new
                self.tool_to_session[tool.name] = session
                self.available_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })
        except Exception as e:
            print(f"Failed to connect to {server_name}: {e}")
            
    async def connect_to_servers(self): # new
        """Connect to all configured MCP servers."""
        try:
            with open("server_config.json", "r") as file:
                data = json.load(file)
            
            servers = data.get("mcpServers", {})
            
            for server_name, server_config in servers.items():
                await self.connect_to_server(server_name, server_config)
        except Exception as e:
            print(f"Error loading server configuration: {e}")
            raise
        
    async def process_query(self, query):
        messages = [{'role':'user', 'content':query}]
        response = self.model.generate_content(
            messages=messages,
            geasyncneration_config=GenerateContentConfig(
                temperature=0,
                tools=self.available_tools,
            )
        )
        process_query = True
        while process_query:
            assistant_content = []
            for content in response.content:
                if content.type =='text':
                    print(content.text)
                    assistant_content.append(content)
                    if(len(response.content) == 1):
                        process_query= False
                elif content.type == 'tool_use':
                    assistant_content.append(content)
                    messages.append({'role':'assistant', 'content':assistant_content})
                    tool_id = content.id
                    tool_args = content.input
                    tool_name = content.name
                    
    
                    print(f"Calling tool {tool_name} with args {tool_args}")
                    # Call a tool
                    session = self.tool_to_session[tool_name] # new
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    messages.append({"role": "user", 
                                      "content": [
                                          {
                                              "type": "tool_result",
                                              "tool_use_id":tool_id,
                                              "content": result.content
                                          }
                                      ]
                                    })
                    response = self.model.generate_content(
                        messages=messages,
                        geasyncneration_config=GenerateContentConfig(
                            temperature=0,
                            tools=self.available_tools,
                            )
                        ) 
                    
                    if(len(response.content) == 1 and response.content[0].type == "text"):
                        print(response.content[0].text)
                        process_query= False
                        
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
        
                if query.lower() == 'quit':
                    break
                    
                await self.process_query(query)
                print("\n")
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def cleanup(self): # new
        """Cleanly close all resources using AsyncExitStack."""
        await self.exit_stack.aclose()
        
async def main():
    chatbot = MCP_ChatBot()
    try:
        await chatbot.connect_to_servers() 
        await chatbot.chat_loop()
    finally:
        await chatbot.cleanup() 
        
if __name__ == "__main__":
    asyncio.run(main())