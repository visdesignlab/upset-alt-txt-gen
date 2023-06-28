from pprint import pprint
from alttxt.models import DataModel
from alttxt.models import GrammarModel
from alttxt.parser import Parser
from alttxt.types import ParseType
from pathlib import Path

"""
This file specifies the constructors for the data models,
objects which hold data parsed from files.
Models.py defines the fields necessary for each model.

Each constructor takes a file path and returns a model.
The 'model' property is used to make the data immutable after
it has been parsed.

Currently, only DataModel and GrammarModel are used-
the others will likely be removed
"""
Model = DataModel | GrammarModel


class SetData:
    def __init__(self, file_path: Path) -> None:
        self.data = Parser(file_path).data

    @property
    def model(self) -> Model:
        return self.data


class RawData:
    def __init__(self, file_path: Path) -> None:
        self.data = Parser(file_path, ParseType.DATA).data

    @property
    def model(self) -> Model:
        return self.data


class MatData:
    def __init__(self, file_path: Path) -> None:
        self.data = Parser(file_path).data

    @property
    def model(self) -> Model:
        return self.data


class TblData:
    def __init__(self, file_path: Path) -> None:
        self.data = Parser(file_path).data

    @property
    def model(self) -> Model:
        return self.data


class Grammar:
    def __init__(self, file_path: Path) -> None:
        self.grammar = Parser(file_path, ParseType.GRAMMAR).data

    @property
    def model(self) -> Model:
        return self.grammar
