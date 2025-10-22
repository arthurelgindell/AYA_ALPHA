#!/usr/bin/env python3
"""
AYA Agent Turbo MCP Server

Exposes Agent Turbo knowledge base capabilities to Claude Desktop via MCP.

Features:
- Semantic search (query_knowledge)
- Knowledge addition (add_knowledge)
- Statistics monitoring (get_stats)
- GPU-accelerated embeddings (MLX Metal, 80 cores)
- PostgreSQL backend (aya_rag)

Installation:
  Requires Python 3.11+ with MCP SDK
  pip install mcp psycopg2-binary numpy requests

Prime Directives Compliance:
- All operations use actual PostgreSQL database
- No mocks, no theatrical wrappers
- Real data flow verification
- Complete audit trail
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Optional

# Add Agent Turbo to Python path
AGENT_TURBO_PATH = Path(__file__).parent.parent.parent / "Agent_Turbo" / "core"
sys.path.insert(0, str(AGENT_TURBO_PATH))

from mcp.server.fastmcp import FastMCP, Context

# Initialize MCP server
mcp = FastMCP("AYA Agent Turbo")

# Global Agent Turbo instance (initialized on first use)
_agent_instance = None

def get_agent():
    """Get or create Agent Turbo instance"""
    global _agent_instance
    if _agent_instance is None:
        try:
            from agent_turbo import AgentTurbo
            _agent_instance = AgentTurbo()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Agent Turbo: {e}")
    return _agent_instance

@mcp.tool()
async def query_knowledge(
    query: str,
    limit: int = 5,
    ctx: Context = None
) -> str:
    """
    Query the Agent Turbo knowledge base with semantic search.

    Args:
        query: Search query text
        limit: Maximum number of results (default: 5)

    Returns:
        JSON string with relevant knowledge entries

    Example:
        query_knowledge("PostgreSQL connection pooling", limit=3)
    """
    if ctx:
        ctx.info(f"Querying knowledge base: '{query}' (limit: {limit})")

    try:
        agent = get_agent()
        # Run sync method in thread pool (Agent Turbo is synchronous)
        result = await asyncio.to_thread(agent.query, query, limit)

        if ctx:
            ctx.info(f"Query completed successfully")

        return result
    except Exception as e:
        error_msg = f"Query failed: {str(e)}"
        if ctx:
            ctx.error(error_msg)
        return json.dumps({"error": error_msg, "query": query})

@mcp.tool()
async def add_knowledge(
    content: str,
    source: str = "mcp",
    knowledge_type: str = "solution",
    ctx: Context = None
) -> str:
    """
    Add new knowledge to the Agent Turbo knowledge base.

    Args:
        content: Knowledge content to add
        source: Source identifier (default: "mcp")
        knowledge_type: Type of knowledge - "solution", "pattern", "concept" (default: "solution")

    Returns:
        JSON string with confirmation and entry ID

    Example:
        add_knowledge("MCP servers use stdio for communication", source="claude-desktop")
    """
    if ctx:
        ctx.info(f"Adding knowledge: {content[:50]}...")

    try:
        agent = get_agent()
        # Run sync method in thread pool
        result = await asyncio.to_thread(
            agent.add,
            content,
            source_session=source,
            knowledge_type=knowledge_type
        )

        if ctx:
            ctx.info("Knowledge added successfully")

        return result
    except Exception as e:
        error_msg = f"Add knowledge failed: {str(e)}"
        if ctx:
            ctx.error(error_msg)
        return json.dumps({"error": error_msg, "content_preview": content[:100]})

@mcp.tool()
async def get_stats(ctx: Context = None) -> str:
    """
    Get Agent Turbo performance statistics.

    Returns:
        JSON string with:
        - Database stats (total entries, embedded percentage)
        - Cache performance (hit rate, size)
        - GPU status (cores, availability)
        - System metrics (uptime, queries)

    Example:
        get_stats()
    """
    if ctx:
        ctx.info("Retrieving Agent Turbo statistics")

    try:
        agent = get_agent()
        # Run sync method in thread pool
        result = await asyncio.to_thread(agent.stats)

        if ctx:
            ctx.info("Statistics retrieved successfully")

        return result
    except Exception as e:
        error_msg = f"Get stats failed: {str(e)}"
        if ctx:
            ctx.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.resource("knowledge://stats")
async def knowledge_stats() -> str:
    """
    Expose knowledge base statistics as an MCP resource.

    This resource auto-refreshes when accessed by Claude Desktop.

    Returns:
        JSON string with current Agent Turbo statistics
    """
    try:
        agent = get_agent()
        result = await asyncio.to_thread(agent.stats)
        return result
    except Exception as e:
        return json.dumps({"error": f"Stats resource failed: {str(e)}"})

# Run the server
if __name__ == "__main__":
    mcp.run()
