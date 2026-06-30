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
