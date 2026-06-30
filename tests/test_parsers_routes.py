from peerpath.parsers.routes import parse_ip_routes


def test_parse_ip_routes_detects_missing_peer_cidr():
    routes = parse_ip_routes(
        "default via 192.0.2.1 dev eth0\n"
        "172.28.0.0/16 dev br-peerpath\n"
    )
    assert routes.has_route_for("10.44.0.0/24") is False
    assert routes.has_route_for("172.28.0.0/16") is True


def test_parse_ip_routes_detects_covering_route():
    routes = parse_ip_routes("10.44.0.0/24 via 172.28.0.2 dev br-peerpath\n")
    assert routes.has_route_for("10.44.0.2/32") is True
