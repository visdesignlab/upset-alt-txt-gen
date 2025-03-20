from enum import Enum
from typing import Dict, Optional
from alttxt.enums import AggregateBy, SortBy, SortVisibleBy, SortOrder, IntersectionType
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
    classification: IntersectionType
    setMembership: set

class DataModel(BaseModel):
    """
    For holding data from the "rawData" and "processedData" fields
    of the JSON data file.
    """

    count: list # of int
    sets: list # of str
    sizes: dict # str -> int
    subsets: list # of Subset
    all_subsets: list # of All Subsets
    all_sets_length: int

class FilterModel(BaseModel):
    max_visible: int
    min_visible: int
    hide_empty: bool
    hide_no_set: bool


class BookmarkedIntersectionModel(BaseModel):
    id: str
    label: str
    size: int


class PlotModel(BaseModel):
    scatterplots: list  # of float
    histograms: list  # of float


class MetaDataModel(BaseModel):
    title: Optional[str] = ""
    caption: Optional[str] = ""
    description: Optional[str] = ""
    sets: Optional[str] = ""
    items: Optional[str] = ""

class SetMembershipStatus(str, Enum):
    '''Possible set membership statuses'''
    YES = "Yes"
    NO = "No"
    MAY = "May"
    
class SetQueryModel(BaseModel):
    '''A set query, which defines which sets are included, excluded, or may be included in the intersections'''
    name: str
    query: Dict[str, SetMembershipStatus]

class GrammarModel(BaseModel):
    # TODO: Uncomment these if added to the JSON export
    # caption: str
    # title: str
    first_aggregate_by: AggregateBy
    second_aggregate_by: AggregateBy
    first_overlap_degree: int
    second_overlap_degree: int
    sort_visible_by: SortVisibleBy
    sort_by: SortBy
    sort_order: SortOrder
    filters: FilterModel
    collapsed: list  # of str
    visible_sets: list  # of str
    visible_atts: list  # of str
    visible_set_sizes: dict  # str -> int
    plots: PlotModel
    metaData: MetaDataModel
    bookmarked_intersections: list  # of BookmarkedIntersectionModel
    set_query: Optional[SetQueryModel]
