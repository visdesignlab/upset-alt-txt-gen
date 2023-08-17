import json

from alttxt.enums import AggregateBy, SortBy, SortVisibleBy
from alttxt.models import BookmarkedIntersectionModel, Subset, \
        DataModel, FilterModel, GrammarModel, PlotModel

from pathlib import Path
from collections import Counter
from typing import Any
from typing import Union

class Parser:
    """
    Handles parsing of data files into objects.
    Params:
    - data: Path to the data file to be parsed, 
            or a dictionary containing the data parsed from JSON.
    """
    def __init__(self, data: "Union[Path, dict[str, dict[str, Any]]]") -> None:
        # Default message for when a field cannot be found by the parser
        self.default_field = "(field not available)"
        
        # Now load the file and parse the data
        if isinstance(data, Path):
            self.data: dict[str, dict[str, Any]] = self.load_data(data)
        elif isinstance(data, dict):
            self.data = data
        else:
            raise Exception(f"Invalid data format: {type(data)} "
                            "should be Path or dict[str, dict[str, Any]]")
        
        # Currently aggregated data is unsupported.
        # When support is added, this should change to a match statement
        # which feeds the data to different functions based on the aggregation type
        if AggregateBy(self.data["firstAggregateBy"]) != AggregateBy.NONE:
            raise Exception(f"Cannot parse aggregated data, please provide non-aggregated data.")

    def get_grammar(self) -> GrammarModel:
        """
        Parses the grammar data from the JSON export from the UpSet Multinet implementation 
        into a GrammarModel. 
        """
        return self.parse_grammar(self.data)
    
    def get_data(self) -> DataModel:
        """
        Parses the data from the JSON export from the UpSet Multinet implementation 
        into a DataModel. 
        """
        return self.parse_data_no_agg(self.data)

    def load_data(self, file_path: Path) -> "dict[str, dict[str, Any]]":
        """
        Loads a data file into JSON to be parsed. 
        Raises an exception if the file is aggregated.
        """
        with open(file_path) as f:
            return json.load(f)

    def parse_data_no_agg(self, data: "dict[str, dict[str, Any]]") -> DataModel:
        """
        Responsible for parsing non-aggregated data from the JSON export 
        from the UpSet Multinet implementation. Other functions in this
        class should be implemented to parse aggregated data.

        Not all data from the data JSON file is parsed and accessible.
        Current data parsed:
        - set sizes and names
        - set membership of items
        - deviations from expected set membership
        - Information about sets/intersections/aggregations:
          - name
          - size
          - deviation
          - description
        """
        # Dictionary mapping set names to their sizes
        sizes: dict[str, int] = {}
        
        # Dictionary mapping sets/intersections/aggregations to information about them        
        subsets: list[Subset] = []
        for item in data["accessibleProcessedData"]["values"].values():
            # Name of the set/intersection/aggregation- 
            # a list of set names in the case of intersections
            name: str = item.get("elementName", self.default_field)
            # size
            size: int = int(item.get("size", self.default_field))
            # Deviation - rounded to 2 decimals
            dev: float = round(item.get("deviation", self.default_field), 2)
            # Degree
            degree: int = int(item.get("degree", self.default_field))
            subsets.append(Subset(name=name, size=size, dev=dev, degree=degree))

        # List of set names
        sets_: list[str] = []
        for set_ in data["rawData"]["sets"].values():
            set_name: str = set_["elementName"]
            sizes[set_name] = set_["size"]
            
            # Remove the 'Set_' prefix from the set name, if extant- 
            # must be done after prev steps
            if set_name.startswith("Set_"):
                set_name = set_name[4:]
            sets_.append(set_name)

        # List of all members (data points) of the sets
        membs: list[frozenset[str]] = []
        for elem in data["rawData"]["items"].values():
            membership = frozenset(
                [
                    key
                    for key, value in elem.items()
                    if key in data["rawData"]["setColumns"] and value == 1
                ]
            )
            if len(membership):
                membs.append(membership)

        # List of the number of sets each member is in
        count = list(Counter(membs).values())
        membs = list(Counter(membs).keys())
        # Initialize deviations
        data_model = DataModel(
            membs=membs, sets=sets_, sizes=sizes, count=count, subsets=subsets
        )
        return data_model

    def parse_grammar(self, grammar: "dict[str, Any]") -> GrammarModel:
        """
        Parses the state data from the JSON export from the UpSet Multinet implementation 
        into a GrammarModel. 
        """
        # Currently removed as they don't exist in the grammar exports from multinet
        # TODO: Re-add title when it is added to the grammar export. Caption likely won't be
        #caption = grammar["caption"]
        #title = grammar["title"]
        first_aggregate_by = AggregateBy(grammar["firstAggregateBy"])
        second_aggregate_by = AggregateBy(grammar["secondAggregateBy"])

        first_overlap_degree = int(grammar["firstOverlapDegree"])
        second_overlap_degree = int(grammar["secondOverlapDegree"])

        sort_visible_by = SortVisibleBy(grammar["sortVisibleBy"])

        sort_by = SortBy(grammar["sortBy"])

        filters = FilterModel(
            max_visible=grammar["filters"]["maxVisible"],
            min_visible=grammar["filters"]["minVisible"],
            hide_empty=grammar["filters"]["hideEmpty"],
        )

        plots = PlotModel(
            scatterplots=grammar["plots"]["scatterplots"],
            histograms=grammar["plots"]["histograms"],
            wordclouds=grammar["plots"]["wordClouds"],
        )

        collapsed: list[str] = grammar["collapsed"]
        visible_sets: list[str] = grammar["visibleSets"]
        visible_atts: list[str] = grammar["visibleAttributes"]

        bookmarked_intersections = list(
            map(
                lambda bookmarked_intersection: BookmarkedIntersectionModel(
                    **bookmarked_intersection
                ),
                grammar["bookmarkedIntersections"],
            )
        )

        # Remove the 'Set_' prefix from each visible set name, if extant
        for i in range(len(visible_sets)):
            if visible_sets[i].startswith("Set_"):
                visible_sets[i] = visible_sets[i][4:]

        grammar_model = GrammarModel(
            first_aggregate_by=first_aggregate_by,
            second_aggregate_by=second_aggregate_by,
            first_overlap_degree=first_overlap_degree,
            second_overlap_degree=second_overlap_degree,
            sort_visible_by=sort_visible_by,
            sort_by=sort_by,
            filters=filters,
            collapsed=collapsed,
            visible_sets=visible_sets,
            visible_atts=visible_atts,
            plots=plots,
            bookmarked_intersections=bookmarked_intersections,
        )

        return grammar_model