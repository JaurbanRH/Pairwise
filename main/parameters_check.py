"""Parameters check class for pairwise tool"""
import json


class ParametersCheck:
    """Parameters check class"""

    def __init__(self, input_file):
        self.weights = None
        self.parameters = None
        self.file = None
        self.input_file = input_file

    def check_parameters(self):
        """Checks if input paramateres are correct"""
        self.try_load()
        self._check_empty_kind()
        self._check_duplicate_parameter()
        self._check_nonexistent_weight()
        self._check_negative_weight()

    def try_load(self):
        """Try to load input json file"""
        try:
            self.file = json.load(self.input_file)
        except Exception as e:
            raise InvalidJSON("\nGiven JSON file is invalid.") from e

        self.parameters = self.file["Parameters"]
        self.weights = self.file.get("Weights", {})

    def _check_empty_kind(self):
        """Checks if any parameters list is empty"""
        for kind, parameters in self.parameters.items():
            if not parameters:
                raise EmptyList(f"\nList of parameters for {kind} is empty.")

    def _check_duplicate_parameter(self):
        """Checks if any parameter is present more tha once"""
        seen = set()
        duplicates = set()
        lst = []
        for params in self.parameters.values():
            lst.extend(params)
        for item in lst:
            if item in seen:
                duplicates.add(item)
            seen.add(item)

        if len(duplicates) != 0:
            raise DuplicateParameter(
                f"\nParameters {list(duplicates)} are present more than once."
                f"\nPlease use unique name for each parameter."
            )

    def _check_nonexistent_weight(self):
        """Checks if there is weight set for nonexistent parameter"""
        lst = []
        for params in self.parameters.values():
            lst.extend(params)
        for weight in self.weights.keys():
            if weight not in lst:
                raise InvalidWeight(f"Parameter '{weight}' doesn't exists.")

    def _check_negative_weight(self):
        """Checks if there is negative weight set for any parameter"""
        for k, v in self.weights.items():
            if v < 0:
                raise InvalidWeight(f"Weight for parameter '{k}' is negative.")


class EmptyList(Exception):
    """Exception class for empty parameters list"""


class DuplicateParameter(Exception):
    """Exception class for duplicate parameter"""


class InvalidJSON(Exception):
    """Exception class for invalid JSON file"""


class InvalidWeight(Exception):
    """Exception class for invalid parameter weight"""
