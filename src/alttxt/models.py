from alttxt.enums import AggregateBy, SortBy, SortVisibleBy
from pydantic import BaseModel

class Subset(BaseModel):
    """
    This represents a single intersection between two sets,
    which is displayed as a row in the UpSet plot.
    Any field changes/additions need to be reflected in the
    SubsetField enum in types.py.
    """
    name: str
    size: int # size
    dev: float # Deviation
    degree: int # Set to -1 if parser fails to find degree

class DataModel(BaseModel):
    """
    For holding data from the "rawData" and "processedData" fields
    of the JSON data file.
    """
    membs: list # of frozenset[str]
    count: list # of int
    sets: list # of str
    sizes: dict # str -> int
    subsets: list # of Subset


class FilterModel(BaseModel):
    max_visible: int
    min_visible: int
    hide_empty: bool


class BookmarkedIntersectionModel(BaseModel):
    id: str
    label: str
    size: int


class PlotModel(BaseModel):
    scatterplots: list # of float
    histograms: list # of float
    wordclouds: list # of float


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
    collapsed: list # of str
    visible_sets: list # of str
    visible_atts: list # of str
    plots: PlotModel
    bookmarked_intersections: list # of BookmarkedIntersectionModel