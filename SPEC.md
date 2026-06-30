# SPEC — PeerPath

## User story

As a homelab operator running wg-easy in Docker, I want a safe diagnostic report that explains host/container/peer reachability, so that I can fix routing and firewall problems without pasting random privileged commands.

## Core flow

1. User runs `peerpath doctor` on the host, optionally with `--container wg-easy`.
2. PeerPath collects read-only facts from Docker, WireGuard, routing, sysctls, and firewall summaries.
3. PeerPath builds a path matrix: host → container, container → peer, host → peer, and optional reverse-proxy container → peer.
4. PeerPath maps failures to likely causes and confidence levels.
5. PeerPath prints a Markdown report with safe next checks and clearly labeled remediation snippets.

## Feature list

### v0.1.0-alpha.1

- Python CLI skeleton: `peerpath doctor`, `peerpath fixture`, `peerpath explain`.
- Fixture loader for CI and demos.
- Parsers for:
  - `docker inspect` JSON,
  - `docker compose ps --format json`,
  - `wg show all dump`,
  - `wg showconf`,
  - `ip route show table all`,
  - forwarding sysctl output,
  - redacted nftables/iptables summaries.
- Rule engine for the first three failures:
  - host missing route to peer CIDR,
  - forwarding disabled or blocked,
  - peer `AllowedIPs` mismatch.

### v0.1.0-alpha.2

- Connectivity probe planner with dry-run output.
- Markdown and JSON report exporters.
- Redaction pass for hostnames, usernames, private comments, and key material.
- Example broken and fixed fixtures.

### v0.2.0-alpha.1

- Optional container exec collection for `wg show` when host lacks WireGuard tools.
- nftables/iptables backend detection.
- Docker network mode and published-port diagnosis.
- Report diagram for path state.

## Data model

```text
Report
- generated_at
- environment_summary
- collectors[]
- path_matrix[]
- findings[]
- recommendations[]
- redactions[]

PathCheck
- name
- from_node
- to_node
- target_cidr_or_ip
- observed_state
- likely_causes[]
- confidence

Finding
- id
- severity: info | warning | blocking | unsafe
- evidence[]
- explanation
- safe_next_check
- remediation_options[]
```

## Technical approach

- Python 3 CLI using `argparse` initially; upgrade to Typer only if needed.
- Collectors are pure functions over command output so fixture tests are cheap.
- Default mode is read-only. Any command with side effects requires an explicit future flag and is out of scope for the scaffold.
- Redaction happens before export and before fixture generation.
- CI runs parser tests against checked-in fixtures; no WireGuard or Docker daemon required.

## Validation plan

- Build three synthetic fixtures:
  1. host route missing,
  2. forwarding disabled,
  3. peer `AllowedIPs` mismatch.
- For each fixture, assert the top finding and recommendation are stable.
- Manually compare output against public wg-easy support issues and the r/selfhosted post class.
- Validate wedge by replying manually later in relevant support threads with only the report template and asking whether it would have shortened debugging.

## Milestones

- v0.1.0-alpha.0 — repo scaffold/spec.
- v0.1.0-alpha.1 — CLI skeleton plus fixture parser tests.
- v0.1.0-alpha.2 — first useful Markdown report.
- v0.2.0-alpha.1 — real host/container collection path.
