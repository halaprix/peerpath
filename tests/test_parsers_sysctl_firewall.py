from peerpath.parsers.firewall import parse_firewall_summary
from peerpath.parsers.sysctl import parse_forwarding_sysctls


def test_parse_forwarding_disabled():
    state = parse_forwarding_sysctls(
        "net.ipv4.ip_forward = 0\n"
        "net.ipv6.conf.all.forwarding = 0\n"
    )
    assert state.ipv4_forwarding is False
    assert state.ipv6_forwarding is False


def test_parse_forwarding_enabled():
    state = parse_forwarding_sysctls("net.ipv4.ip_forward = 1\n")
    assert state.ipv4_forwarding is True


def test_parse_firewall_summary_collects_backend_and_forward_policy():
    summary = parse_firewall_summary(
        "backend: nftables\n"
        "policy forward drop\n"
        "masquerade: enabled for 172.28.0.0/16\n"
    )
    assert summary.backend == "nftables"
    assert summary.forward_policy == "drop"
    assert summary.masquerade_enabled is True
