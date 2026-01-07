# DNS Checker (Learning Project)

## Description
This is a simple DNS checker written in Python.

It sends the same DNS query to multiple DNS resolvers stored in a MongoDB database and collects their responses.

Results are delivered in real time using WebSocket.

This project is built for learning purposes.

---

## Why this project?
DNS results can change depending on:
- Resolver location
- DNS propagation
- Network latency

Using multiple DNS resolvers helps to better understand these differences.

---

## Features
- Query multiple DNS resolvers at the same time
- Measure DNS response latency
- Read TTL values from DNS answers
- Stream results in real time using WebSocket
- Store DNS check results in MongoDB
- IP-based rate limiting

---

## Technologies Used
- Python 3
- dnspython
- Tornado (WebSocket)
- MongoDB
- PyMongo
- ThreadPoolExecutor

---

## How it works
1. DNS resolvers are loaded from MongoDB.
2. The same DNS query is sent to all resolvers.
3. Each resolver response is processed in parallel.
4. Results are sent to the client one by one via WebSocket.
5. All results are saved to the database.

---

## WebSocket Usage
- Clients connect via WebSocket.
- DNS results are streamed in real time.
- Each resolver result is sent as a separate message.

Example message types:
- `resolver_result` – single DNS resolver result
- `done` – all resolvers completed

---

## Rate Limits
To prevent abuse, the following limits are applied per IP address:

- 5 requests per minute
- 40 requests per hour
- 200 requests per day

Requests exceeding these limits are rejected.

---

## Disclaimer
This project is created for learning and experimentation.

It is not intended for production use without additional security, validation, and scaling improvements.

---

## License
MIT
