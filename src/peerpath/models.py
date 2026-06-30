from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
