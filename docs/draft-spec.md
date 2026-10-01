
# Moochy.dev: Ultra-Lightweight Peer-to-Peer AI Compute Relay

## 1. Project Boundaries & Repository Structure

- **Closed-Source Monorepo (`moochy-core`):**
  - Contains Go backend API, in-memory WebSocket routing engine, HTMX dashboard templates, and SQLite database.
- **Open-Source Client Repository (`moochy-cli`):**
  - Apache-2.0 / MIT licensed Rust binary executable containing both `moochy-mcp` (maintainer IDE tool) and `moochy-daemon` (donor execution client).


```

┌────────────────────────────────────────────────────────────────────────┐
│            Moochy Closed-Source Monolith (Go + HTMX)                   │
│  - In-Memory Zero-Latency Routing Table (<1ms dispatch)                │
│  - Web App, Public Audit Ledger & SQLite (WAL Mode)                    │
└───────────────┬────────────────────────────────────────▲───────────────┘
│                                        │
Fast HMAC Signed WSS Payload              GPG/Ed25519 Signed Result
│                                        │
▼                                        │
┌───────────────────────────────┐        ┌───────────────────────────────┐
│ Maintainer IDE (Cursor)       │        │ Donor Daemon (Rust CLI)       │
│  moochy-mcp (Open Source)     │        │  moochy-daemon (Open Source)  │
└───────────────────────────────┘        └───────────────────────────────┘

```

---

## 2. Ultra-Fast Dispatch & Dynamic Routing Engine

To ensure IDE tasks feel instant to maintainers, client-side dispatching and relay routing targets **sub-millisecond overhead**.

### 2.1 High-Performance Client Dispatcher (`moochy-mcp` in Rust)
- **Zero Cold-Start / Persistent Connection:** `moochy-mcp` maintains a persistent multiplexed WebSocket connection to the Go relay upon IDE startup.
- **Async I/O via Tokio:** Prompts are serialized using zero-copy JSON parsing (`simd-json` / `serde_json`) and dispatched in **<2ms** from the maintainer's IDE to the network layer.

### 2.2 Capacity-Aware In-Memory Routing Table (Go Engine)
- **Lock-Free In-Memory Registry:** The Go relay holds an in-memory `sync.Map` / lock-free index of all currently connected online donor daemons, indexed by:
  1. Allowed LLM Models (`claude-3-7-sonnet`, `gpt-4o`, `deepseek-r1`).
  2. Max Effort Level capability (`low`, `medium`, `high`).
  3. Real-Time Token Balance ($LOCKED > 0$).
  4. Round-Trip Latency (RTT) and active concurrent task load.
- **Sub-Millisecond Matchmaking:** Matching an incoming task to an optimal donor daemon takes **<1ms** with zero database read latency during routing.

### 2.3 Instant Failover & Re-Routing Protocol
- **Fast ACK Deadline (500ms):** When a task is dispatched to a donor's daemon, the daemon must return a lightweight TCP/WS acknowledgment (`ACK`) within 500ms.
- **Auto-Redirect:** If a donor node drops, stalls, or fails to acknowledge within 500ms, the Go engine instantly redirects the task payload to the next highest-ranked available donor node in the pool without dropping the maintainer's IDE connection.

---

## 3. Security & Cryptographic Integrity Architecture

### 3.1 Asymmetric Cryptography & Output Integrity (GPG / Ed25519)
1. **Donor Key Pair Registration:** Donors generate or import an **Ed25519 keypair or GPG key** into `moochy-daemon`. The private key is encrypted locally via **AES-256-GCM** using a user passphrase.
2. **Execution & Non-Repudiation Signature:** The donor's daemon signs $H_{\text{prompt}} + H_{\text{output}} + \text{task\_id}$ using their local private key.
3. **Relay Verification:** The Go backend verifies the signature against the donor's registered public key before delivering the result to the maintainer.

### 3.2 Anti-Abuse & Anti-Mining Isolation (Zero Arbitrary Execution)
- **Text-Only JSON-RPC Schema:** The platform **never** accepts or dispatches shell scripts, binaries, or container images.
- **Sandboxed Daemon:** `moochy-daemon` acts exclusively as an HTTPS API bridge to official LLM provider endpoints. Attempting to pass code execution instructions inside prompts simply results in text generation, consuming zero GPU/CPU host compute beyond standard HTTPS calls.

---

## 4. Tech Stack & Architecture

- **Backend:** **Go Monolith** (`net/http`, `chi`, `crypto/ed25519`, `html/template`).
- **Frontend:** **HTMX** + **Server-Sent Events (SSE)** + **Tailwind CSS**.
- **Database:** **SQLite3** (`WAL` mode for high-concurrency writes, with in-memory routing tables).
- **Client Binaries (Open Source):** **Rust** (`rmcp` SDK + `tokio` + `ed25519-dalek`).
  - `moochy-cli mcp`: Maintainer IDE integration binary (<10MB).
  - `moochy-cli daemon`: Donor background runner with local passphrase unlocking.

---

## 5. Token Locking & Reclamation Protocol


```

[ Unallocated ] ──(Donate)──► [ LOCKED in Pool ] ──(Task Match)──► [ RESERVED ] ──(Done)──► [ SPENT ]
│
(Reclaim Clicked)
▼
[ RECLAIMED / FREE ]

```

