# Contributing

PeerPath is early-stage. Keep changes small, testable, and safe.

## Development principles

- Read-only by default.
- Synthetic fixtures first.
- No private VPN keys, hostnames, IP inventories, or local paths in examples.
- Explain networking findings in plain language before suggesting commands.

## Commit style

Use Conventional Commits:

```text
feat: add fixture parser
fix: redact private key material
chore: update ci workflow
```

## Pull requests

Include:

- what changed,
- what was tested,
- any safety/privacy impact,
- sample output if user-facing report text changed.
