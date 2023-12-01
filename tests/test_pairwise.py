"""Test for pairwise tool"""

import os

import pytest


@pytest.fixture()
def input_file(create_file):
    """Create file with input parameters"""
    data = {"Parameters": {"P1": ["a", "b"], "P2": [1, 2], "P3": ["x", "y"]}}
    return create_file(data)


def test_pairwise(capfd, input_file):
    """Test correct configuration generation"""
    os.system(f"pipenv run pairwise {input_file}")
    capture = capfd.readouterr()
    assert "1: ['a', 2, 'y']\n2: ['a', 1, 'x']\n3: ['b', 1, 'y']\n4: ['b', 2, 'x']\n" == capture.out


def test_output_to_csv(capfd, input_file, request):
    """Test output to csv file"""
    request.addfinalizer(lambda: os.remove("out.csv"))
    os.system(f"pipenv run pairwise --output out.csv {input_file}")
    capture = capfd.readouterr()
    assert "1: ['a', 2, 'y']\n2: ['a', 1, 'x']\n3: ['b', 1, 'y']\n4: ['b', 2, 'x']\n" == capture.out
    assert os.path.isfile("out.csv")
