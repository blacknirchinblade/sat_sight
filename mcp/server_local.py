"""
Local MCP Server for Development and Testing
A simple MCP server that provides basic tools for local development.
"""

import logging
import json
from typing import Dict, Any, List
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    Server = None
    stdio_server = None
    Tool = None
    TextContent = None
    MCP_AVAILABLE = False


class LocalMCPServer:
    """Local MCP server for testing and development."""
    
    def __init__(self):
        """Initialize local MCP server."""
        if not MCP_AVAILABLE:
            logger.warning("MCP library not installed")
            self.app = None
            return
        
        self.app = Server("local-dev-server")
        self._register_tools()
        logger.info("Local MCP Server initialized")
    
    def _register_tools(self):
        """Register development tools."""
        if not self.app:
            return
        
        @self.app.list_tools()
        async def list_tools() -> List[Tool]:
            """List available development tools."""
            return [
                Tool(
                    name="echo",
                    description="Echo back the input message (for testing)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to echo"
                            }
                        },
                        "required": ["message"]
                    }
                ),
                Tool(
                    name="list_local_images",
                    description="List satellite images in the local data directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory path (default: data/images)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of images to list",
                                "default": 10
                            }
                        }
                    }
                ),
                Tool(
                    name="get_system_info",
                    description="Get system information (CPU, memory, disk)",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.app.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "echo":
                    return await self._echo(arguments)
                elif name == "list_local_images":
                    return await self._list_images(arguments)
                elif name == "get_system_info":
                    return await self._system_info(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _echo(self, args: Dict[str, Any]) -> List[TextContent]:
        """Echo tool for testing."""
        message = args.get("message", "")
        return [TextContent(type="text", text=f"Echo: {message}")]
    
    async def _list_images(self, args: Dict[str, Any]) -> List[TextContent]:
        """List local satellite images."""
        directory = args.get("directory", "data/images")
        limit = args.get("limit", 10)
        
        data_dir = project_root / directory
        if not data_dir.exists():
            return [TextContent(type="text", text=f"Directory not found: {directory}")]
        
        image_extensions = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
        images = []
        
        for ext in image_extensions:
            images.extend(data_dir.glob(f"*{ext}"))
            if len(images) >= limit:
                break
        
        images = images[:limit]
        
        result = {
            "directory": str(data_dir),
            "total_found": len(images),
            "images": [
                {
                    "name": img.name,
                    "path": str(img),
                    "size_mb": img.stat().st_size / (1024 * 1024)
                }
                for img in images
            ]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _system_info(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get system information."""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            info = {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "percent": disk.percent
                }
            }
            
            return [TextContent(type="text", text=json.dumps(info, indent=2))]
        except ImportError:
            return [TextContent(type="text", text="psutil not installed")]
    
    async def run(self):
        """Run the MCP server."""
        if not self.app or not stdio_server:
            logger.error("Cannot run: MCP library not installed")
            return
        
        logger.info("Starting Local MCP Server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.app.run(read_stream, write_stream)


async def main():
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)
    server = LocalMCPServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
