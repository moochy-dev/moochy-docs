# Hardening checklist — `cli/crates/node` (`moochy`)

Owner: `mo-node`. CLI, config, keystore, relay link, the Gateway API door and MCP door (stdio + Streamable HTTP), local tokens, Host checks, scrubber, tool-call release. This binary runs on the **maintainer's machine**, so its blast radius is local RCE. Attack ids → [attack-catalog.md](attack-catalog.md).

`#![forbid(unsafe_code)]`; clippy as proto. Every external input hostile; timeouts on every network op.

## Local doors (Gateway + MCP)

| # | Control | Attack | Proof |
|---|---|---|---|
| N1 | Bind `127.0.0.1`/`::1` only, never `0.0.0.0` | A30 | E14 |
| N2 | `Host` must equal the bound loopback authority exactly (`127.0.0.1:P`, `[::1]:P`, `localhost:P`); reject absolute-form targets naming another authority; else 403 | A30 | A30, E14 |
| N3 | `/mcp`: in addition to N2 and the bearer token, reject any present `Origin` that is not `http://127.0.0.1:P`/`http://localhost:P` (MCP transports spec) | A32 | A32 |
| N4 | **No CORS, ever.** Never emit `Access-Control-Allow-*`; OPTIONS → 405 | A31 | A31, E14 |
| N5 | MCP session ids 128-bit random, bound to `SHA-256(token)`; mismatch → 404; a session id is never authentication by itself | A33 | A33 |
| N6 | HTTP server timeouts (header read 10 s, body read, idle), max open connections, `Content-Length`/stream cap at 32 MiB; strict HTTP/1.1 framing (hyper) | A34, A35, A17 | A34, A35 |
| N7 | Local token lookup by `SHA-256(token)` then `subtle::ConstantTimeEq` on the full value; wrong/missing → 401; no early return | A36 | A36 |
| N8 | Port held by launchd/systemd socket; `moochy doctor` checks the listener uid | A37 | M |
| N9 | `connect --write` writes only user-scoped files; refuse any git-tracked path; tokens repo-scoped and rotatable | A38 | U |

## MCP `files`

| # | Control | Attack | Proof |
|---|---|---|---|
| N10 | Root = git top-level recorded at `connect` ∩ client MCP roots (fallback: shim CWD / recorded root). Reject absolute paths, `..` components, NUL, URL schemes before resolution | A40 | A40, E14 |
| N11 | **No realpath-then-open.** Open from the root dirfd with `openat2(RESOLVE_BENEATH \| RESOLVE_NO_SYMLINKS \| RESOLVE_NO_MAGICLINKS)` on Linux; component-wise `O_NOFOLLOW` walk (or `cap-std`) elsewhere. This closes the realpath→open TOCTOU | A41 | A40 (symlink cases), U |
| N12 | Deny `.git/**`, secret-shaped (`.env*`, `.npmrc`, `.netrc`, `*.pem`, `id_*`, `*.kdbx`) and git-ignored files (`git check-ignore`), even when tracked | A42 | A40 |
| N13 | `fstat` the opened fd: regular files only (reject FIFO/device/socket), `st_nlink == 1` (no hard links), read within the remaining 2 MiB total budget | A43, A44 | U |
| N14 | Secret scrubber on file content and request bodies before sealing (redact mode default) | A85 | U |

## Output handling

| # | Control | Attack | Proof |
|---|---|---|---|
| N15 | `moochy_delegate` results wrapped as "untrusted content from donor X"; a single `sanitize_for_terminal()` strips C0 (keep `\n\t`), DEL, C1 (U+0080–009F) and bidi overrides/isolates (U+202A–202E, U+2066–2069) from delegate text | A46, A49 | A46 |
| N16 | Same sanitizer on **every** CLI print of a remote value (relay `error.message`, pseudonyms, `sealed_detail` capped 512 B, `moochy status`) | A47 | U |
| N17 | Model ids offered to clients come only from the signed catalog (regex `^[a-z0-9][a-z0-9._:/-]{0,63}$`); never free text from `pool.sync`; pseudonyms from a fixed alphabet | A39 | U |
| N18 | API door writes the provider's original bytes unchanged; tool-call blocks released only after verifying the Worker progress checkpoint, else an error tool result | A48 | E17, E18 |

## Keys, link, updates

| # | Control | Attack | Proof |
|---|---|---|---|
| N19 | Headless keystore: scrypt N≥2¹⁷,r=8,p=1 (or argon2id m=64 MiB); file mode 0600; refuse to start if group/world-readable | A86 | U |
| N20 | Device keys never exported; provider keys via prompt/stdin only, never argv; `secrecy`+`zeroize`; redaction unit-tested | A84 | U |
| N21 | Relay link: verify TLS to the dialed origin; auth signs `lp(auth, nonce, dialed_origin, tls_exporter, device_id)` with `dialed_origin` from the Node's own dial, never from `hello` | A08 | V |
| N22 | Gateway seals only to worker keys the key-log mirror shows logged, unrevoked and owner-`DONOR_APPROVED` for the repo | A72 | U |
| N23 | No silent auto-update; `moochy update` verifies the signature before replacing the binary | A83 | U |
| N24 | Clients that lose their connection mid-stream: abort cleanly; a second started attempt's frames → abort the task (A01 defense) | A01 | E17 |

## Node links (gRPC, CONTRACT §12)

| # | Control | Attack | Proof |
|---|---|---|---|
| N25 | Relay link (`tonic` + our rustls connector): TLS 1.3 + ALPN `h2`; capture `export_keying_material` for the `Auth` sig; one `Channel` per TLS connection, re-authenticated on any transport error | A95 | V |
| N26 | Client message-size caps (128 KiB), `http2_max_header_list_size`, connect/request timeouts, bounded per-stream buffers, no gRPC compression | A91 | U |
| N27 | `LocalControl` only on `<home>/state/node.sock`: path-based 0600 socket in a 0700 dir, never abstract-namespace; **check the peer uid** on every connection | A101, A103 | A101 |
| N28 | Create/rebind safely in a 0700 dir: bind to a temp name + atomic `rename`, `fchmod`, refuse if the final path is a symlink or non-socket (symlink/TOCTOU) | A102 | A101 |
| N29 | Security decisions read the signed JSON `bytes`, never a protobuf scalar; the route header is re-parsed with the strict decoder | A90 | U |
| N30 | Handles, repo and display names printed by the CLI go through `sanitize_for_terminal()` (N16) and handle validation mirrors the relay's vectors | A110, A112 | U |

## Source boundary (CONTRACT §0a)

| # | Control | Attack | Proof |
|---|---|---|---|
| N31 | The client is the whole trust base: every guarantee (sealing, signatures, caps, firewall, tool-call gating) is enforced here against a **malicious** relay, never delegated to it | A130 | E11, E15–E17 |
| N32 | No dependency on closed code: crates.io deps + `spec/**` only; no path/git deps outside `cli/` and `spec/` | A131 | M (CI) |
| N33 | Implement only `spec/protocol.md` + `spec/vectors`; ignore unknown relay messages, refuse unknown suites/versions | A133 | V |
| N34 | Release builds default to the official relay; a non-default `--relay` requires `MOOCHY_INSECURE_DEV=1`, prints a persistent warning, and uses a separate keystore + key-log mirror per relay origin | A135 | U |
