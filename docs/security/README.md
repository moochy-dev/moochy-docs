# Moochy security docs (`mo-sec`)

The red-team surface of the project.

- [attack-catalog.md](attack-catalog.md) — every attack (A01–A89) with its countermeasure, owner, verification and status. Start here. The **top-10 gaps** are in §10.
- `hardening-<component>.md` — per-owner, testable checklists:
  [proto](hardening-proto.md), [worker](hardening-worker.md), [node](hardening-node.md), [relay](hardening-relay.md), [web](hardening-web.md).
- Black-box attack tests live in [`e2e/attacks/`](../../e2e/attacks/) as `TestA<NN>_*`, same harness conventions as `e2e/`. They skip with `pending:` until the relay/moochy binaries exist (`RELAY_BIN`, `MOOCHY_BIN`).

How to use: each owner reads their `hardening-*.md`, implements every row, and makes its "Proof" pass. `mo-sec` keeps the catalog current as attacks and fixes land — flip `status` to `implemented` only when the verification actually passes.
