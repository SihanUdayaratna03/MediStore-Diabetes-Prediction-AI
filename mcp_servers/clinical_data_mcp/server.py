import asyncio
import chromadb
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

app = Server("clinical-data-mcp-server")

# Build absolute path so this works regardless of working directory
DB_PATH = str(Path(__file__).resolve().parents[2] / "data" / "chroma_db")
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection(name="medical_guidelines")

TOOLS = [
    types.Tool(
        name="semantic_search",
        description="Search the medical knowledge base for guidelines, treatments, and facts.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The medical question or keywords to search for."
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of relevant documents to return (default is 2)."
                }
            },
            "required": ["query"]
        }
    )
]


async def handle_list_tools(req: types.ListToolsRequest) -> types.ListToolsResult:
    """Tells the connecting Agent what tools are available."""
    return types.ListToolsResult(tools=TOOLS)


async def handle_call_tool(req: types.CallToolRequest) -> types.CallToolResult:
    """Executes the tool when requested by the Agent."""
    name = req.params.name
    arguments = req.params.arguments or {}

    if name == "semantic_search":
        query = arguments.get("query")
        n_results = arguments.get("num_results", 2)

        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )

        formatted_results = "Search Results:\n\n"
        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            formatted_results += f"- (Source: {meta['source']}): {doc}\n"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=formatted_results)]
        )

    raise ValueError(f"Unknown tool: {name}")


# Register handlers
app.add_request_handler("tools/list", types.ListToolsRequest, handle_list_tools)
app.add_request_handler("tools/call", types.CallToolRequest, handle_call_tool)


async def main():
    print("Starting Clinical Data MCP Server...", flush=True)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
