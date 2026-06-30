from __future__ import annotations

from peerpath.models import FirewallSummary


def parse_firewall_summary(text: str) -> FirewallSummary:
    backend = "unknown"
    forward_policy = "unknown"
    masquerade_enabled = False
    evidence: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower()
        evidence.append(line)
        if lowered.startswith("backend:"):
            backend = line.split(":", 1)[1].strip().lower()
        if "policy forward" in lowered:
            if "drop" in lowered:
                forward_policy = "drop"
            elif "accept" in lowered:
                forward_policy = "accept"
        if "masquerade" in lowered and "enabled" in lowered:
            masquerade_enabled = True

    return FirewallSummary(
        backend=backend,
        forward_policy=forward_policy,
        masquerade_enabled=masquerade_enabled,
        evidence=tuple(evidence),
    )
