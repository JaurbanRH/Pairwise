"""Conftest for pairwise tests"""
import json
import os
import string
from random import choice

import pytest


@pytest.fixture()
def create_file(request):
    """Create input file from given parameters"""

    def _create_file(data):
        filename = f"{''.join(choice(string.ascii_lowercase) for _ in range(10))}.json"
        request.addfinalizer(lambda: os.remove(filename))
        with open(filename, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile)
        return filename

    return _create_file
