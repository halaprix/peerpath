from __future__ import annotations

from ipaddress import ip_network

from peerpath.models import DiagnosticReport, Finding, LoadedFixture, RemediationOption
from peerpath.parsers.routes import parse_ip_routes
from peerpath.parsers.sysctl import parse_forwarding_sysctls
from peerpath.parsers.wireguard import parse_wg_show_dump

SEVERITY_RANK = {"unsafe": 3, "blocking": 2, "warning": 1, "info": 0}
CONFIDENCE_RANK = {"high": 2, "medium": 1, "low": 0}


def _inspect_option(title: str, detail: str) -> tuple[RemediationOption, ...]:
    return (RemediationOption(title=title, detail=detail, risk_label="inspect-only"),)


def _allowed_ips_cover_target(allowed_ips: tuple[str, ...], target_cidr: str) -> bool:
    target = ip_network(target_cidr, strict=False)
    for value in allowed_ips:
        try:
            network = ip_network(value, strict=False)
        except ValueError:
            continue
        if target.version != network.version:
            continue
        if target.subnet_of(network) or target == network:
            return True
    return False


def _host_missing_route(fixture: LoadedFixture) -> Finding | None:
    routes = parse_ip_routes(fixture.collectors["ip-route"])
    target = fixture.manifest.target.peer_cidr
    if routes.has_route_for(target):
        return None
    return Finding(
        id="host_missing_route_to_peer_cidr",
        title="Host has no specific route to the WireGuard peer CIDR",
        severity="blocking",
        confidence="high",
        evidence=(
            f"Target peer CIDR: {target}",
            "No non-default route covers that CIDR in ip route output.",
        ),
        explanation=(
            "The host can reach the Docker bridge, but it does not know that peer-side "
            "addresses should be routed toward the wg-easy container."
        ),
        safe_next_check="Inspect the host route table for a specific route to the peer CIDR.",
        remediation_options=_inspect_option(
            "Confirm intended next hop",
            "Before adding any persistent route, verify the wg-easy container IP and bridge name.",
        ),
    )


def _forwarding_disabled(fixture: LoadedFixture) -> Finding | None:
    forwarding = parse_forwarding_sysctls(fixture.collectors["sysctl"])
    if forwarding.ipv4_forwarding is not False:
        return None
    return Finding(
        id="forwarding_disabled",
        title="IPv4 forwarding is disabled",
        severity="blocking",
        confidence="high",
        evidence=("net.ipv4.ip_forward = 0",),
        explanation=(
            "Host/container/peer reachability requires packet forwarding across interfaces, "
            "but the kernel forwarding switch is off."
        ),
        safe_next_check="Inspect sysctl forwarding settings before changing any persistent config.",
        remediation_options=_inspect_option(
            "Confirm forwarding requirement",
            "Check whether this host is intended to route between Docker and WireGuard networks.",
        ),
    )


def _allowedips_mismatch(fixture: LoadedFixture) -> Finding | None:
    wg_state = parse_wg_show_dump(fixture.collectors["wg-show-dump"])
    target = fixture.manifest.target.peer_cidr
    if any(_allowed_ips_cover_target(peer.allowed_ips, target) for peer in wg_state.peers):
        return None
    allowed = ", ".join(
        allowed_ip for peer in wg_state.peers for allowed_ip in peer.allowed_ips
    ) or "<none>"
    return Finding(
        id="peer_allowedips_mismatch",
        title="Peer AllowedIPs do not cover the intended peer CIDR",
        severity="blocking",
        confidence="high",
        evidence=(f"Target peer CIDR: {target}", f"Observed peer AllowedIPs: {allowed}"),
        explanation=(
            "WireGuard routes packets by AllowedIPs. If the intended CIDR is not covered, "
            "traffic can be sent to the wrong peer or never enter the tunnel."
        ),
        safe_next_check=(
            "Compare the intended route with each peer's AllowedIPs before editing config."
        ),
        remediation_options=_inspect_option(
            "Confirm peer ownership of the CIDR",
            "Verify which peer should own the CIDR and whether a narrower /32 is intentional.",
        ),
    )


def _sort_findings(findings: list[Finding]) -> tuple[Finding, ...]:
    return tuple(
        sorted(
            findings,
            key=lambda finding: (
                SEVERITY_RANK[finding.severity],
                CONFIDENCE_RANK[finding.confidence],
                finding.id,
            ),
            reverse=True,
        )
    )


def analyze_fixture(fixture: LoadedFixture) -> DiagnosticReport:
    findings = [
        finding
        for finding in (
            _host_missing_route(fixture),
            _forwarding_disabled(fixture),
            _allowedips_mismatch(fixture),
        )
        if finding is not None
    ]
    return DiagnosticReport(fixture_name=fixture.manifest.name, findings=_sort_findings(findings))
