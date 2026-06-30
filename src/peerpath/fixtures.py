from __future__ import annotations

import json
from pathlib import Path

from peerpath.models import FixtureExpected, FixtureManifest, FixtureTarget, LoadedFixture

REQUIRED_COLLECTOR_FILES = (
    "docker-inspect.json",
    "docker-compose-ps.json",
    "wg-show-dump.txt",
    "wg-showconf.conf",
    "ip-route.txt",
    "sysctl.txt",
    "firewall.txt",
)


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}") from exc


def load_fixture(root: Path) -> LoadedFixture:
    root = Path(root)
    manifest_path = root / "manifest.json"
    expected_path = root / "expected.json"
    collectors_dir = root / "collectors"

    missing = [
        str(path.relative_to(root))
        for path in (manifest_path, expected_path, collectors_dir)
        if not path.exists()
    ]
    missing.extend(
        f"collectors/{name}"
        for name in REQUIRED_COLLECTOR_FILES
        if not (collectors_dir / name).exists()
    )
    if missing:
        raise ValueError(f"fixture {root} is missing required files: {', '.join(missing)}")

    manifest_data = _read_json(manifest_path)
    target_data = manifest_data.get("target", {})
    target = FixtureTarget(
        peer_cidr=target_data["peer_cidr"],
        peer_ip=target_data["peer_ip"],
        wg_interface=target_data["wg_interface"],
        container_name=target_data["container_name"],
    )
    manifest = FixtureManifest(
        name=manifest_data["name"],
        description=manifest_data.get("description", ""),
        target=target,
    )

    expected_data = _read_json(expected_path)
    expected = FixtureExpected(
        top_finding_id=expected_data["top_finding_id"],
        top_severity=expected_data["top_severity"],
    )

    collectors = {
        Path(name).stem: (collectors_dir / name).read_text()
        for name in REQUIRED_COLLECTOR_FILES
    }
    return LoadedFixture(root=root, manifest=manifest, collectors=collectors, expected=expected)


def list_fixtures(fixtures_dir: Path) -> list[FixtureManifest]:
    fixtures_dir = Path(fixtures_dir)
    if not fixtures_dir.exists():
        return []

    manifests: list[FixtureManifest] = []
    for child in sorted(path for path in fixtures_dir.iterdir() if path.is_dir()):
        try:
            manifests.append(load_fixture(child).manifest)
        except ValueError:
            continue
    return manifests
