from alttxt.models import DataModel
from alttxt.models import GrammarModel
from alttxt.types import FileType
from alttxt.parser import Parser
from pathlib import Path

"""
This file specifies the constructors for the data models,
objects which hold data parsed from files.
Models.py defines the fields necessary for each model.

Each constructor takes a file path and returns a model.
The 'model' property is used to make the data immutable after
it has been parsed.
"""
Model = DataModel | GrammarModel


class SetData:
    def __init__(self, file_path: Path) -> None:
        self.data = Parser(file_path, FileType.SETDATA)._data

    @property
    def model(self) -> Model:
        return self.data


class RawData:
    def __init__(self, file_path: Path) -> None:
        self.data = Parser(file_path, FileType.RAWDATA)._data

    @property
    def model(self) -> Model:
        return self.data


class MatData:
    def __init__(self, file_path: Path) -> None:
        self.data = Parser(file_path, FileType.MATDATA)._data

    @property
    def model(self) -> Model:
        return self.data


class TblData:
    def __init__(self, file_path: Path) -> None:
        self.data = Parser(file_path, FileType.TBLDATA)._data

    @property
    def model(self) -> Model:
        return self.data


class Grammar:
    def __init__(self, file_path: Path) -> None:
        self.grammar = Parser(file_path, FileType.GRAMMAR)._data

    @property
    def model(self) -> Model:
        return self.grammar
