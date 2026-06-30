from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Severity = Literal["info", "warning", "blocking", "unsafe"]
Confidence = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class RemediationOption:
    title: str
    detail: str
    risk_label: str


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


@dataclass(frozen=True)
class PathCheck:
    name: str
    observed_state: str
    likely_causes: tuple[str, ...]


@dataclass(frozen=True)
class DiagnosticReport:
    fixture_name: str
    findings: tuple[Finding, ...]
    path_matrix: tuple[PathCheck, ...] = ()


@dataclass(frozen=True)
class DockerService:
    name: str
    service: str
    state: str


@dataclass(frozen=True)
class DockerState:
    container_name: str
    network_mode: str
    container_ip: str
    gateway: str
    prefix_len: int | None
    published_ports: tuple[str, ...]
    capabilities: tuple[str, ...]


@dataclass(frozen=True)
class WireGuardPeer:
    public_key: str
    allowed_ips: tuple[str, ...]
    endpoint: str = ""


@dataclass(frozen=True)
class WireGuardState:
    interface: str = ""
    listen_port: int | None = None
    interface_address: str = ""
    peers: tuple[WireGuardPeer, ...] = ()


@dataclass(frozen=True)
class RouteEntry:
    destination: str
    via: str = ""
    dev: str = ""


@dataclass(frozen=True)
class RouteTable:
    routes: tuple[RouteEntry, ...]

    def has_route_for(self, cidr: str) -> bool:
        from ipaddress import ip_network

        target = ip_network(cidr, strict=False)
        for route in self.routes:
            try:
                network = ip_network(route.destination, strict=False)
            except ValueError:
                continue
            if target.version != network.version:
                continue
            if network.prefixlen == 0:
                continue
            if target.subnet_of(network) or target == network:
                return True
        return False


@dataclass(frozen=True)
class ForwardingState:
    ipv4_forwarding: bool | None = None
    ipv6_forwarding: bool | None = None


@dataclass(frozen=True)
class FirewallSummary:
    backend: str = "unknown"
    forward_policy: str = "unknown"
    masquerade_enabled: bool = False
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class FixtureTarget:
    peer_cidr: str
    peer_ip: str
    wg_interface: str
    container_name: str


@dataclass(frozen=True)
class FixtureManifest:
    name: str
    description: str
    target: FixtureTarget


@dataclass(frozen=True)
class FixtureExpected:
    top_finding_id: str
    top_severity: str


@dataclass(frozen=True)
class LoadedFixture:
    root: Path
    manifest: FixtureManifest
    collectors: dict[str, str]
    expected: FixtureExpected
