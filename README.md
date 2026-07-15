# Asynchronous Infrastructure Monitoring & Auto-Recovery Engine

A high-performance, asynchronous microservice monitoring engine built with **FastAPI** and **HTTPX**. This project simulates real-time health checks across standard and critical services, handling network anomalies concurrently without choking the server or freezing user requests.

This was developed as a hands-on architectural playground to master **Asynchronous Data Pipelines, Singleton Connection Pooling, Fault Tolerance, Defensive Programming, and State Machines in Python.**

---

## 🛠️ Architecture & Core Engineering Concepts

Instead of standard, copy-pasted boilerplate APIs, this system implements production-grade backend logic designed around efficiency and memory safety:

### 1. Singleton Connection Pooling (`httpx.AsyncClient`)
To prevent connection starvation and memory leaks (`tebzir bl RAM`), a single, shared HTTPX client instance is initialized during application startup and gracefully torn down at shutdown. This ensures reusing under-the-hood TCP sockets safely.

### 2. High-Throughput Concurrency (`asyncio.gather`)
Checking millions of servers one-by-one sequentially causes catastrophic performance bottlenecks. The engine wraps tasks concurrently, blasting network requests at the exact same millisecond. The total runtime of a global sweep only takes as long as the slowest responding server.

### 3. Smart RAM Dependency Injection (Single Parameter Optimization)
Initially designed using split array metrics, the pipeline was heavily optimized to pass a single real-time parsed data dictionary directly through the RAM. This minimizes method invocation overhead, bypassing redundant network lookups or heavy data re-zipping.

### 4. Defensive Programming (`len(response.content)`)
Rather than blindly trusting remote server response headers (which can be absent, manipulated, or incorrect), the system reads the exact binary byte-length directly from the RAM buffer for bulletproof tracking.

### 5. Automation Over Human Intervention (Auto-Recovery State Machine)
If a critical system drops, the core flips into a `maintenance` shield, triggering automated disk backups while raising a structured `503 Service Unavailable` API exception. Manual human terminal intervention is avoided; an internal engine evaluates real-time sweeps to restore the status back to `healthy` automatically the moment infra recovers.

---

## 💡 Core Concepts I Mastered (From My Code Comments)

Every decision in this codebase was intentionally designed to solve specific architecture and system performance issues. Here is the engineering logic behind my inline comments:

* **Eliminating Complete Server Shutdowns (`8alat ta3mol shutdown kersa`)**
  I realized that hard-stopping a server during an infrastructure crash is a disaster (`kersa`) because it completely cuts off users and incurs extreme operational costs. Instead, my code transitions into a dynamic `maintenance` mode, allowing the app to stay alive while gracefully informing users.
  
* **Passing Parameters via RAM Over Re-fetching (`2estakbltha k parameter mn ram asra3`)**
  To achieve lightning-fast failure handling, I structured the pipeline to pass the fetched server result dictionary straight through the memory (RAM) into the handler. This avoids the massive performance penalty of making another function call or re-pinging the network.
  
* **Avoiding Manual Terminal Intervention (`b selb terminal flag`)**
  In traditional dead-server scenarios, an operator usually has to manually log into a terminal and throw flags to change state. My project completely replaces this bottleneck with an automated loop running perpetually (`lel 2abad`) that safely acts as an independent cron monitor.
  
* **Defensive Content Validation Over Headers (`2a2man mn response.headers.get`)**
  Network payloads can have missing or falsified headers. To make the code bulletproof, I bypassed `response.headers.get` and went straight to calculating the absolute binary size of the raw body payload via `len(response.content)`.
  
* **Understanding File Streaming Mechanics (`dump` vs `dumps`)**
  Through hands-on trial and error, I mastered data serialization differences. I mapped out when to write structured streams directly to disk using `json.dump` (for wiping/overwriting entire backups) versus converting objects to memory strings via `json.dumps` coupled with an append flag (`"a"`) to preserve cumulative multi-failure histories.

---

## 🚀 Key Features

- **Background Worker Loop:** Runs perpetually (`lel 2abad`) utilizing non-blocking `asyncio.sleep` blocks to preserve CPU cycles (0% idle overhead).
- **Fault-Tolerant Retries:** Filters out temporary network blips using structural `MAX_RETRIES` loops with exponential spacing.
- **Smart Append Logging:** Protects historical data dumps by shifting secondary server isolates into append-only modes (`"a"` with serialized `json.dumps`), eliminating data loss from accidental over-writes.

---

## 📡 API Endpoints

### 1. General System Shield (`GET /health`)
Acts as a lightning-fast gateway check. Reads raw state directly from RAM. If critical systems are compromised, it instantly triggers an HTTP `503` exception, shielding downstream clients.

### 2. Live Metrics Dashboard (`GET /servers`)
Bypasses the cron timing to force an on-demand real-time network sweep. Calculates and delivers aggregated metrics (`total_servers`, `online_servers_count`, `offline_servers_count`) alongside exact server speeds and attempt intervals.

---

## 📋 Technical Stack

- **Framework:** FastAPI
- **Asynchronous HTTP Client:** HTTPX
- **Asynchronous Task Manager:** Asyncio
- **Data Serialization:** JSON
- **Environment Integration:** Virtual Environment (`venv`) with localized dependency boundaries.
