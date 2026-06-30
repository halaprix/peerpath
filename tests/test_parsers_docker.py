from peerpath.parsers.docker import parse_compose_ps, parse_docker_inspect


def test_parse_docker_inspect_extracts_container_network_and_ports():
    inspect_text = """[
      {
        "Name": "/peerpath-wg-easy",
        "HostConfig": {
          "NetworkMode": "peerpath_net",
          "CapAdd": ["NET_ADMIN", "SYS_MODULE"],
          "PortBindings": {"51820/udp": [{"HostIp": "0.0.0.0", "HostPort": "51820"}]}
        },
        "NetworkSettings": {
          "Networks": {
            "peerpath_net": {"IPAddress": "172.28.0.2", "Gateway": "172.28.0.1", "IPPrefixLen": 16}
          }
        }
      }
    ]"""
    state = parse_docker_inspect(inspect_text)
    assert state.container_name == "peerpath-wg-easy"
    assert state.network_mode == "peerpath_net"
    assert state.container_ip == "172.28.0.2"
    assert state.published_ports == ("51820/udp->0.0.0.0:51820",)
    assert "NET_ADMIN" in state.capabilities


def test_parse_compose_ps_extracts_running_service():
    ps_text = '[{"Name":"peerpath-wg-easy","Service":"wg-easy","State":"running"}]'
    services = parse_compose_ps(ps_text)
    assert services[0].name == "peerpath-wg-easy"
    assert services[0].service == "wg-easy"
    assert services[0].state == "running"
