from __future__ import annotations

from peerpath.models import RouteEntry, RouteTable


def parse_ip_routes(text: str) -> RouteTable:
    routes: list[RouteEntry] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        destination = parts[0]
        if destination == "default":
            destination = "0.0.0.0/0"
        via = ""
        dev = ""
        if "via" in parts:
            via_index = parts.index("via")
            if via_index + 1 < len(parts):
                via = parts[via_index + 1]
        if "dev" in parts:
            dev_index = parts.index("dev")
            if dev_index + 1 < len(parts):
                dev = parts[dev_index + 1]
        routes.append(RouteEntry(destination=destination, via=via, dev=dev))
    return RouteTable(routes=tuple(routes))
