# Moochy security docs (`mo-sec`)

The red-team surface of the project. Published in the public `moochy-docs` repository (CONTRACT §0a); the attack tests live in the private relay repository. The threat model assumes the closed relay is untrusted (adversary A3); every user-facing guarantee is enforced and verifiable in the open-source client (Apache-2.0).

- [attack-catalog.md](attack-catalog.md) — every attack (A01–A272, incl. the source audits §14b-§14k; §14k = §19 organisations); key-log attacks A136–A139/A164, A253 and the org attacks A254–A263 proven end-to-end with its countermeasure, owner, verification and status. Start here. The **top-10 gaps** are in §15.
- `hardening-<component>.md` — per-owner, testable checklists:
  [proto](hardening-proto.md), [worker](hardening-worker.md), [node](hardening-node.md), [relay](hardening-relay.md), [web](hardening-web.md), [sandbox](hardening-sandbox.md).
- Black-box attack tests live in `e2e/attacks/` (private relay repository) as `TestA<NN>_*`, same harness conventions as `e2e/`. Last run: see §15 of the catalog and `e2e/TRIAGE.md`. Evil-peer tooling: `e2e/attacks/evil/`.

How to use: each owner reads their `hardening-*.md`, implements every row, and makes its "Proof" pass. `mo-sec` keeps the catalog current as attacks and fixes land — flip `status` to `implemented` only when the verification actually passes.
