"""Test for argument parsing of pairwise tools"""

import os

import pytest


@pytest.fixture()
def valid_parameters(create_file):
    """Creates file with valid paramaters data"""
    data = {"Parameters": {"P1": ["a", "b"], "P2": [1, 2], "P3": ["x", "y"]}}
    return create_file(data)


@pytest.fixture()
def empty_list(create_file):
    """Creates file with empty parameters list"""
    data = {"Parameters": {"P1": [], "P2": [1, 2], "P3": ["x", "y"]}}
    return create_file(data)


@pytest.fixture()
def invalid_weight(create_file):
    """Creates file with valid invalid parameter weight"""
    data = {"Parameters": {"P1": ["a", "b"], "P2": [1, 2], "P3": ["x", "y"]}, "Weights": {"invalid": 1}}
    return create_file(data)


@pytest.fixture()
def negative_weight(create_file):
    """Creates file with valid negative parameter weight"""
    data = {"Parameters": {"P1": ["a", "b"], "P2": [1, 2], "P3": ["x", "y"]}, "Weights": {"a": -1}}
    return create_file(data)


@pytest.fixture()
def not_file():
    """Returns filename that doesn't exist"""
    return "not_file.json"


def test_empty_arg(capfd):
    """Test error message from empty arguments"""
    os.system("pipenv run pairwise")
    capture = capfd.readouterr()
    assert "Error: Missing argument 'PARAMETERS'" in capture.err


def test_valid_parameters(capfd, valid_parameters):
    """Test that no error message is present with valid arguments"""
    os.system(f"PIPENV_VERBOSITY=-1 pipenv run pairwise {valid_parameters}")
    capture = capfd.readouterr()
    assert capture.err == ""


@pytest.mark.parametrize(
    ("data", "error"),
    [
        ("empty_list", "List of parameters for P1 is empty"),
        ("invalid_weight", "Parameter 'invalid' doesn't exists."),
        ("negative_weight", "Weight for parameter 'a' is negative."),
        ("not_file", "Error: Invalid value for 'PARAMETERS': 'not_file.json': No such file or directory"),
    ],
)
def test_invalid_parameters(request, capfd, data, error):
    """Test error message for different invalid parameters"""
    filename = request.getfixturevalue(data)
    os.system(f"pipenv run pairwise {filename}")
    capture = capfd.readouterr()
    assert error in capture.err


@pytest.mark.parametrize(
    ("option", "error"),
    [
        ("--invalid", "Error: No such option: --invalid"),
        ("--margin invalid", "Error: Invalid value for '-m' / '--margin': 'invalid' is not a valid float."),
    ],
)
def test_invalid_option(capfd, valid_parameters, option, error):
    """Test error message for different invalid options"""
    os.system(f"pipenv run pairwise {option} {valid_parameters}")
    capture = capfd.readouterr()
    assert error in capture.err
