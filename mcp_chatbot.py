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
                config=types.GenerateContentConfig(
                    temperature=0,
                    tools=self.available_toolsavailable_tools,
                ),
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
                    result = await self.session.call_tool(tool_name, arguments=tool_args)
                    messages.append({"role": "user", 
                                      "content": [
                                          {
                                              "type": "tool_result",
                                              "tool_use_id":tool_id,
                                              "content": result.content
                                          }
                                      ]
                                    })
                    response = client.models.generate_content(
                        model="gemini-2.5-pro-exp-03-25",
                        config=types.GenerateContentConfig(
                            temperature=0,
                            tools=self.available_toolsavailable_tools,
                            ),
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