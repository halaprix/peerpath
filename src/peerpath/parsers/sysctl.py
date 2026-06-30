from __future__ import annotations

from peerpath.models import ForwardingState


def _parse_bool(value: str) -> bool | None:
    value = value.strip()
    if value == "1":
        return True
    if value == "0":
        return False
    return None


def parse_forwarding_sysctls(text: str) -> ForwardingState:
    ipv4: bool | None = None
    ipv6: bool | None = None
    for raw_line in text.splitlines():
        if "=" not in raw_line:
            continue
        key, value = (part.strip() for part in raw_line.split("=", 1))
        if key == "net.ipv4.ip_forward":
            ipv4 = _parse_bool(value)
        elif key == "net.ipv6.conf.all.forwarding":
            ipv6 = _parse_bool(value)
    return ForwardingState(ipv4_forwarding=ipv4, ipv6_forwarding=ipv6)
