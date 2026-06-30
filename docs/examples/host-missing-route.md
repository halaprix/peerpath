# PeerPath Diagnostic Report

## Summary

Fixture: `host-missing-route`
Findings: 1

## Path matrix

No path checks were generated for this fixture.

## Findings

### blocking: Host has no specific route to the WireGuard peer CIDR

- ID: `host_missing_route_to_peer_cidr`
- Confidence: high
- Evidence:
  - Target peer CIDR: 10.44.0.0/24
  - No non-default route covers that CIDR in ip route output.
- Explanation: The host can reach the Docker bridge, but it does not know that peer-side addresses should be routed toward the wg-easy container.
- Safe next check: Inspect the host route table for a specific route to the peer CIDR.
- Remediation options:
  - Confirm intended next hop
    - Risk label: inspect-only
    - Detail: Before adding any persistent route, verify the wg-easy container IP and bridge name.

## Safety note

PeerPath v0.1 reports evidence and read-only next checks. It does not mutate routes, firewall rules, Docker networks, or WireGuard state.

