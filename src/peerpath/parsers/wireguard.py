from __future__ import annotations

from peerpath.models import WireGuardPeer, WireGuardState


def _split_allowed_ips(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def parse_wg_show_dump(text: str) -> WireGuardState:
    interface = ""
    listen_port: int | None = None
    peers: list[WireGuardPeer] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        fields = line.split("\t")
        if len(fields) == 5:
            interface = fields[0]
            try:
                listen_port = int(fields[3])
            except ValueError:
                listen_port = None
        elif len(fields) >= 9:
            peers.append(
                WireGuardPeer(
                    public_key=fields[1],
                    endpoint=fields[3],
                    allowed_ips=_split_allowed_ips(fields[4]),
                )
            )

    return WireGuardState(interface=interface, listen_port=listen_port, peers=tuple(peers))


def parse_wg_showconf(text: str) -> WireGuardState:
    interface_address = ""
    peers: list[WireGuardPeer] = []
    current_section = ""
    current_public_key = ""
    current_allowed_ips: tuple[str, ...] = ()

    def flush_peer() -> None:
        nonlocal current_public_key, current_allowed_ips
        if current_public_key or current_allowed_ips:
            peers.append(
                WireGuardPeer(public_key=current_public_key, allowed_ips=current_allowed_ips)
            )
        current_public_key = ""
        current_allowed_ips = ()

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            if current_section == "Peer":
                flush_peer()
            current_section = line.strip("[]")
            continue
        if "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if current_section == "Interface" and key == "Address":
            interface_address = value
        elif current_section == "Peer" and key == "PublicKey":
            current_public_key = value
        elif current_section == "Peer" and key == "AllowedIPs":
            current_allowed_ips = _split_allowed_ips(value)

    if current_section == "Peer":
        flush_peer()

    return WireGuardState(interface_address=interface_address, peers=tuple(peers))
