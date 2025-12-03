# server_custom.py
# Custom MCP SSE Server - No host validation
# Bu dosya FastMCP'nin host validation sorununu bypass eder

import os
import json
import asyncio
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse

from tools.clean_price import clean_price as clean_price_core
from tools.insert_listing import insert_listing as insert_listing_core
from tools.search_listings import search_listings as search_listings_core
from tools.update_listing import update_listing as update_listing_core
from tools.delete_listing import delete_listing as delete_listing_core
from tools.list_user_listings import list_user_listings as list_user_listings_core

app = FastAPI(title="Pazarglobal MCP Server")

# Tool definitions for MCP protocol
TOOLS = [
    {
        "name": "clean_price_tool",
        "description": "Fiyat metnini temizler ve sayısal değeri döndürür",
        "inputSchema": {
            "type": "object",
            "properties": {
                "price_text": {"type": "string", "description": "Temizlenecek fiyat metni"}
            }
        }
    },
    {
        "name": "search_listings_tool",
        "description": "Supabase'den ilan arar",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "category": {"type": "string"},
                "condition": {"type": "string"},
                "location": {"type": "string"},
                "min_price": {"type": "integer"},
                "max_price": {"type": "integer"},
                "limit": {"type": "integer", "default": 10},
                "metadata_type": {"type": "string"}
            }
        }
    },
    {
        "name": "insert_listing_tool",
        "description": "Yeni ilan ekler",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "user_id": {"type": "string"},
                "price": {"type": "integer"},
                "condition": {"type": "string"},
                "category": {"type": "string"},
                "description": {"type": "string"},
                "location": {"type": "string"},
                "stock": {"type": "integer"},
                "metadata": {"type": "object"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "update_listing_tool",
        "description": "Mevcut ilanı günceller",
        "inputSchema": {
            "type": "object",
            "properties": {
                "listing_id": {"type": "string"},
                "title": {"type": "string"},
                "price": {"type": "integer"},
                "condition": {"type": "string"},
                "category": {"type": "string"},
                "description": {"type": "string"},
                "location": {"type": "string"},
                "stock": {"type": "integer"},
                "metadata": {"type": "object"}
            },
            "required": ["listing_id"]
        }
    },
    {
        "name": "delete_listing_tool",
        "description": "İlanı siler",
        "inputSchema": {
            "type": "object",
            "properties": {
                "listing_id": {"type": "string"}
            },
            "required": ["listing_id"]
        }
    },
    {
        "name": "list_user_listings_tool",
        "description": "Kullanıcının tüm ilanlarını listeler",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "limit": {"type": "integer", "default": 20}
            },
            "required": ["user_id"]
        }
    }
]

async def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute a tool and return result"""
    print(f"🔧 Executing tool: {tool_name} with args: {arguments}")
    
    try:
        if tool_name == "clean_price_tool":
            result = clean_price_core(arguments.get("price_text"))
            return {"success": True, "result": result}
            
        elif tool_name == "search_listings_tool":
            result = await search_listings_core(**arguments)
            return {"success": True, "result": result}
            
        elif tool_name == "insert_listing_tool":
            result = await insert_listing_core(**arguments)
            return {"success": True, "result": result}
            
        elif tool_name == "update_listing_tool":
            result = await update_listing_core(**arguments)
            return {"success": True, "result": result}
            
        elif tool_name == "delete_listing_tool":
            result = await delete_listing_core(**arguments)
            return {"success": True, "result": result}
            
        elif tool_name == "list_user_listings_tool":
            result = await list_user_listings_core(**arguments)
            return {"success": True, "result": result}
            
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
            
    except Exception as e:
        print(f"❌ Tool execution error: {str(e)}")
        return {"success": False, "error": str(e)}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "server": "Pazarglobal MCP Server (Custom)", "tools": len(TOOLS)}


@app.get("/sse")
async def sse_endpoint(request: Request):
    """
    SSE endpoint for MCP protocol communication
    NO HOST VALIDATION - works with Railway proxy
    """
    print(f"📡 SSE connection from: {request.client.host}")
    
    async def event_generator():
        # Send initial connection message
        yield {
            "event": "endpoint",
            "data": json.dumps({
                "jsonrpc": "2.0",
                "method": "endpoint",
                "params": {
                    "endpoint": "/messages"
                }
            })
        }
        
        # Keep connection alive
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break
                
            # Send ping to keep connection alive
            yield {
                "event": "ping",
                "data": ""
            }
            
            await asyncio.sleep(30)
    
    return EventSourceResponse(event_generator())


@app.post("/messages")
async def messages_endpoint(request: Request):
    """Handle MCP protocol messages"""
    try:
        body = await request.json()
        print(f"📨 Received message: {body}")
        
        method = body.get("method")
        
        # Handle initialize
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "pazarglobal-mcp-python",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {}
                    }
                }
            }
        
        # Handle tools/list
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "tools": TOOLS
                }
            }
        
        # Handle tools/call
        elif method == "tools/call":
            params = body.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            result = await execute_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False)
                        }
                    ]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            
    except Exception as e:
        print(f"❌ Error handling message: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "id": body.get("id", None),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("\n" + "="*60)
    print("🚀 Pazarglobal MCP Server (Custom Implementation)")
    print("⚠️  FastMCP bypass edildi - Railway proxy uyumlu")
    print(f"📡 Host: {host}:{port}")
    print(f"🔧 Tools: {len(TOOLS)} available")
    print(f"🌐 SSE Endpoint: http://{host}:{port}/sse")
    print(f"📨 Messages Endpoint: http://{host}:{port}/messages")
    print("="*60 + "\n")
    
    uvicorn.run(app, host=host, port=port, log_level="info")
