import os
import sys
from dotenv import load_dotenv 
import google.generativeai as genai 
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters 
from backend.config import MCP_SERVERS_DIR
from backend.rag.prompts import ANALYST_AGENT_PROMPT

#Setup

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

PYTHON = sys.executable

KNOWLEDGE_MCP_SERVER = str(MCP_SERVERS_DIR / "knowledge_mcp" / "server.py")

# Retriever Agent 

class RetrieverAgent:
    async def retrieve(self, query: str, num_results: int = 2) -> str:

        server_params = StdioServerParameters(
            command=PYTHON,
            args=[KNOWLEDGE_MCP_SERVER],
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                result = await session.call_tool(
                    "semantic_search",
                    {"query": query, "num_results": num_results}
                )

                if result.content:
                    return result.content[0].text
                return "No relevant documents found."

# AnalystAgent

class AnalystAgent:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=ANALYST_AGENT_PROMPT
        )

    def analyse(self, patient_context: str, retrieved_docs: str) -> str:
        prompt = f"""
Patient Context:
{patient_context}

Retrieved Medical Guidelines:
{retrieved_docs}

Please provide a clear, empathetic clinical analysis based on the above.
"""
        response = self.model.generate_content(prompt)
        return response.text