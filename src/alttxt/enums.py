from enum import Enum

class Listable(Enum):
    @classmethod
    def list(cls) -> "list[Enum]":
        return list(v.value for v in cls)

class Verbosity(Listable):
    """
    Various available verbosity levels.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    def __str__(self) -> str:
        return self.value

class Explanation(Listable):
    """
    3 possible levels for the -explain-upset flag.
    """
    NONE = "none"
    SIMPLE = "simple"
    FULL = "full"

class Level(Listable):
    """
    Various available semantic content levels.
    3 is TBA.
    """
    ONE = "1"
    TWO = "2"
    DEFAULT = "default"

    def __str__(self) -> str:
        return self.value

class SubsetField(Listable):
    """
    Enum for the different attributes of the subset class,
    used for sort functions and similar which need to
    take an attribute as a parameter to sort by.
    Any changes to the Subset class need to be reflected here.
    """
    NAME = "name"
    SIZE = "size"
    DEVIATION = "dev"
    DEGREE = "degree"


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
    SIZE = "Size"
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
