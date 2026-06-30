# PeerPath v0.1 Read-Only Doctor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first useful PeerPath CLI: a safe, read-only, fixture-driven diagnostic report for Dockerized wg-easy host/container/peer reachability failures.

**Architecture:** PeerPath starts as a Python stdlib-first CLI with pure parsers over captured command output, a small normalized diagnostic model, deterministic rules for the first three failure classes, and Markdown/JSON report renderers. Real host collection stays read-only and conservative; fixture mode is the primary development and CI path until parser/rule behavior is stable.

**Tech Stack:** Python 3.11+, `argparse`, `dataclasses`, `ipaddress`, `json`, `pytest`, `ruff`, GitHub Actions.

**Execution unit:** Each Task below = one bead + one implementation branch/commit + tests + push + bead close. Checklist steps inside a Task are executed sequentially by that one worker.

**Canonical plan locations:**
- Local continuity copy: `~/.hermes/plans/2026-06-30-peerpath-v0.1-readonly-doctor.md`
- Repo execution copy: `.resources/plan/implementation-plan.md`

---

## Current repo state

The repo currently contains scaffold/docs only:

```text
README.md
SPEC.md
AGENTS.md
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
LICENSE
.github/workflows/ci.yml
.beads/
```

Existing product spec already defines:

- `peerpath doctor`, `peerpath fixture`, `peerpath explain`
- synthetic fixture mode
- parsers for Docker, WireGuard, routes, sysctls, firewall summaries
- first rule classes: missing host route, forwarding disabled/blocked, `AllowedIPs` mismatch
- read-only default and no firewall/router mutation in v0.1

---

## Hard constraints

1. **Read-only by default.** No command may mutate firewall, routing, Docker, or VPN state.
2. **Synthetic fixtures only in git.** Do not commit real VPN configs, private keys, hostnames, private IP inventories, local paths, or screenshots.
3. **No clever networking automation in v0.1.** Prefer parsers and deterministic fixture tests over live probes.
4. **No privileged execution.** No `sudo`, no `iptables -A`, no `nft add`, no `ip route add`, no Docker network changes.
5. **Explain before suggesting commands.** Reports must show evidence, likely cause, confidence, and risk-labeled next steps.
6. **TDD.** Tests first for every parser/rule/report behavior.
7. **Beads only.** Track all work with `bd`; no markdown TODO lists or alternate trackers.

---

## File structure to create

```text
pyproject.toml                         # package metadata, pytest/ruff config
src/peerpath/__init__.py               # version export
src/peerpath/__main__.py               # `python -m peerpath`
src/peerpath/cli.py                    # argparse commands: doctor, fixture, explain
src/peerpath/models.py                 # dataclasses/enums for inputs, findings, reports
src/peerpath/fixtures.py               # fixture loading + validation
src/peerpath/parsers/docker.py         # docker inspect / compose ps parsers
src/peerpath/parsers/wireguard.py      # wg dump/showconf parsers
src/peerpath/parsers/routes.py         # ip route parser
src/peerpath/parsers/sysctl.py         # forwarding sysctl parser
src/peerpath/parsers/firewall.py       # nft/iptables summary parser
src/peerpath/rules/reachability.py     # first failure-class rules
src/peerpath/report.py                 # Markdown/JSON renderers
src/peerpath/redaction.py              # key/path/hostname redaction helpers
tests/fixtures/host-missing-route/     # synthetic fixture
tests/fixtures/forwarding-disabled/    # synthetic fixture
tests/fixtures/allowedips-mismatch/    # synthetic fixture
tests/test_cli_smoke.py
tests/test_fixtures.py
tests/test_parsers_*.py
tests/test_rules_reachability.py
tests/test_report.py
tests/test_redaction.py
```

---

## Public fixture conventions

Use synthetic examples only. Recommended stable values:

```text
wg interface: wg0
wg-easy container: peerpath-wg-easy
Docker bridge CIDR: 172.28.0.0/16
WireGuard CIDR: 10.44.0.0/24
Peer service IP: 10.44.0.2
Host route missing example: no route for 10.44.0.0/24 via wg-easy bridge/container
Forwarding-disabled example: net.ipv4.ip_forward = 0
AllowedIPs mismatch example: peer allowed IPs only 10.44.0.2/32 when target route expects 10.44.0.0/24
Fake public docs/test hostnames: example.invalid, peerpath.local.invalid
```

Never store realistic private keys. If a WireGuard parser needs key-shaped data, use placeholders like:

