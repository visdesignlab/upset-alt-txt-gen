import re
from enum import auto, Enum
from typing import Any


class Listable(Enum):
    @classmethod
    def list(cls) -> list[Enum]:
        return list(v.value for v in cls)


class FileType(Listable):
    SETDATA = auto()
    RAWDATA = auto()
    MATDATA = auto()
    TBLDATA = auto()
    GRAMMAR = auto()


class Granularity(Listable):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    def __str__(self) -> str:
        return self.value


class Level(Listable):
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    THREE = "3"

    def __str__(self) -> str:
        return self.value


class AggregateBy(Listable):
    DEGREE = "Degree"
    SETS = "Sets"
    DEVIATION = "Deviation"
    OVERLAPS = "Overlaps"
    NONE = "None"


class SortBy(Listable):
    DEGREE = "Degree"
    CARDINALITY = "Cardinality"
    DEVIATION = "Deviation"


class SortVisibleBy(Listable):
    ALPHABETICAL = "Alphabetical"
    ASCENDING = "Ascending"
    DESCENDING = "Descending"


class Orientation(Listable):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Dict(dict[Any, Any]):
    def __init__(self, dict_obj):
        ...

    def __getattr__(self, attr):
        return self[self.snake_case(attr)]

    def __setattr__(self, attr, value):
        self[self.snake_case(attr)] = value

    def snake_case(self, attr):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", attr).lower()
