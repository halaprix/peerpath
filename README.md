# PeerPath

A read-only CLI doctor for Dockerized WireGuard/wg-easy setups that explains why the host, container, and peers can or cannot reach each other, then prints the smallest safe routing/firewall fix.

## Problem

Self-hosters adopt wg-easy because bare WireGuard is annoying to manage, but host-to-peer and reverse-proxy-to-peer routing still depends on Docker networking, WireGuard peer config, host routes, forwarding sysctls, nftables/iptables state, firewall policy, and wg-easy hooks.

When that breaks, users often end up with trial-and-error commands from forum posts or AI chat. Those fixes may be ephemeral, reboot-sensitive, or unsafe.

## Evidence

| Source | Link | Signal |
|---|---|---|
| Reddit / r/selfhosted | https://www.reddit.com/r/selfhosted/comments/1ujajsu/how_to_setup_bridge_between_host_and_wgeasy/ | Fresh post: wg-easy container can reach peers, but the host cannot; the user describes AI/trial-and-error iptables fixes as hard to reproduce. |
| wg-easy | https://github.com/wg-easy/wg-easy | Popular WireGuard + web UI project with Docker-first setup and iptables-sensitive firewall features. |
| wg-easy docs | https://wg-easy.github.io/wg-easy/latest/examples/tutorials/basic-installation/ | Official basic install is Docker Compose-first. |
| wg-easy Podman/nftables docs | https://wg-easy.github.io/wg-easy/latest/examples/tutorials/podman-nft/ | Official advanced setup needs capabilities, sysctls, kernel modules, nftables hooks, and restart behavior. |
| Docker docs | https://docs.docker.com/engine/network/packet-filtering-firewalls/ | Docker creates firewall rules and can set forwarding behavior that surprises router/VPN hosts. |
| WireGuard quick start | https://www.wireguard.com/quickstart/ | WireGuard exposes routing, peer, keepalive, and `wg show` primitives that can be inspected read-only. |

## Competitor / Substitute Check

| Type | Name / Substitute | Notes |
|---|---|---|
| Direct competitor | wg-easy docs and GitHub issues | Authoritative, but not a machine-specific reachability report. |
| Direct competitor | Netmaker / Tailscale / NetBird-style mesh VPNs | Strong alternatives if the user switches stack; they do not diagnose an existing wg-easy Docker box. |
| Direct competitor | Docker, WireGuard, nftables, and iptables docs | Correct but low-level and scattered. |
| Indirect substitute | ChatGPT, forum posts, shell history, copied firewall snippets | Can get lucky; often produces brittle fixes and poor operator understanding. |
| Status quo | Manual probing inside containers plus ad-hoc routes/firewall rules | Wastes hours and can create outages or accidental exposure. |

## Wedge

PeerPath is a diagnostic adapter, not a VPN platform. It correlates facts from the host, the wg-easy container, peer config, routes, forwarding, and firewall state into a single “why can/can’t this path connect?” report.

## Target user

Homelab/self-hosted operators running wg-easy in Docker or Podman who need reliable host-to-peer, peer-to-host, or reverse-proxy-to-peer connectivity.

## MVP

- `peerpath doctor` read-only report.
- Fixture mode for demos and CI.
- Parsers for `docker inspect`, `wg show`, `ip route`, forwarding sysctls, and nft/iptables summaries.
- Safe connectivity probes for host/container/peer paths.
- Ranked remediation snippets with risk labels.
- Markdown/JSON export for support threads and GitHub issues.

## Non-goals

- No default mutation of firewall, routing, or VPN state.
- Not a replacement for wg-easy, WireGuard, or mesh VPN platforms.
- No storage of private VPN keys or secrets.
- No enterprise VPN management in the first version.

## Safety model

PeerPath v0.1 is read-only. It reports evidence and risk-labeled next checks; it does not mutate routes, firewall rules, Docker networks, or WireGuard state.

Committed fixtures are synthetic. Local reports may include private route CIDRs because those addresses are diagnostic evidence; do not publish a report until you have reviewed it for hostnames, paths, comments, and secrets.

## Status

v0.1.0-alpha.0 — scaffold/spec only.
