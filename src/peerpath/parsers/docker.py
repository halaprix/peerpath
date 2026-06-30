from __future__ import annotations

import json

from peerpath.models import DockerService, DockerState


def parse_docker_inspect(text: str) -> DockerState:
    data = json.loads(text)
    item = data[0] if isinstance(data, list) and data else data
    host_config = item.get("HostConfig", {})
    networks = item.get("NetworkSettings", {}).get("Networks", {})
    first_network = next(iter(networks.values()), {}) if networks else {}

    published_ports: list[str] = []
    for container_port, bindings in host_config.get("PortBindings", {}).items():
        for binding in bindings or []:
            host_ip = binding.get("HostIp", "")
            host_port = binding.get("HostPort", "")
            published_ports.append(f"{container_port}->{host_ip}:{host_port}")

    return DockerState(
        container_name=str(item.get("Name", "")).lstrip("/"),
        network_mode=str(host_config.get("NetworkMode", "")),
        container_ip=str(first_network.get("IPAddress", "")),
        gateway=str(first_network.get("Gateway", "")),
        prefix_len=first_network.get("IPPrefixLen"),
        published_ports=tuple(published_ports),
        capabilities=tuple(host_config.get("CapAdd") or ()),
    )


def parse_compose_ps(text: str) -> tuple[DockerService, ...]:
    data = json.loads(text)
    return tuple(
        DockerService(
            name=str(item.get("Name", "")),
            service=str(item.get("Service", "")),
            state=str(item.get("State", "")),
        )
        for item in data
    )
