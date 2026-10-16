import json
import sys
from datetime import datetime, timezone


def add(a, b):
    return a + b


def get_time():
    return datetime.now(timezone.utc).isoformat()


def current_tools():
    return [
        {"name": "add", "description": "Add two integers and return the sum.",
         "inputSchema": {"type": "object",
                         "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                         "required": ["a", "b"]}},
        {"name": "get_time", "description": "Return the current UTC time.",
         "inputSchema": {"type": "object", "properties": {}}},
    ]


def call(name, args):
    if name == "add":
        return add(args.get("a", 0), args.get("b", 0))
    if name == "get_time":
        return get_time()
    return "unknown tool"

def handle(req):
    method = req.get("method")
    if method == "initialize":
        return {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                "serverInfo": {"name": "demo", "version": "1.0"}}
    if method == "tools/list":
        return {"tools": current_tools()}
    if method == "tools/call":
        p = req.get("params", {})
        try:
            text = call(p.get("name"), p.get("arguments", {}))
        except Exception as e:
            text = f"error: {e}"
        return {"content": [{"type": "text", "text": str(text)}]}
    return {}


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    req = json.loads(line)
    if "id" not in req:
        continue
    print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "result": handle(req)}), flush=True)
