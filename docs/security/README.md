# Moochy security docs (`mo-sec`)

The red-team surface of the project. **Internal** (closed side of CONTRACT §0a): do not export to the public `moochy-cli` repository. The threat model assumes the closed relay is untrusted (adversary A3); every user-facing guarantee is enforced and verifiable in the open-source client (Apache-2.0).

- [attack-catalog.md](attack-catalog.md) — every attack (A01–A167) with its countermeasure, owner, verification and status. Start here. The **top-10 gaps** are in §15.
- `hardening-<component>.md` — per-owner, testable checklists:
  [proto](hardening-proto.md), [worker](hardening-worker.md), [node](hardening-node.md), [relay](hardening-relay.md), [web](hardening-web.md), [sandbox](hardening-sandbox.md).
- Black-box attack tests live in [`e2e/attacks/`](../../e2e/attacks/) as `TestA<NN>_*`, same harness conventions as `e2e/`. Last run (2026-10-01 r2, main binaries): 33 pass, 0 fail, 12 skip (A33 stateless MCP; A136–A139 key-log; A56b button route; A150–A155 sandbox — all pending upstream). Evil-peer tooling: `e2e/attacks/evil/`.

How to use: each owner reads their `hardening-*.md`, implements every row, and makes its "Proof" pass. `mo-sec` keeps the catalog current as attacks and fixes land — flip `status` to `implemented` only when the verification actually passes.