```text
PRIVATE_KEY_REDACTED
PUBLIC_KEY_SYNTHETIC_PEER_A
PRESHARED_KEY_REDACTED
```

---

## Task 1 — Python package and CLI smoke baseline

**Bead:** `peerpath-v0.1-package-cli-baseline`

**Files:**
- Create: `pyproject.toml`
- Create: `src/peerpath/__init__.py`
- Create: `src/peerpath/__main__.py`
- Create: `src/peerpath/cli.py`
- Create: `tests/test_cli_smoke.py`
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Write failing CLI smoke tests**

Create `tests/test_cli_smoke.py`:

```python
from peerpath.cli import main


def test_help_exits_success(capsys):
    code = main(["--help"])
    captured = capsys.readouterr()
    assert code == 0
    assert "peerpath" in captured.out.lower()
    assert "doctor" in captured.out
    assert "fixture" in captured.out
    assert "explain" in captured.out


def test_doctor_requires_fixture_or_collect_flag(capsys):
    code = main(["doctor"])
    captured = capsys.readouterr()
    assert code == 2
    assert "--fixture" in captured.err
    assert "read-only" in captured.err.lower()
```

- [ ] **Step 2: Run the failing tests**

Run:

```bash
python -m pytest tests/test_cli_smoke.py -q
```

Expected before implementation: import failure because `peerpath` package does not exist.

- [ ] **Step 3: Add package metadata and minimal CLI**

Create `pyproject.toml` with:

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "peerpath"
version = "0.1.0-alpha.1"
description = "Read-only reachability doctor for Dockerized wg-easy setups"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "Apache-2.0" }
authors = [{ name = "Halaprix" }]

[project.scripts]
peerpath = "peerpath.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

Create `src/peerpath/__init__.py`:

```python
__version__ = "0.1.0-alpha.1"
```

Create `src/peerpath/__main__.py`:

```python
from .cli import main

raise SystemExit(main())
```

Create `src/peerpath/cli.py` with an `argparse` parser exposing `doctor`, `fixture`, and `explain`. `doctor` must reject calls without `--fixture` until live collection exists.

- [ ] **Step 4: Update CI to run tests and lint**

Extend `.github/workflows/ci.yml` after required-doc checks:

```yaml
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install test dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e . pytest ruff
      - name: Run tests
        run: python -m pytest -q
      - name: Run lint
        run: python -m ruff check .
```

- [ ] **Step 5: Verify**

Run:

```bash
python -m pip install -e . pytest ruff
python -m pytest tests/test_cli_smoke.py -q
python -m ruff check .
python -m peerpath --help
```

Expected: tests pass, lint passes, help lists all three commands.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src tests .github/workflows/ci.yml
git commit -m "feat: add peerpath cli baseline

Adds the Python package scaffold, argparse command surface, and CI test/lint checks.

