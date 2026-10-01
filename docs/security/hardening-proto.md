# Hardening checklist — `cli/crates/proto` (`moochy-proto`)

Owner: `mo-proto`. Covers wire types, `lp`, labels, crypto, frames, receipts, vectors. Every item is testable; the "Proof" column is a golden vector in `spec/vectors/` (`V`) or a crate unit test (`U`). Attack ids map to [attack-catalog.md](attack-catalog.md).

`#![forbid(unsafe_code)]`. `clippy::pedantic`, deny `unwrap_used`, `expect_used`, `panic`, `indexing_slicing`, `arithmetic_side_effects` outside tests. No OpenSSL, no home-made crypto.

| # | Control | Attack | Proof |
|---|---|---|---|
| P1 | `lp()` encodes each field as `u32_be(len) \|\| bytes`, integers as `u64_be`; reject any field whose length would overflow the 4-byte prefix | A09 | V `lp` |
| P2 | Every label is a distinct constant (CONTRACT §2); verifiers prepend the label, never read it from input | A09 | V labels |
| P3 | Fresh 32-byte `CK` per sealed body from the OS CSPRNG; `CK` only ever an HKDF input, never an AEAD key directly | A01 | U |
| P4 | `K_req`/`RK` exactly per CONTRACT §3; `RK` uses the per-attempt `R` as HKDF salt; include a vector proving two attempts of one task give different `RK` | A01 | V envelope |
| P5 | AEAD nonce = `0x00*8 \|\| u32_be(seq)`; refuse to seal/open when `seq` would exceed the per-stream chunk bound (request ≤ 513, response bounded); never wrap the counter | A02 | U |
| P6 | AAD binds label, kind, `task_id`, `attempt`, `R`, `seq`, last-flag for every chunk; opening checks contiguous `seq` from 0 and requires a last-flag before returning success | A03 | V, U |
| P7 | HPKE RFC 9180 base mode, suite `moochy.v1.hpke.x25519-sha256-chacha20poly1305`; `suite_id` in `info`; route-header bytes as AAD; unknown suite/version → error | A05, A74 | V |
| P8 | After opening: zstd-decompress with a hard 32 MiB output cap and an 8 MiB window cap, then verify `body_sha256` before returning the tree | A04, A21 | U |
| P9 | Ed25519 **verification = ZIP-215** (`ed25519-zebra`); signing = RFC 8032; ship the ZIP-215 edge-case vectors (non-canonical R/S, small-order points, `S ≥ L`) | A06 | V |
| P10 | Treat signatures as opaque bytes; never derive an id, dedupe key or idempotency token from signature bytes (document this in the receipt type) | A07 | U |
| P11 | `Chunk` fields are bounded on decode: reject `attempt` ∉ 0–3, `ct` whose plaintext would exceed 65,497 before allocation, `seq` beyond the per-stream bound (P5). (The old 23-byte binary frame header is superseded by the gRPC `Chunk` message, CONTRACT §12.) | A02, A13 | V, U |
| P12 | JSON helpers used by other crates parse into typed structs with `deny_unknown_fields` where the contract says so, and use a duplicate-key-rejecting decoder for security/money inputs (CONTRACT §1) | A20, A22 | U |
| P13 | Every secret (`CK`, keys, `R` where sensitive) wrapped in `zeroize`; token/MAC comparisons via `subtle` | A36, A84 | U |
| P14 | Receipts/projections/checkpoints/disputes are the exact signed byte strings; never re-serialize a signed artifact | A06, A07 | V |
| P15 | All external lengths bounded before allocation; parsers are fuzzed (`cargo fuzz`) on frame headers, `lp`, and the inner-payload decoder | A14, A21, A24 | U (fuzz) |

## Protobuf / gRPC (CONTRACT §12)

| # | Control | Attack | Proof |
|---|---|---|---|
| P16 | The route header, receipts, projections and catalog are the exact signed JSON bytes carried in protobuf `bytes`; `moochy-proto` never lets a security/money decision depend on a decoded protobuf scalar (proto3 merges repeated singular fields; unknown fields are dropped) | A90 | V, U |
| P17 | `Chunk{attempt, seq, last, ct}` carries ciphertext; the AEAD AAD (P6) is unchanged by the transport move; the gRPC stream identifies the task | A01, A03 | V |
