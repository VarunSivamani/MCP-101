# MCP Transport

- MCP uses JSON-RPC to encode messages. 
- JSON-RPC messages MUST be UTF-8 encoded.

## Types
1. stdio, communication over standard in and standard out
2. HTTP with SSE
3. Streamable HTTP

**Note : Clients SHOULD support stdio whenever possible.**

### 1. stdio

In the stdio transport:
- The client launches the MCP server as a subprocess.
- The client MUST NOT write anything to the server’s stdin that is not a valid MCP message.
- The server MUST NOT write anything to its stdout that is not a valid MCP message.
- Messages are individual JSON-RPC requests, notifications, or responses.
- Messages are delimited by newlines, and MUST NOT contain embedded newlines.


### 2. HTTP with SSE

In the SSE transport, the server operates as an independent process that can handle multiple client connections.

The server MUST provide two endpoints:
- An SSE endpoint, for clients to establish a connection and receive messages from the server.
- A regular HTTP POST endpoint for clients to send messages to the server.
- URL: https://example.com/sse

#### Security Warning
- Servers MUST / SHOULD
    - validate the Origin header on all incoming connections.
    - bind only to localhost (127.0.0.1) rather than all network interfaces (0.0.0.0)
    - implement proper authentication for all connections.

### 3. Streamable HTTP (HTTP+SSE transport)

- The server operates as an independent process that can handle multiple client connections and uses HTTP POST and GET requests.
- Server can optionally make use of Server-Sent Events (SSE) to stream multiple server messages (permits basic MCP servers, as well as more feature-rich servers supporting streaming and server-to-client notifications and requests).

- The server MUST provide a single HTTP endpoint path (hereafter referred to as the MCP endpoint) that supports both POST and GET methods.
- URL: https://example.com/mcp

#### Security Warning
- Servers MUST / SHOULD
    - validate the Origin header on all incoming connections.
    - bind only to localhost (127.0.0.1) rather than all network interfaces (0.0.0.0)
    - implement proper authentication for all connections.
