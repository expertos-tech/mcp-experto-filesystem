<!-- AGENTS SUMMARY
Architectural boundaries, communication protocols, and standardized contracts for the MCP server.  
Sessions:
- PROTOCOL-DISTRIBUTION: Rules for stdio usage and local security.
- INITIALIZATION-DISCOVERY: How the server handles the initialize hook and self-discovery tools.
- STANDARD-PAYLOAD: Schema and field definitions for the Universal Response Payload.
- DESIGN-PHILOSOPHY: Rationale behind the structured communication approach.
-->

# System Architecture and Protocol Contracts

## Table of Contents

* [Protocol and Distribution](#protocol-and-distribution)
* [Initialization and Self-Discovery](#initialization-and-self-discovery)
* [Standard Response Payload (The Universal Contract)](#standard-response-payload-the-universal-contract)
* [Design Philosophy](#design-philosophy)

---

<!-- START PROTOCOL-DISTRIBUTION -->
## 1. Protocol and Distribution

### 1.1 Local Execution via stdio
Given its nature as a filesystem automation tool, the MCP server must always operate via stdio.  
This ensures:
* **Security:** No network ports are opened on the host machine.  
* **Locality:** The agent executing the commands runs in the same environment as the codebase.  
* **Simplicity:** No complex authentication or network routing is required.  
<!-- END PROTOCOL-DISTRIBUTION -->

---

<!-- START INITIALIZATION-DISCOVERY -->
## 2. Initialization and Self-Discovery

To prevent LLMs from guessing how to use the server, the system provides aggressive self-discovery mechanisms.  

### 2.1 The initialize Hook
Upon connection, the server must return a comprehensive Getting Started payload. This payload will contain a brief  
summary of all available tools, their purposes, and basic rules of engagement.  

### 2.2 The get_help Tool
A dedicated get_help tool must be exposed to allow agents to query documentation dynamically.  

* **get_help()** (no arguments): Returns the full initialization documentation (overview of all tools).  
* **get_help(topic="standards")**: Returns the strict instructions on how to parse the standard response payload.  
* **get_help(topic="[Tool Name]")**: Returns detailed, specific instructions for a particular tool.  
<!-- END INITIALIZATION-DISCOVERY -->

---

<!-- START STANDARD-PAYLOAD -->
## 3. Standard Response Payload (The Universal Contract)

Every tool exposed by this MCP server must return a strictly typed JSON response. This ensures the AI agent can  
parse responses predictably, regardless of the tool used.  

### 3.1 Payload Schema

```json
{
  "status": 200,
  "message": "Operation completed successfully.",
  "data": {},
  "error": null,
  "meta": {
    "warnings": [],
    "next_steps": []
  },
  "metrics": {
    "execution_time_ms": 120.5,
    "approx_input_tokens": 45,
    "approx_output_tokens": 300,
    "input_bytes": 150,
    "output_bytes": 1200
  }
}
```

### 3.2 Field Definitions

* **status (integer):** HTTP-like status codes (200, 400, 403, 404, 500).  
* **message (string):** A brief summary of the operation result.  
* **data (object | array):** The actual tool payload. Must be empty if status >= 400.  
* **error (object | null):** Present only if status >= 400. Contains specific failure details.  
* **meta (object):** Contains warnings and next_steps to guide the agent.  
* **metrics (object):** Telemetry data to monitor token economy and performance.  
<!-- END STANDARD-PAYLOAD -->

---

<!-- START DESIGN-PHILOSOPHY -->
## 4. Design Philosophy

By forcing all tools through this Universal Contract, we ensure that:
1. The LLM never has to parse unstructured text dumps.  
2. Token consumption is transparent and observable.  
3. Errors are handled gracefully with clear status codes.  
<!-- END DESIGN-PHILOSOPHY -->
