from pathlib import Path

from peerpath.fixtures import load_fixture
from peerpath.rules.reachability import analyze_fixture


def test_host_missing_route_is_top_finding():
    report = analyze_fixture(load_fixture(Path("tests/fixtures/host-missing-route")))
    assert report.findings[0].id == "host_missing_route_to_peer_cidr"
    assert report.findings[0].severity == "blocking"
    assert report.findings[0].confidence == "high"
    assert report.findings[0].evidence
    assert report.findings[0].safe_next_check
    assert report.findings[0].remediation_options[0].risk_label == "inspect-only"


def test_forwarding_disabled_is_top_finding():
    report = analyze_fixture(load_fixture(Path("tests/fixtures/forwarding-disabled")))
    assert report.findings[0].id == "forwarding_disabled"
    assert report.findings[0].severity == "blocking"
    assert report.findings[0].confidence == "high"


def test_allowedips_mismatch_is_top_finding():
    report = analyze_fixture(load_fixture(Path("tests/fixtures/allowedips-mismatch")))
    assert report.findings[0].id == "peer_allowedips_mismatch"
    assert report.findings[0].severity == "blocking"
    assert report.findings[0].confidence == "high"