1. **LOCKED:** Donor commits tokens. Balance is held in memory and SQLite, ready for allocation.
2. **RESERVED:** Upon task match, an estimated token ceiling is locked to prevent double-spending.
3. **SPENT:** Upon receipt and signature validation of the result, actual tokens move to `SPENT`. Leftovers return to `LOCKED`.
4. **RECLAIMED:** Donors can click "Reclaim" at any time. Unreserved locked tokens release immediately; active in-flight reserved tasks release upon completion or timeout.

---

## 6. Public Repository & Dashboard UI (HTMX + SSE)

### 6.1 Real-Time Node Presence Component
Donors and maintainers view live node presence and dynamic compute metrics on `moochy.dev/p/{owner}/{repo}`:

```html
<!-- Public Goal, Leaderboard & Audit Page -->
<div class="max-w-4xl mx-auto p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-8">

  <!-- Monthly Goal Progress Bar -->
  <div>
    <div class="flex justify-between mb-2">
      <h3 class="font-bold text-white">Monthly Compute Goal</h3>
      <span class="text-slate-400 font-mono">750,000 / 1,000,000 Tokens (75%)</span>
    </div>
    <div class="w-full bg-slate-800 h-4 rounded-full overflow-hidden">
      <div class="bg-emerald-500 h-full rounded-full transition-all duration-500" style="width: 75%"></div>
    </div>
  </div>

  <!-- Live Worker Node Pool (HTMX SSE) -->
  <div hx-ext="sse" sse-connect="/api/donor/presence-stream" sse-swap="PresenceUpdate">
    <h4 class="text-sm font-semibold uppercase text-slate-400 mb-4">Active Compute Pool</h4>
    <div class="p-3 bg-slate-950 rounded border border-slate-800 flex justify-between items-center">
      <div class="flex items-center gap-3">
        <span class="relative flex h-3 w-3">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
        </span>
        <div>
          <div class="font-mono text-sm text-white">node-alpha (claude-3-7-sonnet)</div>
          <div class="text-xs text-slate-400 font-mono">RTT: 12ms | GPG: Verified</div>
        </div>
      </div>
      <span class="px-2.5 py-1 rounded text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
        Ready
      </span>
    </div>
  </div>

  <!-- Public Verification Audit Ledger -->
  <div>
    <h4 class="text-sm font-semibold uppercase text-slate-400 mb-4">Public Execution Audit Log</h4>
    <div class="space-y-2 font-mono text-xs">
      <div class="p-3 bg-slate-950 rounded border border-slate-800 flex justify-between items-center">
        <div>
          <span class="text-emerald-400">[VERIFIED SIG]</span> Task #tk_8f912a - 14,200 Tokens
          <div class="text-slate-500 text-[10px]">Donor Sig: 3a9f...e102 | Hash: e3b0c442...</div>
        </div>
        <span class="text-slate-400">2 mins ago</span>
      </div>
    </div>
  </div>

</div>

```

---

## 7. SQLite Database Schema (`schema.sql`)

```sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    provider TEXT NOT NULL, -- 'github' or 'gitlab'
    provider_id TEXT NOT NULL,
    public_key TEXT NOT NULL, -- Ed25519/GPG Public Key
    avatar_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS repositories (
    id TEXT PRIMARY KEY,
    owner TEXT NOT NULL,
    name TEXT NOT NULL,
    user_id TEXT NOT NULL,
    mcp_secret TEXT UNIQUE NOT NULL,
    target_token_goal INTEGER DEFAULT 1000000,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    UNIQUE(owner, name)
);

CREATE TABLE IF NOT EXISTS token_pledges (
    id TEXT PRIMARY KEY,
    donor_id TEXT NOT NULL,
    repository_id TEXT NOT NULL,
    allowed_models TEXT NOT NULL, -- JSON array
    max_effort_level TEXT DEFAULT 'medium',
    amount_locked INTEGER NOT NULL DEFAULT 0,
    amount_reserved INTEGER NOT NULL DEFAULT 0,
    amount_spent INTEGER NOT NULL DEFAULT 0,
    amount_reclaimed INTEGER NOT NULL DEFAULT 0,
    status TEXT DEFAULT 'ACTIVE',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(donor_id) REFERENCES users(id),
    FOREIGN KEY(repository_id) REFERENCES repositories(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    pledge_id TEXT NOT NULL,
    prompt_hash TEXT NOT NULL,
    output_hash TEXT NOT NULL,
    signature TEXT NOT NULL,
    tokens_used INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(pledge_id) REFERENCES token_pledges(id)
);

```

---

## 8. Implementation Roadmap for AI Agent

* [ ] **Phase 1: Go Monolith Core & SQLite Setup**
* Initialize Go project with `chi` router and CGO-free `modernc.org/sqlite`.
* Implement GitHub & GitLab OAuth handlers.
* Setup Ed25519 / GPG signature verification module.


* [ ] **Phase 2: Ultra-Fast In-Memory Routing Engine**
* Build lock-free in-memory worker registry for sub-millisecond capacity matching.
* Implement 500ms ACK deadline with auto-redirect/failover logic.
* Record verified execution signatures to `audit_logs` table.


* [ ] **Phase 3: HTMX Dashboard & Public Pages**
* Build Donor Station with real-time SSE worker presence stream.
* Build public route `/p/{owner}/{repo}` with goal progress bar, live pool list, and audit ledger.


* [ ] **Phase 4: Open-Source Rust CLI (`crates/moochy-cli`)**
* Implement passphrase-encrypted local key store (`ed25519-dalek`).
* Build persistent, zero-copy `moochy-cli mcp` client for IDE integration.
* Build `moochy-cli daemon` runner command with output signing and stream response.



```
