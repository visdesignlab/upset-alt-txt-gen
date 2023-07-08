import re
from enum import auto, Enum
from typing import Any


class Listable(Enum):
    @classmethod
    def list(cls) -> list[Enum]:
        return list(v.value for v in cls)

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

    def __str__(self) -> str:
        return self.value


class AggregateBy(Listable):
    """
    Enum for the different aggregation options.
    Strings need to be kept up-to-date with any changes
    to the MultiNet implementation's export format.
    """
    DEGREE = "Degree"
    SETS = "Sets"
    DEVIATION = "Deviations"
    OVERLAP = "Overlaps"
    NONE = "None"


class SortBy(Listable):
    """
    Enum for the different sorting options.
    Strings need to be kept up-to-date with any changes
    to the MultiNet implementation's export format.
    """
    DEGREE = "Degree"
    CARDINALITY = "Cardinality"
    DEVIATION = "Deviation"


class SortVisibleBy(Listable):
    """
    Enum for the different sorting options.
    Strings need to be kept up-to-date with any changes
    to the MultiNet implementation's export format.
    """
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
