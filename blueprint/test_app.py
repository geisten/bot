from .app import Blueprint

def test_app(capsys):
    Blueprint.run()
    captured = capsys.readouterr()

    assert "Hello World..." in captured.out
