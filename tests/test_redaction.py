from peerpath.redaction import redact_text


def test_redacts_wireguard_secret_material():
    text = "PrivateKey = abcdefghijklmnopqrstuvwxyz1234567890=\nPresharedKey = abcdef"
    redacted = redact_text(text)
    assert "abcdefghijklmnopqrstuvwxyz" not in redacted
    assert "PrivateKey = <redacted>" in redacted
    assert "PresharedKey = <redacted>" in redacted


def test_redacts_local_home_paths():
    redacted = redact_text("config at /home/alice/wg/config and /Users/bob/wg.conf")
    assert "/home/alice" not in redacted
    assert "/Users/bob" not in redacted
    assert "/home/<user>/" in redacted
    assert "/Users/<user>/" in redacted


def test_does_not_redact_private_route_cidrs():
    redacted = redact_text("route 10.44.0.0/24 via 172.28.0.2")
    assert "10.44.0.0/24" in redacted
    assert "172.28.0.2" in redacted
