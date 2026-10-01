# Hardening checklist — `cli/crates/sandbox` (`moochy-sandbox`)

Owner: `mo-sandbox`. Confines `moochy run -- <cmd>` (maintainer side) and the donor-side parser child (CONTRACT §15). `unsafe` only in the small documented syscall module, reviewed and fuzzed. Attack ids → [attack-catalog.md](attack-catalog.md). Linux is the strong target; macOS (Seatbelt) is best-effort and its ceiling (no TCC/SIP override) is documented.

| # | Control | Attack | Proof |
|---|---|---|---|
| SB1 | Filesystem: RW only the worktree + a private scratch (`$TMPDIR`/`$HOME` in tmpfs); read-only system paths; deny `~/.ssh`, `~/.aws`, `~/.config`, keychains, browser profiles, other repos, the Moochy keystore/state, the real home. Landlock + mount ns + `pivot_root` | A150 | A150 (E93+) |
| SB2 | Network: empty net namespace; only the gateway via a Unix-socket bridge; `--allow-host` CONNECT proxy off by default; no DNS to the host resolver | A151 | A151 |
| SB3 | seccomp-bpf denylist: `ptrace`, `mount` (after setup), `bpf`, `keyctl`, `perf_event_open`, `userfaultfd`, `kexec*`, module loading, ns re-entry — **and `io_uring_setup`/`io_uring_enter`/`io_uring_register`** (ring ops bypass a name-based filter) | A152, A156 | A152, U:sandbox |
| SB4 | Deny terminal input injection: block `TIOCSTI`/`TIOCLINUX` ioctls and run the child in its own session (`setsid`), so it cannot push chars to the parent tty | A152 | U:sandbox |
| SB5 | `no_new_privs`; user+PID+mount+net+IPC+UTS namespaces; the sandbox and all descendants die with `moochy run` | A152, A154 | A152, A155 |
| SB6 | Clean environment: only an allowlist + gateway base-URL vars; never pass `MOOCHY_PASSPHRASE` or provider keys; `O_CLOEXEC` on every sandbox-held fd so none leaks across exec | A153, A154 | A153 |
| SB7 | rlimits (CPU, AS, NOFILE, NPROC) + wall-clock kill + cgroup v2 when a delegated cgroup is available (fork bomb, memory hog) | A154 | A154 |
| SB8 | Never silently unsandboxed: fail closed with the reason if setup fails; `--unsafe-no-sandbox` only for debugging with a loud warning; `moochy doctor` detects restricted unprivileged userns (Ubuntu AppArmor) and prints the fix | A155 | A155 |
| SB9 | No host bus/socket reachable: abstract-namespace Unix sockets are contained by the net namespace; never bind-mount `docker.sock`, the D-Bus socket, `$SSH_AUTH_SOCK` or X11 into the sandbox | A157 | A157 |
| SB10 | Donor-side parser child (§15.2): envelope-open, zstd, strict JSON, firewall and SSE parsing run with no filesystem, no keystore, seccomp allowlist; the broker keeps keys and does the HTTPS call with the re-serialized body | A145, T2 | U:sandbox, E-donor |
| SB11 | macOS: `sandbox-exec` deny-by-default profile (reads of system paths + worktree, writes only worktree/scratch, net only the gateway loopback); document that it cannot override TCC (Keychain, Apple Events, Pasteboard are TCC-governed) and is weaker than Linux | A150–A153 | A150 (darwin) |
