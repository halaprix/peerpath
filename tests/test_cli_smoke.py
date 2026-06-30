from peerpath.cli import main


def test_help_exits_success(capsys):
    code = main(["--help"])
    captured = capsys.readouterr()
    assert code == 0
    assert "peerpath" in captured.out.lower()
    assert "doctor" in captured.out
    assert "fixture" in captured.out
    assert "explain" in captured.out


def test_doctor_requires_fixture_or_collect_flag(capsys):
    code = main(["doctor"])
    captured = capsys.readouterr()
    assert code == 2
    assert "--fixture" in captured.err
    assert "read-only" in captured.err.lower()
