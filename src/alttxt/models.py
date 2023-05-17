from pydantic import BaseModel

from alttxt.types_ import AggregateBy, SortBy, SortVisibleBy


class DataModel(BaseModel):
    membs: list[frozenset[str]]
    count: list[int]
    sets: list[str]
    sizes: dict[str, int]
    devs: list[float]


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
