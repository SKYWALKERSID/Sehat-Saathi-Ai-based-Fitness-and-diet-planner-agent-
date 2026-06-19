import sys
import json
import traceback

# Import individual MCP tools
from backend.mcp.nutrition import lookup_food_nutrition
from backend.mcp.exercise import lookup_exercise
from backend.mcp.health_knowledge import lookup_health_standards
from backend.mcp.progress import analyze_progress_history
from backend.mcp.weather import fetch_weather_recommendation
from backend.mcp.hydration import calculate_hydration_target
from backend.mcp.rag import query_rag_knowledge_base

def list_mcp_tools():
    """Returns the list of tools offered by this unified MCP server."""
    return [
        {
            "name": "nutrition_lookup",
            "description": "Nutrition MCP: Lookup macro and micronutrient profiles for foods.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "food_name": {"type": "string", "description": "The name of the food item, e.g. Paneer, Chicken Breast."}
                },
                "required": ["food_name"]
            }
        },
        {
            "name": "exercise_lookup",
            "description": "Exercise MCP: Lookup targeted muscle groups, MET levels, and sets/reps details for exercises.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "exercise_name": {"type": "string", "description": "The name of the exercise, e.g. Squats, Deadlift."}
                },
                "required": ["exercise_name"]
            }
        },
        {
            "name": "health_knowledge_lookup",
            "description": "Health Knowledge MCP: Retrieve clinical BMI guidelines, WHO exercise standards, or medical risk suggestions.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to search, e.g. BMI, WHO, diabetes, asthma."}
                },
                "required": ["topic"]
            }
        },
        {
            "name": "progress_analyze",
            "description": "Progress MCP: Analyze weight log velocity (kg/week) and compute hydration/sleep compliance indexes.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "history_logs": {
                        "type": "array", 
                        "items": {"type": "object"},
                        "description": "Array of daily logs containing weight, water, sleep, log_date."
                    },
                    "target_goal": {"type": "string", "description": "Primary goal to verify velocity boundaries, e.g. Weight Loss."}
                },
                "required": ["history_logs", "target_goal"]
            }
        },
        {
            "name": "weather_lookup",
            "description": "Weather MCP: Lookup current temperature and receive suggestions for indoor vs. outdoor scaling.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number", "description": "Location latitude coordinate."},
                    "longitude": {"type": "number", "description": "Location longitude coordinate."}
                }
            }
        },
        {
            "name": "hydration_calculate",
            "description": "Hydration MCP: Dynamically compute standard water targets (Liters/day) based on body weight, workout levels, and heat factors.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "weight_kg": {"type": "number", "description": "Body mass weight in kilograms."},
                    "activity_level": {"type": "string", "description": "Activity rating, e.g. Sedentary, Moderately Active."},
                    "temperature_c": {"type": "number", "description": "Outdoor temperature in Celsius degrees."}
                },
                "required": ["weight_kg", "activity_level"]
            }
        },
        {
            "name": "rag_search",
            "description": "RAG MCP: Semantic retrieval search over fitness, WHO guidelines, and injury-safe workout databases.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search question or query term."},
                    "top_k": {"type": "integer", "description": "Maximum matching results to return (default 3)."}
                },
                "required": ["query"]
            }
        }
    ]

def call_mcp_tool(name: str, arguments: dict) -> dict:
    """Executes the specific tool matching the name and returns standard text content response."""
    try:
        if name == "nutrition_lookup":
            res = lookup_food_nutrition(arguments["food_name"])
        elif name == "exercise_lookup":
            res = lookup_exercise(arguments["exercise_name"])
        elif name == "health_knowledge_lookup":
            res = lookup_health_standards(arguments["topic"])
        elif name == "progress_analyze":
            res = analyze_progress_history(arguments["history_logs"], arguments["target_goal"])
        elif name == "weather_lookup":
            lat = arguments.get("latitude", 28.61)
            lon = arguments.get("longitude", 77.20)
            res = fetch_weather_recommendation(lat, lon)
        elif name == "hydration_calculate":
            weight = float(arguments["weight_kg"])
            act = arguments["activity_level"]
            temp = float(arguments.get("temperature_c", 24.0))
            res = calculate_hydration_target(weight, act, temp)
        elif name == "rag_search":
            q = arguments["query"]
            k = int(arguments.get("top_k", 3))
            res = query_rag_knowledge_base(q, k)
        else:
            raise ValueError(f"Unknown MCP Tool name: '{name}'")
            
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(res, indent=2)
                }
            ]
        }
    except Exception as e:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"Error executing tool '{name}': {str(e)}\n{traceback.format_exc()}"
                }
            ]
        }

def run_stdio_server():
    """Main stdio JSON-RPC loop for handling MCP client messages."""
    print("Sehat Saathi unified MCP server is starting over stdio...", file=sys.stderr)
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            
            if method == "initialize":
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "Sehat Saathi Unified MCP Server",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": list_mcp_tools()
                    }
                }
            elif method == "tools/call":
                params = req.get("params", {})
                tool_name = params.get("name")
                args = params.get("arguments", {})
                
                tool_res = call_mcp_tool(tool_name, args)
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": tool_res
                }
            else:
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: '{method}'"
                    }
                }
                
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
            
        except Exception as e:
            err = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal RPC processing error: {str(e)}"
                }
            }
            try:
                sys.stdout.write(json.dumps(err) + "\n")
                sys.stdout.flush()
            except Exception:
                pass
            print(f"Error in stdio loop: {e}", file=sys.stderr)

if __name__ == '__main__':
    run_stdio_server()
