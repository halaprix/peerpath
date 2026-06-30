# Agent Instructions — PeerPath

PeerPath is a public software/app bet from the 100 Days, 100 Apps lab.

## Mission

Build a safe, read-only diagnostic CLI for Dockerized WireGuard/wg-easy reachability problems.

## Implementation plan

**Read first:** `.resources/plan/implementation-plan.md`

Execute the plan task-by-task in Beads order. Each plan Task maps to one bead, one implementation commit, one push, and one bead close.

## Hard constraints

- Public-safe only: do not commit secrets, private keys, VPN configs, private hostnames, private IP inventories, screenshots with personal data, or local machine paths.
- Do not add commands that mutate firewall, routing, Docker, or VPN state without an explicit design review.
- Fixture files must be synthetic or heavily redacted.
- Prefer simple Python modules and deterministic parser tests over clever networking automation.
- Conventional Commits only.
- Use Beads (`bd`) for task tracking; do not use markdown task lists as a tracker.
- TDD: write failing tests before implementation for every parser, rule, report, or CLI behavior.

## Key gotchas

- v0.1 alpha is fixture-first. Live host/container collection is future work unless a later bead explicitly scopes it.
- Private RFC1918 routes may be valid local diagnostic evidence, but committed fixtures must be synthetic and public-safe.
- No `sudo`, `iptables -A`, `nft add`, `ip route add`, Docker network mutation, or WireGuard state mutation in v0.1.
- Reports must explain evidence and risk before suggesting any command.

## Quality bar

Before claiming work is complete, run the validation commands from the current bead/plan task and include real output in the handoff.

## Halt condition

After finishing the v0.1 alpha acceptance bead, halt for human review before adding live collection, container exec, remediation snippets, or support-thread automation.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:7510c1e2 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->
