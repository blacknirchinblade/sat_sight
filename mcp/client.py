"""
MCP Client for Sat-Sight
Allows Sat-Sight to use external MCP tools and services.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from mcp.client import ClientSession
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    ClientSession = None
    stdio_client = None
    MCP_AVAILABLE = False


class MCPClient:
    """Client for connecting to external MCP servers."""
    
    def __init__(self):
        """Initialize MCP client."""
        self.sessions: Dict[str, Any] = {}
        self.available_tools: Dict[str, List[Dict]] = {}
        
        if not MCP_AVAILABLE:
            logger.warning("MCP library not installed. Client functionality disabled.")
        else:
            logger.info("MCP Client initialized")
    
    async def connect_to_server(self, server_name: str, command: str, 
                                args: Optional[List[str]] = None) -> bool:
        """
        Connect to an MCP server.
        
        Args:
            server_name: Unique name for this server connection
            command: Command to start the server
            args: Optional command arguments
            
        Returns:
            True if connection successful
        """
        if not MCP_AVAILABLE:
            logger.error("Cannot connect: MCP library not installed")
            return False
        
        try:
            session = await stdio_client(command, args or [])
            self.sessions[server_name] = session
            
            tools = await session.list_tools()
            self.available_tools[server_name] = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in tools
            ]
            
            logger.info(f"Connected to MCP server '{server_name}' with {len(tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server '{server_name}': {e}")
            return False
    
    def list_available_tools(self, server_name: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        List available tools from connected servers.
        
        Args:
            server_name: Optional specific server name (None = all servers)
            
        Returns:
            Dictionary of server_name -> tools
        """
        if server_name:
            return {server_name: self.available_tools.get(server_name, [])}
        return self.available_tools.copy()
    
    async def call_tool(self, server_name: str, tool_name: str, 
                       arguments: Dict[str, Any]) -> Optional[str]:
        """
        Call a tool on a connected MCP server.
        
        Args:
            server_name: Server name
            tool_name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool response text
        """
        if not MCP_AVAILABLE:
            logger.error("Cannot call tool: MCP library not installed")
            return None
        
        if server_name not in self.sessions:
            logger.error(f"Not connected to server '{server_name}'")
            return None
        
        try:
            session = self.sessions[server_name]
            result = await session.call_tool(tool_name, arguments)
            
            if result and len(result) > 0:
                return result[0].text
            return None
            
        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}' on '{server_name}': {e}")
            return None
    
    async def disconnect(self, server_name: str) -> None:
        """
        Disconnect from an MCP server.
        
        Args:
            server_name: Server name
        """
        if server_name in self.sessions:
            try:
                await self.sessions[server_name].close()
                del self.sessions[server_name]
                del self.available_tools[server_name]
                logger.info(f"Disconnected from MCP server '{server_name}'")
            except Exception as e:
                logger.error(f"Error disconnecting from '{server_name}': {e}")
    
    async def disconnect_all(self) -> None:
        """Disconnect from all MCP servers."""
        for server_name in list(self.sessions.keys()):
            await self.disconnect(server_name)


class MCPToolWrapper:
    """Wrapper for using MCP tools within Sat-Sight agents."""
    
    def __init__(self, client: MCPClient):
        """
        Initialize tool wrapper.
        
        Args:
            client: MCPClient instance
        """
        self.client = client
    
    async def search_external_data(self, query: str, source: str = "web") -> Optional[str]:
        """
        Search external data sources via MCP tools.
        
        Args:
            query: Search query
            source: Source type (web, database, api, etc.)
            
        Returns:
            Search results
        """
        servers = self.client.list_available_tools()
        
        for server_name, tools in servers.items():
            for tool in tools:
                if "search" in tool["name"].lower():
                    logger.info(f"Using MCP tool '{tool['name']}' for external search")
                    result = await self.client.call_tool(
                        server_name,
                        tool["name"],
                        {"query": query, "source": source}
                    )
                    if result:
                        return result
        
        logger.warning("No suitable MCP search tool found")
        return None
    
    async def get_weather_data(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get weather data via MCP tools.
        
        Args:
            location: Location name or coordinates
            
        Returns:
            Weather data dictionary
        """
        servers = self.client.list_available_tools()
        
        for server_name, tools in servers.items():
            for tool in tools:
                if "weather" in tool["name"].lower():
                    result = await self.client.call_tool(
                        server_name,
                        tool["name"],
                        {"location": location}
                    )
                    if result:
                        try:
                            return json.loads(result)
                        except:
                            return {"raw_response": result}
        
        logger.warning("No MCP weather tool found")
        return None
    
    async def get_satellite_data(self, coordinates: Dict[str, float], 
                                 date_range: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get satellite data via MCP tools.
        
        Args:
            coordinates: Lat/lon dictionary
            date_range: Optional start/end dates
            
        Returns:
            Satellite data dictionary
        """
        servers = self.client.list_available_tools()
        
        for server_name, tools in servers.items():
            for tool in tools:
                if "satellite" in tool["name"].lower() or "imagery" in tool["name"].lower():
                    args = {"coordinates": coordinates}
                    if date_range:
                        args["date_range"] = date_range
                    
                    result = await self.client.call_tool(server_name, tool["name"], args)
                    if result:
                        try:
                            return json.loads(result)
                        except:
                            return {"raw_response": result}
        
        logger.warning("No MCP satellite data tool found")
        return None


mcp_client_instance = MCPClient()


def get_mcp_client() -> MCPClient:
    """Get singleton MCP client instance."""
    return mcp_client_instance
