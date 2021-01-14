"""Test the app module"""
from .app import Blueprint


def test_app(capsys):
    """Test the main (starter) method"""
    Blueprint.run()
    captured = capsys.readouterr()

    assert "Hello World..." in captured.out
