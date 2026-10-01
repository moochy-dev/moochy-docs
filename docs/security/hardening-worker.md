# Hardening checklist — `cli/crates/worker` (`moochy-worker`)

Owner: `mo-worker`. The firewall, the recursive validator, provider adapters, usage parsers, tool-call inspection, local reservations. This crate is the last line between a relayed request and a donor's money and provider account. Attack ids → [attack-catalog.md](attack-catalog.md).

`#![forbid(unsafe_code)]`; same clippy denials as proto; checked integer money math (`checked_*`). No dependency on `moochy-proto`.

| # | Control | Attack | Proof |
|---|---|---|---|
| W1 | **Allowlist, never denylist, recursive.** Per-adapter tables of allowed endpoints, headers (+ values), top-level fields, content-block types (incl. nested in `tool_result`/documents), tool types. Anything unknown → `nack{firewall}` | A24, A25, A60–A62 | E09, U (fuzz) |
| W2 | Parse provider bodies with a decoder that **rejects duplicate keys**, invalid UTF-8, lone surrogates, numbers outside i64/f64, depth > 64; compare keys decoded and case-sensitive | A20, A22, A24 | U |
| W3 | Validate the **decoded** tree; after a safe mutation, **re-serialize from that tree** — never forward original bytes a second parser could read differently | A20, A24 | U |
| W4 | zstd decode into a buffer capped at 32 MiB + 1 (fail at the cap); `WithDecoderMaxWindow(8 MiB)`, never size allocation from `Frame_Content_Size`; single frame only | A21 | U |
| W5 | Recompute every route-header field from the decoded body; `est_input_tokens` must match **exactly** (catalog maxima per image/page); mismatch → `route_mismatch` non-retryable + strike | A23, A68 | V, U |
| W6 | Verify `task_sig`, key logged + unrevoked, owner-signed `MEMBER_ADDED`/owner, pledge↔repo, ULID freshness ±10 min, and `(gateway_device, task_id)` never served (persisted set over the window) **before** calling the provider | A73 | E16, U |
| W7 | Deny server tools, `mcp_servers`, `container`, skills, file ids, URL sources, `n>1`, predicted outputs, `service_tier`, `speed:fast`, `inference_geo`, OpenRouter `models[]`/`route`/`plugins`/variants — except where a pledge flag allows (`fast`, `images`, `documents`, `cache_1h`) | A25, A60–A64 | E09, U |
| W8 | Allowlist `anthropic-beta` and other provider header **values** per catalog version; unknown value → `firewall` | A26 | U |
| W9 | Local reservation against the device cap and per-pledge counters with the Relay's `reserve()` formula, at `max_tokens` and the cache-write price for `cache_ttl`, **before** `task.ack`; refuse when the Relay ignores caps | A63, A69 | E11, U |
| W10 | Tool-call inspection: hold each block to its end; reject names not in `tools[]`, inputs failing `input_schema`, forbidden block types (`server_tool_use`, `mcp_tool_use`), responses whose model ≠ requested; emit the progress checkpoint signature | A48 | E18 |
| W11 | Tripwire scan of tool-call inputs (pipe-to-shell, credential paths, persistence, encoded payloads, raw-IP) → replace with an error tool result | A48 | E18 |
| W12 | Provider HTTP client: fixed base URL per adapter (loopback override only under `MOOCHY_INSECURE_DEV=1` + loopback literal); **refuse redirects**; ignore `HTTP(S)_PROXY`/`NO_PROXY` env; timeouts on connect, headers and each read | A45 | A45, U |
| W13 | Usage parsers for both dialects bound every number; force `store:false` and stream-usage-on; `estimated` receipts settle pessimistically at the reservation | A65, A69 | U |
| W14 | API keys and `R` wrapped in `zeroize`; never logged; redaction unit-tested; opt-in telemetry reports field **names** only, never values | A84 | U |
| W15 | Firewall tables are data; allowlist-widening changes need two-person review; continuous fuzzing with real client corpora + mutations incl. deep nesting | A24 | M, U (fuzz) |
| W16 | Strict SSE parser: treat CRLF/CR/LF alike, bound line and field length, require the blank-line terminator, reject injected `event:`/`id:` reframing; fail closed (`stream` Invalid) and never forward an event that failed to parse | A145, A147 | U:worker, E18 |
