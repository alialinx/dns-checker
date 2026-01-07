# DNS Checker

This project is a backend service that performs DNS queries against multiple DNS resolvers and streams the results to clients in real time via WebSocket.

It is designed as a learning project to explore DNS behavior, concurrency, WebSocket communication, and basic rate limiting.

---

## Overview

DNS results may vary depending on:
- Resolver location
- DNS propagation state
- Network latency

This service sends the same DNS query to multiple resolvers and compares their responses in real time.

---

## Features

- Query multiple DNS resolvers in parallel
- Measure DNS response latency per resolver
- Extract TTL values from DNS answers
- Stream results in real time using WebSocket
- Store query results in MongoDB
- IP-based rate limiting (minute / hour / day)

---

## How It Works

1. DNS resolver definitions are loaded from MongoDB.
2. A client sends a DNS query request via WebSocket.
3. The same query is dispatched to all resolvers in parallel using a thread pool.
4. Each resolver result is sent immediately to the client.
5. After all resolvers complete, a final completion message is sent.
6. All results are persisted in MongoDB for later analysis.

---

## WebSocket Protocol

Clients connect to the backend using WebSocket.

### Incoming message
```json
{
  "query_name": "example.com",
  "query_type": "A"
}

```

## Outgoing Message Types

The backend sends messages to connected clients over WebSocket in real time.

### `resolver_result`
Sent for **each DNS resolver** as soon as its response is received.

```json
{
  "type": "resolver_result",
  "data": {
    "name": "Google",
    "dns": "8.8.8.8",
    "country": "USA",
    "flag": "🇺🇸",
    "latency_ms": 24.3,
    "ttl": 300,
    "status": true,
    "result": "93.184.216.34"
  }
}

```

### Resolver Result Fields

Each `resolver_result` message contains the following fields:

- **`name`**  
  Human-readable DNS resolver name.

- **`dns`**  
  IP address of the DNS resolver used for the query.

- **`country`**  
  Country where the DNS resolver is located.

- **`flag`**  
  Country flag represented as a Unicode emoji.

- **`latency_ms`**  
  DNS query response time in milliseconds.

- **`ttl`**  
  Time-to-Live value returned in the DNS answer.

- **`status`**  
  Indicates whether the DNS query was successful.  
  Possible values: `true`, `false`.

- **`result`**  
  DNS response value (for successful queries) or error message (for failed queries).

---

## Rate Limiting Details

To prevent abuse and excessive load, the backend applies IP-based rate limiting.

Limits are enforced using request timestamps stored in MongoDB.

### Applied Limits

- **5 requests per minute**
- **40 requests per hour**
- **200 requests per day**

If a client exceeds any of these limits, the request is rejected and an appropriate message is sent via WebSocket.

---

## MongoDB Collections

The backend uses MongoDB to store:

### `resolvers`
Stores DNS resolver definitions.

Example document:
```json
{
  "name": "Google",
  "dns": "8.8.8.8",
  "country": "USA",
  "flag": "🇺🇸"
}
```


### `results`

Stores DNS query results for auditing and analysis purposes.

Each document represents a single DNS check request and contains aggregated resolver responses.

Stored data includes:

- **Client IP address**  
  IP address of the client initiating the DNS query.

- **Query name**  
  The domain or hostname that was queried.

- **Query type**  
  DNS record type (e.g. `A`, `AAAA`, `MX`, `TXT`, etc.).

- **Resolver responses**  
  List of resolver-specific results, including success or failure information.

- **Latency values**  
  DNS response time per resolver, measured in milliseconds.

- **TTL values**  
  Time-to-Live values returned by each resolver.

- **Timestamp**  
  UTC timestamp indicating when the query was executed.

Example document:
```json
{
  "client_ip": "203.0.113.10",
  "query_name": "example.com",
  "query_type": "A",
  "created_at": "2026-01-08T12:34:56Z",
  "results": [
    {
      "name": "Google",
      "dns": "8.8.8.8",
      "country": "USA",
      "flag": "🇺🇸",
      "status": true,
      "latency_ms": 42.7,
      "ttl": 1800,
      "result": "93.184.216.34"
    }
  ]
}
```


## Backend Configuration

The backend behavior is controlled through environment variables.

Required Environment Variables

- **MONGO_URI**
MongoDB connection string.

- **MONGO_DB_NAME**
Database name used by the application.

- **CLIENT_MINUTE_LIMIT**
Maximum requests allowed per IP per minute.

- **CLIENT_HOUR_LIMIT**
Maximum requests allowed per IP per hour.

- **CLIENT_DAY_LIMIT**
Maximum requests allowed per IP per day.


# Architecture Diagram

```
┌──────────────┐
│ Client       │
│ (WebSocket)  │
└──────┬───────┘
       │
       │ WebSocket request
       │ { query_name, query_type }
       │
┌──────▼─────────────────────┐
│ Tornado WebSocket Server    │
│ (socket.py)                │
└──────┬─────────────────────┘
       │
       │ Rate limit check
       │ (per client IP)
       │
┌──────▼─────────────────────┐
│ Rate Limiter Logic          │
│ (functions.py)             │
└──────┬─────────────────────┘
       │
       │ Load resolvers
       │
┌──────▼─────────────────────┐
│ MongoDB                    │
│ resolvers collection       │
└──────┬─────────────────────┘
       │
       │ Parallel DNS queries
       │
┌──────▼─────────────────────┐
│ ThreadPoolExecutor          │
│ (one task per resolver)    │
└──────┬─────────────────────┘
       │
       │ DNS query (dnspython)
       │
┌──────▼─────────────────────┐
│ DNS Resolvers               │
│ (Google, Cloudflare, etc.)  │
└──────┬─────────────────────┘
       │
       │ Resolver results
       │
┌──────▼─────────────────────┐
│ Result Aggregation          │
│ + Latency / TTL parsing    │
└──────┬─────────────────────┘
       │
       │ Stream results
       │ (resolver_result)
       │
┌──────▼─────────────────────┐
│ WebSocket Client            │
│ (real-time updates)        │
└──────┬─────────────────────┘
       │
       │ Persist results
       │
┌──────▼─────────────────────┐
│ MongoDB                    │
│ results collection         │
└────────────────────────────┘
```
