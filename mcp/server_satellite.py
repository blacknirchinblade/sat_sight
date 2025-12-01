"""
MCP Server for Sat-Sight
Exposes Sat-Sight capabilities as Model Context Protocol tools.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    Server = None
    stdio_server = None
    Tool = None
    TextContent = None

from sat_sight.core.workflow import run_workflow

logger = logging.getLogger(__name__)


class SatSightMCPServer:
    """MCP Server exposing Sat-Sight satellite analysis capabilities."""
    
    def __init__(self):
        """Initialize MCP server."""
        self.app = Server("sat-sight-server") if Server else None
        if not self.app:
            logger.warning("MCP library not installed. Server functionality disabled.")
            return
        
        self._register_tools()
        logger.info("Sat-Sight MCP Server initialized")
    
    def _register_tools(self):
        """Register available tools."""
        if not self.app:
            return
        
        @self.app.list_tools()
        async def list_tools() -> List[Tool]:
            """List available Sat-Sight tools."""
            return [
                Tool(
                    name="analyze_satellite_image",
                    description="Analyze a satellite image using CLIP-based classification and retrieval. Identifies land cover types, features, and similar images.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "image_path": {
                                "type": "string",
                                "description": "Absolute path to satellite image file"
                            },
                            "query": {
                                "type": "string",
                                "description": "Optional query about the image (e.g., 'What land cover is shown?')"
                            }
                        },
                        "required": ["image_path"]
                    }
                ),
                Tool(
                    name="search_satellite_images",
                    description="Search for satellite images by description (e.g., 'show me forests', 'urban areas'). Returns similar images from the database.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query describing desired satellite images"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of images to return (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="environmental_query",
                    description="Ask questions about environmental topics, land use, climate change, deforestation, etc. Uses knowledge base of 5000+ documents.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Environmental question or topic"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="web_search_satellites",
                    description="Search the web for latest satellite imagery news, monitoring reports, and real-time environmental data.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for latest satellite/environmental information"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="multi_modal_analysis",
                    description="Perform comprehensive analysis combining image analysis, knowledge base search, and web search.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Comprehensive query"
                            },
                            "image_path": {
                                "type": "string",
                                "description": "Optional image path for multi-modal analysis"
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]
        
        @self.app.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "analyze_satellite_image":
                    return await self._analyze_image(arguments)
                elif name == "search_satellite_images":
                    return await self._search_images(arguments)
                elif name == "environmental_query":
                    return await self._environmental_query(arguments)
                elif name == "web_search_satellites":
                    return await self._web_search(arguments)
                elif name == "multi_modal_analysis":
                    return await self._multi_modal_analysis(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _analyze_image(self, args: Dict[str, Any]) -> List[TextContent]:
        """Analyze satellite image."""
        image_path = args.get("image_path", "")
        query = args.get("query", "Analyze this satellite image")
        
        response, state = run_workflow(query=query, image_path=image_path)
        
        result = {
            "analysis": response,
            "confidence": state.get("confidence_score"),
            "agents_used": state.get("completed_sources", [])
        }
        
        if state.get("retrieved_image_metadata"):
            result["similar_images"] = [
                {
                    "label": img.get("label"),
                    "path": img.get("image_path")
                }
                for img in state["retrieved_image_metadata"][:3]
            ]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _search_images(self, args: Dict[str, Any]) -> List[TextContent]:
        """Search for satellite images."""
        query = args.get("query", "")
        limit = args.get("limit", 5)
        
        response, state = run_workflow(query=f"Show me {query}")
        
        result = {
            "query": query,
            "results": []
        }
        
        if state.get("retrieved_image_metadata"):
            distances = state.get("retrieved_image_distances", [])
            for i, img in enumerate(state["retrieved_image_metadata"][:limit]):
                result["results"].append({
                    "label": img.get("label"),
                    "path": img.get("image_path"),
                    "similarity": f"{1 - distances[i]:.3f}" if i < len(distances) else "N/A"
                })
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _environmental_query(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle environmental query."""
        query = args.get("query", "")
        
        response, state = run_workflow(query=query)
        
        result = {
            "answer": response,
            "sources": state.get("completed_sources", []),
            "confidence": state.get("confidence_score")
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _web_search(self, args: Dict[str, Any]) -> List[TextContent]:
        """Perform web search."""
        query = args.get("query", "")
        
        response, state = run_workflow(query=f"Latest {query}")
        
        result = {
            "query": query,
            "answer": response,
            "web_sources": len(state.get("web_snippets", []))
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _multi_modal_analysis(self, args: Dict[str, Any]) -> List[TextContent]:
        """Perform multi-modal analysis."""
        query = args.get("query", "")
        image_path = args.get("image_path", "")
        
        response, state = run_workflow(query=query, image_path=image_path)
        
        result = {
            "analysis": response,
            "modalities_used": state.get("completed_sources", []),
            "confidence": state.get("confidence_score"),
            "thinking_process": len(state.get("thinking_process", []))
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def run(self):
        """Run the MCP server."""
        if not self.app or not stdio_server:
            logger.error("Cannot run server: MCP library not installed")
            return
        
        logger.info("Starting Sat-Sight MCP Server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.app.run(read_stream, write_stream)


async def main():
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)
    server = SatSightMCPServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
