import json
from pathlib import Path

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
    assert "Safety note" in text


def test_json_report_is_machine_readable():
    report = analyze_fixture(load_fixture(Path("tests/fixtures/host-missing-route")))
    data = json.loads(render_json(report))
    assert data["findings"][0]["id"] == "host_missing_route_to_peer_cidr"
    assert data["findings"][0]["remediation_options"][0]["risk_label"] == "inspect-only"
