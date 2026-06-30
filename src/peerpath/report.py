from __future__ import annotations

import json
from dataclasses import asdict

from peerpath.models import DiagnosticReport, Finding
from peerpath.redaction import redact_text


def _finding_to_dict(finding: Finding) -> dict:
    return {
        "id": finding.id,
        "title": finding.title,
        "severity": finding.severity,
        "confidence": finding.confidence,
        "evidence": [redact_text(item) for item in finding.evidence],
        "explanation": redact_text(finding.explanation),
        "safe_next_check": redact_text(finding.safe_next_check),
        "remediation_options": [
            {
                "title": redact_text(option.title),
                "detail": redact_text(option.detail),
                "risk_label": option.risk_label,
            }
            for option in finding.remediation_options
        ],
    }


def render_json(report: DiagnosticReport) -> str:
    data = {
        "fixture_name": report.fixture_name,
        "path_matrix": [asdict(path_check) for path_check in report.path_matrix],
        "findings": [_finding_to_dict(finding) for finding in report.findings],
    }
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def render_markdown(report: DiagnosticReport) -> str:
    lines = [
        "# PeerPath Diagnostic Report",
        "",
        "## Summary",
        "",
        f"Fixture: `{report.fixture_name}`",
        f"Findings: {len(report.findings)}",
        "",
        "## Path matrix",
        "",
    ]

    if report.path_matrix:
        for check in report.path_matrix:
            lines.extend(
                [
                    f"- **{check.name}:** {check.observed_state}",
                    f"  - Likely causes: {', '.join(check.likely_causes) or 'none'}",
                ]
            )
    else:
        lines.append("No path checks were generated for this fixture.")

    lines.extend(["", "## Findings", ""])
    if not report.findings:
        lines.append("No findings.")
    for finding in report.findings:
        finding_data = _finding_to_dict(finding)
        lines.extend(
            [
                f"### {finding_data['severity']}: {finding_data['title']}",
                "",
                f"- ID: `{finding_data['id']}`",
                f"- Confidence: {finding_data['confidence']}",
                "- Evidence:",
            ]
        )
        lines.extend(f"  - {item}" for item in finding_data["evidence"])
        lines.extend(
            [
                f"- Explanation: {finding_data['explanation']}",
                f"- Safe next check: {finding_data['safe_next_check']}",
                "- Remediation options:",
            ]
        )
        for option in finding_data["remediation_options"]:
            lines.extend(
                [
                    f"  - {option['title']}",
                    f"    - Risk label: {option['risk_label']}",
                    f"    - Detail: {option['detail']}",
                ]
            )
        lines.append("")

    lines.extend(
        [
            "## Safety note",
            "",
            "PeerPath v0.1 reports evidence and read-only next checks. It does not mutate "
            "routes, firewall rules, Docker networks, or WireGuard state.",
            "",
        ]
    )
    return "\n".join(lines)
