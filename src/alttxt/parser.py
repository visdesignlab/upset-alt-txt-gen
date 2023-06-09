import json
from pprint import pprint

from alttxt.types import AggregateBy, SortBy, SortVisibleBy
from alttxt.models import BookmarkedIntersectionModel, Subset, DataModel, FilterModel, GrammarModel, PlotModel

from pathlib import Path
from collections import Counter
from typing import Any

class Parser:
    """
    Handles parsing of data files into objects.
    """
    def __init__(self, file_path: Path) -> None:
        # Default message for when a field cannot be found by the parser
        self.default_field = "(field not available)"
        
        # Now load the file and parse the data
        self.data: dict[str, dict[str, Any]] = self.load_data(file_path)

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

    def load_data(self, file_path: Path) -> dict[str, dict[str, Any]]:
        """
        Loads a data file into JSON to be parsed. 
        Raises an exception if the file is aggregated.
        """
        with open(file_path) as f:
            data: dict[str, dict[str, Any]] = json.load(f)
            # Currently aggregated data is unsupported.
            # When support is added, this should change to a match statement
            # which feeds the data to different functions based on the aggregation type
            if AggregateBy(data["firstAggregateBy"]) != AggregateBy.NONE:
                raise Exception(f"Cannot parse aggregated data from file '{file_path}', please provide non-aggregated data.")
            
            return data

    def parse_data_no_agg(self, data: dict[str, dict[str, Any]]) -> DataModel:
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
          - cardinality
          - deviation
          - description
        """
        # Dictionary mapping set names to their sizes
        sizes: dict[str, int] = {}
        
        # Dictionary mapping sets/intersections/aggregations to information about them        
        subsets: list[Subset] = []
        for item in data["processedData"]["values"].values():
            # Name of the set/intersection/aggregation- a list of set names in the case of intersections
            name = item.get("elementName", self.default_field)
            # Cardinality
            size = item.get("size", self.default_field)
            # Deviation - rounded to 2 decimals
            dev = round(item.get("deviation", self.default_field), 2)
            # Degree. This will be replaced when degree is added to the JSON export
            # Current implementation is bugged if set names include spaces,
            # but it's the only way to get set degree until added to the JSON
            if name == self.default_field:
                degree = -1
            else:
                degree = name.count(" ") + 1
            subsets.append(Subset(name=name, size=size, dev=dev, degree=degree))

        # List of set names
        sets_: list[str] = []
        for set_ in data["rawData"]["sets"].values():
            set_name: str = set_["elementName"]
            sizes[set_name] = set_["size"]
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

    def parse_grammar(self, grammar: dict[str, Any]) -> GrammarModel:
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

        collapsed = grammar["collapsed"]
        visible_sets = grammar["visibleSets"]
        visible_atts = grammar["visibleAttributes"]

        bookmarked_intersections = list(
            map(
                lambda bookmarked_intersection: BookmarkedIntersectionModel(
                    **bookmarked_intersection
                ),
                grammar["bookmarkedIntersections"],
            )
        )

        grammar_model = GrammarModel(
            #caption=caption,
            #title=title,
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