Closes <bead-id>"
git push
```

---

## Task 2 — Synthetic fixture schema and loader

**Bead:** `peerpath-v0.1-fixture-schema`

**Depends on:** Task 1.

**Files:**
- Create: `src/peerpath/models.py`
- Create: `src/peerpath/fixtures.py`
- Create: `tests/fixtures/host-missing-route/*`
- Create: `tests/fixtures/forwarding-disabled/*`
- Create: `tests/fixtures/allowedips-mismatch/*`
- Create: `tests/test_fixtures.py`
- Modify: `src/peerpath/cli.py`

- [ ] **Step 1: Define fixture directory contract**

Each fixture directory must contain:

```text
manifest.json
collectors/docker-inspect.json
collectors/docker-compose-ps.json
collectors/wg-show-dump.txt
collectors/wg-showconf.conf
collectors/ip-route.txt
collectors/sysctl.txt
collectors/firewall.txt
expected.json
```

`manifest.json` shape:

```json
{
  "name": "host-missing-route",
  "description": "Host cannot reach peer CIDR because no host route exists",
  "target": {
    "peer_cidr": "10.44.0.0/24",
    "peer_ip": "10.44.0.2",
    "wg_interface": "wg0",
    "container_name": "peerpath-wg-easy"
  }
}
```

`expected.json` shape:

```json
{
  "top_finding_id": "host_missing_route_to_peer_cidr",
  "top_severity": "blocking"
}
```

- [ ] **Step 2: Write failing fixture tests**

Create `tests/test_fixtures.py` asserting:

```python
from pathlib import Path

from peerpath.fixtures import load_fixture


def test_load_host_missing_route_fixture():
    fixture = load_fixture(Path("tests/fixtures/host-missing-route"))
    assert fixture.manifest.name == "host-missing-route"
    assert fixture.manifest.target.peer_cidr == "10.44.0.0/24"
    assert "ip-route" in fixture.collectors
    assert fixture.expected.top_finding_id == "host_missing_route_to_peer_cidr"


def test_fixture_loader_rejects_missing_required_file(tmp_path):
    (tmp_path / "manifest.json").write_text('{"name":"broken","target":{}}')
    try:
        load_fixture(tmp_path)
    except ValueError as exc:
        assert "expected.json" in str(exc)
    else:
        raise AssertionError("missing expected.json should fail")
```

- [ ] **Step 3: Implement dataclasses and loader**

`models.py` defines `FixtureManifest`, `FixtureTarget`, `FixtureExpected`, and `LoadedFixture`. `fixtures.py` loads JSON/text files and validates required collector filenames.

- [ ] **Step 4: Add the three synthetic fixtures**

Populate all three fixture directories. Keep files small and readable. Use comments only in text files, never JSON.

- [ ] **Step 5: Wire `peerpath fixture list`**

`peerpath fixture list --fixtures-dir tests/fixtures` should print the three fixture names and descriptions.

- [ ] **Step 6: Verify**

Run:

```bash
python -m pytest tests/test_fixtures.py -q
python -m peerpath fixture list --fixtures-dir tests/fixtures
python -m ruff check .
```

Expected: all pass and fixture names are printed.

- [ ] **Step 7: Commit**

```bash
git add src/peerpath/models.py src/peerpath/fixtures.py src/peerpath/cli.py tests/fixtures tests/test_fixtures.py
git commit -m "test: add synthetic peerpath fixtures

Defines the fixture contract and adds three public-safe wg-easy reachability examples.

Closes <bead-id>"
git push
```

---

## Task 3 — Pure parsers for Docker, WireGuard, routes, sysctls, and firewall summaries

**Bead:** `peerpath-v0.1-parser-layer`

**Depends on:** Task 2.

**Files:**
- Create: `src/peerpath/parsers/__init__.py`
- Create: `src/peerpath/parsers/docker.py`
- Create: `src/peerpath/parsers/wireguard.py`
- Create: `src/peerpath/parsers/routes.py`
- Create: `src/peerpath/parsers/sysctl.py`
- Create: `src/peerpath/parsers/firewall.py`
- Create: `tests/test_parsers_docker.py`
- Create: `tests/test_parsers_wireguard.py`
- Create: `tests/test_parsers_routes.py`
- Create: `tests/test_parsers_sysctl_firewall.py`
- Modify: `src/peerpath/models.py`

- [ ] **Step 1: Write parser tests first**

Tests must cover only the synthetic fixture strings. Example route test:

```python
from peerpath.parsers.routes import parse_ip_routes


def test_parse_ip_routes_detects_missing_peer_cidr():
    routes = parse_ip_routes("default via 192.0.2.1 dev eth0\n172.28.0.0/16 dev br-peerpath\n")
    assert routes.has_route_for("10.44.0.0/24") is False
    assert routes.has_route_for("172.28.0.0/16") is True
```

Example sysctl test:

```python
from peerpath.parsers.sysctl import parse_forwarding_sysctls


def test_parse_forwarding_disabled():
    state = parse_forwarding_sysctls("net.ipv4.ip_forward = 0\nnet.ipv6.conf.all.forwarding = 0\n")
    assert state.ipv4_forwarding is False
    assert state.ipv6_forwarding is False
```

- [ ] **Step 2: Implement small parser return types**

Use dataclasses in `models.py`:

```python
@dataclass(frozen=True)
class RouteTable:
    routes: tuple[RouteEntry, ...]

    def has_route_for(self, cidr: str) -> bool:
        ...
```

Keep parsing permissive: unknown lines become ignored evidence, not crashes, unless the whole file is unreadable.

- [ ] **Step 3: Parse WireGuard allowed IPs**

Support `wg show all dump` first. Parse peer rows enough to identify public key and allowed IPs. `wg showconf` can be minimal in v0.1 and used as fallback evidence.

- [ ] **Step 4: Parse Docker inspect facts**

Extract container name, network mode, bridge network CIDRs/IPs, published UDP port, and Linux capabilities if present. Avoid deep Docker abstractions.

- [ ] **Step 5: Parse firewall summaries conservatively**

Detect backend hints (`nft`, `iptables`, `FORWARD DROP`, `MASQUERADE`, `WG_POST_UP`) as evidence strings. Do not claim exact firewall truth unless fixture text is explicit.

- [ ] **Step 6: Verify**

Run:

```bash
python -m pytest tests/test_parsers_*.py -q
python -m pytest -q
python -m ruff check .
```

Expected: parser tests and full suite pass.

- [ ] **Step 7: Commit**

```bash
git add src/peerpath/parsers src/peerpath/models.py tests/test_parsers_*.py
git commit -m "feat: parse peerpath diagnostic inputs

Adds pure parsers for Docker, WireGuard, routes, sysctls, and firewall summaries.

Closes <bead-id>"
git push
```

---

## Task 4 — Reachability model and first three diagnostic rules

**Bead:** `peerpath-v0.1-reachability-rules`

**Depends on:** Task 3.

**Files:**
- Create: `src/peerpath/rules/__init__.py`
- Create: `src/peerpath/rules/reachability.py`
- Create: `tests/test_rules_reachability.py`
- Modify: `src/peerpath/models.py`

- [ ] **Step 1: Write failing rule tests against fixtures**

Create tests asserting the top finding for each fixture:

```python
from pathlib import Path

from peerpath.fixtures import load_fixture
from peerpath.rules.reachability import analyze_fixture


def test_host_missing_route_is_top_finding():
    report = analyze_fixture(load_fixture(Path("tests/fixtures/host-missing-route")))
    assert report.findings[0].id == "host_missing_route_to_peer_cidr"
    assert report.findings[0].severity == "blocking"
    assert report.findings[0].confidence == "high"


def test_forwarding_disabled_is_top_finding():
    report = analyze_fixture(load_fixture(Path("tests/fixtures/forwarding-disabled")))
    assert report.findings[0].id == "forwarding_disabled"


def test_allowedips_mismatch_is_top_finding():
    report = analyze_fixture(load_fixture(Path("tests/fixtures/allowedips-mismatch")))
    assert report.findings[0].id == "peer_allowedips_mismatch"
```

- [ ] **Step 2: Define report/finding model**

`models.py` should include:

```python
Severity = Literal["info", "warning", "blocking", "unsafe"]
Confidence = Literal["low", "medium", "high"]

@dataclass(frozen=True)
class Finding:
    id: str
    title: str
    severity: Severity
    confidence: Confidence
    evidence: tuple[str, ...]
    explanation: str
    safe_next_check: str
    remediation_options: tuple[RemediationOption, ...]
```

- [ ] **Step 3: Implement deterministic rules**

Rules:

1. `host_missing_route_to_peer_cidr`: target peer CIDR not present in host route table.
2. `forwarding_disabled`: IPv4 forwarding is false when path requires host/container routing.
3. `peer_allowedips_mismatch`: intended target peer CIDR/IP is not covered by any parsed peer `AllowedIPs`.

Each rule must attach evidence from parser outputs and must avoid remediation that mutates state by default.

- [ ] **Step 4: Rank findings**

Sort by severity order `unsafe > blocking > warning > info`, then by confidence. In the three fixture tests, expected top finding must be stable.

- [ ] **Step 5: Verify**

Run:

```bash
python -m pytest tests/test_rules_reachability.py -q
python -m pytest -q
python -m ruff check .
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add src/peerpath/rules src/peerpath/models.py tests/test_rules_reachability.py
git commit -m "feat: diagnose first reachability failures

Adds deterministic rules for missing host routes, disabled forwarding, and AllowedIPs mismatches.

Closes <bead-id>"
git push
```

---

## Task 5 — Markdown/JSON reports and `peerpath doctor --fixture`

**Bead:** `peerpath-v0.1-report-cli`

**Depends on:** Task 4.

**Files:**
- Create: `src/peerpath/report.py`
- Create: `tests/test_report.py`
- Modify: `src/peerpath/cli.py`

- [ ] **Step 1: Write failing report tests**

Create tests for Markdown and JSON output:

```python
from pathlib import Path
import json

from peerpath.fixtures import load_fixture
from peerpath.report import render_json, render_markdown
from peerpath.rules.reachability import analyze_fixture


def test_markdown_report_contains_evidence_and_safe_next_check():
    report = analyze_fixture(load_fixture(Path("tests/fixtures/host-missing-route")))
    text = render_markdown(report)
    assert "# PeerPath Diagnostic Report" in text
    assert "host_missing_route_to_peer_cidr" in text
    assert "Evidence" in text
    assert "Safe next check" in text
    assert "Risk label" in text


def test_json_report_is_machine_readable():
    report = analyze_fixture(load_fixture(Path("tests/fixtures/host-missing-route")))
    data = json.loads(render_json(report))
    assert data["findings"][0]["id"] == "host_missing_route_to_peer_cidr"
```

- [ ] **Step 2: Implement report renderers**

Markdown report sections:

```markdown
# PeerPath Diagnostic Report

## Summary
## Path matrix
## Findings
### <severity>: <title>
- ID:
- Confidence:
- Evidence:
- Explanation:
- Safe next check:
- Remediation options:
## Safety note
```

JSON must use only primitives/lists/dicts so it is stable for future API use.

- [ ] **Step 3: Wire CLI**

Support:

```bash
python -m peerpath doctor --fixture tests/fixtures/host-missing-route --format markdown
python -m peerpath doctor --fixture tests/fixtures/host-missing-route --format json
```

Default format: Markdown.

- [ ] **Step 4: Add CLI integration tests**

Use `capsys` to call `main([...])` and assert output contains expected finding IDs.

- [ ] **Step 5: Verify**

Run:

```bash
python -m pytest tests/test_report.py tests/test_cli_smoke.py -q
python -m peerpath doctor --fixture tests/fixtures/host-missing-route --format markdown
python -m peerpath doctor --fixture tests/fixtures/allowedips-mismatch --format json | python -m json.tool >/tmp/peerpath-report.json
python -m pytest -q
python -m ruff check .
```

Expected: report commands succeed, JSON validates, tests/lint pass.

- [ ] **Step 6: Commit**

```bash
git add src/peerpath/report.py src/peerpath/cli.py tests/test_report.py tests/test_cli_smoke.py
git commit -m "feat: render peerpath diagnostic reports

Adds Markdown and JSON output for fixture-driven doctor runs.

Closes <bead-id>"
git push
```

---

## Task 6 — Redaction and safety guardrails

**Bead:** `peerpath-v0.1-redaction-safety`

**Depends on:** Task 5.

**Files:**
- Create: `src/peerpath/redaction.py`
- Create: `tests/test_redaction.py`
- Modify: `src/peerpath/report.py`
- Modify: `README.md`

- [ ] **Step 1: Write redaction tests**

Create `tests/test_redaction.py`:

```python
from peerpath.redaction import redact_text


def test_redacts_wireguard_private_key_material():
    text = "PrivateKey = abcdefghijklmnopqrstuvwxyz1234567890=\nPresharedKey = abcdef"
    redacted = redact_text(text)
    assert "abcdefghijklmnopqrstuvwxyz" not in redacted
    assert "PrivateKey = <redacted>" in redacted
    assert "PresharedKey = <redacted>" in redacted


def test_redacts_local_home_paths():
    redacted = redact_text("config at /home/alice/wg/config and /Users/bob/wg.conf")
    assert "/home/alice" not in redacted
    assert "/Users/bob" not in redacted
```

- [ ] **Step 2: Implement conservative redaction**

Redact:

- `PrivateKey = ...`
- `PresharedKey = ...`
- PEM private key blocks
- `/home/<user>/...`
- `/Users/<user>/...`
- obvious container IDs longer than 12 hex chars in public report mode

Do not blindly redact all RFC1918 CIDRs from local reports: private routes are core diagnostic evidence. Instead, document that committed fixtures must be synthetic and future `peerpath fixture capture` must ask before writing local network inventories.

- [ ] **Step 3: Apply redaction before report rendering**

Ensure evidence strings pass through redaction before Markdown/JSON output.

- [ ] **Step 4: Add README safety section**

Document:

```markdown
## Safety model

PeerPath v0.1 is read-only. It reports evidence and risk-labeled next checks; it does not mutate routes, firewall rules, Docker networks, or WireGuard state.
```

- [ ] **Step 5: Verify**

Run:

```bash
python -m pytest tests/test_redaction.py tests/test_report.py -q
python -m peerpath doctor --fixture tests/fixtures/host-missing-route --format markdown
python -m pytest -q
python -m ruff check .
```

Expected: no key material appears in generated reports; all tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/peerpath/redaction.py src/peerpath/report.py tests/test_redaction.py README.md
git commit -m "feat: add peerpath report redaction

Redacts key material and local paths before diagnostic reports are exported.

Closes <bead-id>"
git push
```

---

## Task 7 — Docs, changelog, and v0.1 alpha acceptance gate

**Bead:** `peerpath-v0.1-docs-acceptance`

**Depends on:** Task 6.

**Files:**
- Modify: `README.md`
- Modify: `SPEC.md`
- Modify: `CHANGELOG.md`
- Modify: `.github/workflows/ci.yml` if previous tasks missed CI details
- Create: `docs/examples/host-missing-route.md`

- [ ] **Step 1: Generate example report from fixture**

Run:

```bash
python -m peerpath doctor --fixture tests/fixtures/host-missing-route --format markdown > docs/examples/host-missing-route.md
```

Inspect the file before committing. It must contain only synthetic fixture values.

- [ ] **Step 2: Update README quickstart**

README must include:

```bash
python -m pip install -e .
python -m peerpath fixture list --fixtures-dir tests/fixtures
python -m peerpath doctor --fixture tests/fixtures/host-missing-route
```

Also include one short report excerpt and a clear statement that live collection is not enabled yet unless implemented by a future bead.

- [ ] **Step 3: Update SPEC status**

Mark `v0.1.0-alpha.1` as implemented if Tasks 1–6 are done. Keep live host/container collection in a future milestone.

- [ ] **Step 4: Update CHANGELOG**

Add an unreleased section:

```markdown
## [0.1.0-alpha.1] - YYYY-MM-DD

### Added
- Fixture-driven `peerpath doctor` CLI.
- Synthetic wg-easy reachability fixtures.
- Parsers for Docker, WireGuard, routes, sysctls, and firewall summaries.
- Deterministic findings for missing host routes, disabled forwarding, and AllowedIPs mismatch.
- Markdown/JSON diagnostic reports with redaction.
```

- [ ] **Step 5: Final verification**

Run:

```bash
python -m pytest -q
python -m ruff check .
python -m peerpath doctor --fixture tests/fixtures/host-missing-route --format markdown >/tmp/peerpath-host-missing-route.md
python -m peerpath doctor --fixture tests/fixtures/forwarding-disabled --format json | python -m json.tool >/tmp/peerpath-forwarding-disabled.json
bd ready --json >/tmp/peerpath-ready.json
git status --short
```

Expected: tests/lint pass, report commands succeed, JSON validates, working tree contains only intended docs/status changes before commit.

- [ ] **Step 6: Commit and push**

```bash
git add README.md SPEC.md CHANGELOG.md docs/examples/host-missing-route.md .github/workflows/ci.yml
git commit -m "docs: document peerpath alpha cli

Adds quickstart, example output, changelog notes, and final acceptance documentation.

Closes <bead-id>"
git push
```

---

## Future beads explicitly out of scope for v0.1 alpha

Create these only after alpha.1 is working:

- live read-only host collection (`docker inspect`, `ip route`, sysctl commands)
- optional `docker exec` collection from wg-easy container
- nftables vs iptables backend deep diagnosis
- reverse-proxy-container to peer path checks
- remediation planner that emits persistent Docker Compose/sysctl snippets
- support-thread template generator

---

## Self-review

### Spec coverage

- CLI surface: covered by Task 1 and Task 5.
- Fixture mode: covered by Task 2.
- Parsers: covered by Task 3.
- First failures: covered by Task 4.
- Markdown/JSON report: covered by Task 5.
- Redaction/safety: covered by Task 6.
- Docs/CI: covered by Task 1 and Task 7.

### Placeholder scan

No `TBD`, `TODO`, `implement later`, or unspecified test steps are present. Future work is explicitly out of scope and separated from v0.1.

### Type consistency

The plan consistently uses `LoadedFixture`, `Finding`, `RemediationOption`, `DiagnosticReport`, parser dataclasses, and `analyze_fixture()` as the implementation vocabulary.

---

## Recommended execution order

1. Task 1: package + CLI baseline.
2. Task 2: fixture schema + three public-safe fixtures.
3. Task 3: parser layer.
4. Task 4: reachability rules.
5. Task 5: report/CLI integration.
6. Task 6: redaction and safety guardrails.
7. Task 7: docs/changelog/final acceptance.

Do not dispatch Task 3 before Task 2; parser tests should use the committed fixture strings. Do not dispatch Task 5 before Task 4; reports need stable finding IDs.
