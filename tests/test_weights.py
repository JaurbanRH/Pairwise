"""Tests for pairwise weights"""

import os


def test_unfulfillable_weight(capfd, create_file):
    """Test warn message when weights cannot be fulfilled"""
    data = {"Parameters": {"P1": ["a", "b"], "P2": [1, 2], "P3": ["x", "y"]}, "Weights": {"a": 2, "x": 3}}
    filename = create_file(data)
    os.system(f"pipenv run pairwise {filename}")
    capture = capfd.readouterr()
    assert "No more unique configuration meeting the requirements" in capture.err


def test_weight(capfd, create_file):
    """Test pairwise weights"""
    data = {
        "Parameters": {"P1": ["a", "b", "c", "d"], "P2": ["e", "f", "g", "h"], "P3": ["x", "y"], "P4": [1, 2]},
        "Weights": {"a": 2, "e": 0},
    }
    filename = create_file(data)
    os.system(f"pipenv run pairwise --count {filename}")
    capture = capfd.readouterr()
    assert "('a', 7)" in capture.out
    assert "('b', 4)" in capture.out
    assert "('c', 4)" in capture.out
    assert "('d', 4)" in capture.out
    assert "('e', 4)" in capture.out

    os.system(f"pipenv run pairwise --count --margin 0 {filename}")
    capture = capfd.readouterr()
    assert "('e', 4)" in capture.out
