#!/usr/bin/env python3
"""Synthetic stdio MCP task manager for opt-in native tests; never a provider connector.

Newline JSON-RPC framing follows the MCP stdio transport specification:
https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/basic/transports.mdx
State/log paths are supplied by the temporary harness, never consumer configuration.
"""
import json
from pathlib import Path
import sys


def tool(name, description, properties, required=()):
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": properties,
                            "required": list(required), "additionalProperties": False}}


STRING = {"type": "string"}
TOOLS = [
    tool("get_board", "Read the selected fixture board schema and authorized capabilities.", {"board": STRING}, ("board",)),
    tool("list_tasks", "Read fixture tasks. Follow next_cursor even if a page is empty. All statuses are returned.",
         {"board": STRING, "cursor": STRING}, ("board",)),
    tool("create_task", "Create a synthetic task; reuse correlation_key to avoid duplicates.",
         {"board": STRING, "title": STRING, "correlation_key": STRING}, ("board", "title", "correlation_key")),
    tool("update_task", "Change one task status using its current revision from a fresh list.",
         {"board": STRING, "id": STRING, "status": STRING, "revision": {"type": "integer"}}, ("board", "id", "status", "revision")),
    tool("delete_task", "Move an identified fixture task to Trash. confirmed must reflect explicit intent for this exact ID.",
         {"board": STRING, "id": STRING, "confirmed": {"type": "boolean"}}, ("board", "id", "confirmed")),
]


def call(state, name, args):
    if args.get("board") != "fixture-project":
        raise ValueError("Unknown or unauthorized board")
    if name == "get_board":
        return {"board": "fixture-project", "title_field": "title", "status_field": "status",
                "status_options": ["Pendente", "Em curso", "Bloqueada", "Concluída", "Triagem"],
                "status_mapping": {"pending": "Pendente", "in_progress": "Em curso", "blocked": "Bloqueada", "done": "Concluída"},
                "permissions": ["read", "create", "update_status", "trash_identified_tasks"]}
    if name == "list_tasks":
        if not args.get("cursor"):
            return {"tasks": [], "next_cursor": "remaining", "has_more": True}
        if args["cursor"] != "remaining":
            raise ValueError("Unknown cursor")
        return {"tasks": [t for t in state["tasks"] if not t.get("trashed")], "has_more": False}
    if name == "create_task":
        key = args.get("correlation_key")
        if not isinstance(key, str) or not key.strip() or not isinstance(args.get("title"), str) or not args["title"].strip():
            raise ValueError("Title and correlation key required")
        existing = next((t for t in state["tasks"] if t.get("correlation_key") == key), None)
        if existing:
            return {"task": existing, "created": False}
        item = {"id": "created-1", "title": args["title"], "status": "Pendente", "revision": 1, "correlation_key": key}
        state["tasks"].append(item)
        return {"task": item, "created": True}
    item = next((t for t in state["tasks"] if t["id"] == args.get("id")), None)
    if not item:
        raise ValueError("Task not found")
    if name == "update_task":
        if args.get("revision") != item["revision"]:
            raise ValueError("Revision conflict; read current task before retrying")
        if args.get("status") not in ("Pendente", "Em curso", "Bloqueada", "Concluída", "Triagem"):
            raise ValueError("Unknown status option")
        item["status"] = args["status"]
        item["revision"] += 1
        return {"task": item, "updated": True}
    if name == "delete_task":
        if args.get("confirmed") is not True:
            raise ValueError("Explicit intent for the identified task is required")
        item["trashed"] = True
        return {"id": item["id"], "trashed": True, "permanent": False}
    raise ValueError("Unknown fixture operation")


def main():
    state_path, log_path = map(Path, sys.argv[1:3])
    for line in sys.stdin:
        request = json.loads(line)
        if "id" not in request:
            continue
        method, params = request.get("method"), request.get("params", {})
        try:
            if method == "initialize":
                result = {"protocolVersion": "2025-11-25", "capabilities": {"tools": {}},
                          "serverInfo": {"name": "dat-fixture-tasks", "version": "1.0.0"}}
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                state = json.loads(state_path.read_text(encoding="utf-8"))
                name, args = params["name"], params.get("arguments", {})
                with log_path.open("a", encoding="utf-8") as log:
                    log.write(json.dumps({"name": name, "arguments": args}) + "\n")
                value = call(state, name, args)
                state_path.write_text(json.dumps(state), encoding="utf-8")
                result = {"content": [{"type": "text", "text": json.dumps(value)}]}
            else:
                raise ValueError("Unsupported fixture method")
            response = {"jsonrpc": "2.0", "id": request["id"], "result": result}
        except (KeyError, ValueError) as error:
            if method == "tools/call":
                response = {"jsonrpc": "2.0", "id": request["id"], "result": {"isError": True,
                            "content": [{"type": "text", "text": str(error)}]}}
            else:
                response = {"jsonrpc": "2.0", "id": request["id"], "error": {"code": -32601, "message": str(error)}}
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
