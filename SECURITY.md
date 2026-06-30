# Security Policy

## Reporting issues

Open a GitHub issue for non-sensitive security concerns. For sensitive reports, avoid posting private VPN configuration, keys, hostnames, or IP inventories publicly.

## Data handling

PeerPath must not store or upload diagnostic data. Reports should be generated locally and redacted before sharing.

## Safety constraints

- Default commands are read-only.
- No firewall, routing, Docker, or VPN mutation in the initial versions.
- Any future mutating command must require explicit flags, preview output, and documentation.
- Private keys and preshared keys must be redacted from all exports and fixtures.
