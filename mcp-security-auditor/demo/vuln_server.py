import json
import os
import pickle
import sys
import urllib.request

API_KEY = "sk-live-9f8e7d6c5b4a39281706f5e4d3c2b1a0"


def read_note(path):
    with open(path) as f:
        return f.read()


def run_command(cmd):
    return os.popen("echo " + cmd).read()


def load_state(blob):
    return pickle.loads(blob)


def fetch_page(url):
    return urllib.request.urlopen(url).read().decode()


def current_tools():
    return [
        {"name": "read_note", "description": "Read a note file and return its text.",
         "inputSchema": {"type": "object",
                         "properties": {"path": {"type": "string"}}, "required": ["path"]}},
        {"name": "run_command", "description": "Run a shell command and return its output.",
         "inputSchema": {"type": "object", "properties": {"cmd": {"type": "string"}}}},
    ]


def call(name, args):
    if name == "read_note":
        return read_note(args.get("path", ""))
    if name == "run_command":
        return run_command(args.get("cmd", ""))
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
