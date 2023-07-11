from alttxt.types import AggregateBy, SortBy, SortVisibleBy
from pydantic import BaseModel
from typing import Any


class Subset(BaseModel):
    """
    This represents a single intersection between two sets,
    which is displayed as a row in the UpSet plot.
    Any field changes/additions need to be reflected in the
    SubsetField enum in types.py.
    """
    name: str
    size: int # Cardinality
    dev: float # Deviation
    degree: int # Set to -1 if parser fails to find degree

class DataModel(BaseModel):
    """
    For holding data from the "rawData" and "processedData" fields
    of the JSON data file.
    """
    membs: list[frozenset[str]]
    count: list[int]
    sets: list[str]
    sizes: dict[str, int]
    subsets: list[Subset]


class FilterModel(BaseModel):
    max_visible: int
    min_visible: int
    hide_empty: bool


class BookmarkedIntersectionModel(BaseModel):
    id: str
    label: str
    size: int


class PlotModel(BaseModel):
    scatterplots: list[float]
    histograms: list[float]
    wordclouds: list[float]


class GrammarModel(BaseModel):
    # TODO: Uncomment these if added to the JSON export
    #caption: str
    #title: str
    first_aggregate_by: AggregateBy
    second_aggregate_by: AggregateBy
    first_overlap_degree: int
    second_overlap_degree: int
    sort_visible_by: SortVisibleBy
    sort_by: SortBy
    filters: FilterModel
    collapsed: list[str]
    visible_sets: list[str]
    visible_atts: list[str]
    plots: PlotModel
    bookmarked_intersections: list[BookmarkedIntersectionModel]