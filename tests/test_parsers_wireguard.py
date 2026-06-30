from peerpath.parsers.wireguard import parse_wg_show_dump, parse_wg_showconf


def test_parse_wg_show_dump_extracts_peer_allowed_ips():
    dump = (
        "wg0\tPRIVATE_KEY_REDACTED\tPUBLIC_KEY_SYNTHETIC_HOST\t51820\toff\n"
        "wg0\tPUBLIC_KEY_SYNTHETIC_PEER_A\tPRESHARED_KEY_REDACTED\t"
        "198.51.100.10:51820\t10.44.0.0/24\t0\t0\t0\t25\n"
    )
    state = parse_wg_show_dump(dump)
    assert state.interface == "wg0"
    assert state.listen_port == 51820
    assert state.peers[0].public_key == "PUBLIC_KEY_SYNTHETIC_PEER_A"
    assert state.peers[0].allowed_ips == ("10.44.0.0/24",)


def test_parse_wg_showconf_extracts_interface_address_and_allowed_ips():
    conf = """[Interface]
PrivateKey = PRIVATE_KEY_REDACTED
Address = 10.44.0.1/24
ListenPort = 51820

[Peer]
PublicKey = PUBLIC_KEY_SYNTHETIC_PEER_A
AllowedIPs = 10.44.0.2/32, 10.44.0.3/32
"""
    state = parse_wg_showconf(conf)
    assert state.interface_address == "10.44.0.1/24"
    assert state.peers[0].allowed_ips == ("10.44.0.2/32", "10.44.0.3/32")
