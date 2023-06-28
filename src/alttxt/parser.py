import json
from pprint import pprint

from alttxt.types import AggregateBy
from alttxt.types import SortBy
from alttxt.types import SortVisibleBy
from alttxt.types import ParseType

from alttxt.models import BookmarkedIntersectionModel
from alttxt.models import DataModel
from alttxt.models import FilterModel
from alttxt.models import GrammarModel
from alttxt.models import PlotModel

from pathlib import Path
from collections import Counter
from typing import Any


Model = DataModel | GrammarModel


class Parser:
    """
    Handles parsing of data files into objects.
    """
    def __init__(self, file_path: Path, ptype: ParseType) -> None:
        # Default message for when a field cannot be found by the parser
        self.default_field = "(field not available)"
        
        # Now load the file and parse the data
        self.data = self.load_file(file_path, ptype)

    def load_file(self, file_path: Path, ptype: ParseType) -> Model:
        """
        Parses a data file into a DataModel and GrammarModel. The data file must be
        a JSON export from Multinet containing both state and data.
        """
        with open(file_path) as f:
            data = json.load(f)
            # Currently aggregated data is unsupported.
            # When support is added, this should change to a match statement
            # which feeds the data to different functions based on the aggregation type
            if AggregateBy(data["firstAggregateBy"]) != AggregateBy.NONE:
                raise Exception(f"Cannot parse aggregated data from file '{file_path}', please provide non-aggregated data.")
            
            if ptype == ParseType.DATA:
                return self.parse_data_no_agg(data)
            elif ptype == ParseType.GRAMMAR:
                return self.parse_grammar(data)

    def query_devs(
        self,
        membs: list[frozenset[str]],
        count: list[int],
        sets: list[str],
        sizes: dict[str, int],
    ) -> list[float]:
        """
        Computes the `disproportionality` w.r.t. expected `count`.
        Assumes marginal independence of the sets. Weakly adapted
        from Lex et al `UpSet: Visualizing Intersecting Sets`.
        """
        devs = [0.0] * len(membs)
        nval = sum(count)
        for i, membership in enumerate(membs):
            devs[i] = count[i] / nval
            residue = 1.0
            for set_ in membership:
                residue *= sizes[set_] / nval
            for set_ in filter(lambda set_: set_ not in membership, sets):
                residue *= 1 - sizes[set_] / nval
            devs[i] -= residue
        devs = list(map(lambda dev: round(100 * dev, 1), devs))
        return devs

    def parse_data_no_agg(self, data: dict[str, dict[str, Any]]) -> Model:
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
        subsets: list[dict[str, Any]] = []
        for item in data["processedData"]["values"].values():
            info = dict()
            # Name of the set/intersection/aggregation- a list of set names in the case of intersections
            info["name"] = item.get("elementName", self.default_field)
            # Cardinality
            info["card"] = item.get("size", self.default_field)
            # Deviation
            info["dev"] = item.get("deviation", self.default_field)
            # Degree. This will be replaced when degree is added to the JSON export
            # Current implementation is bugged if set names include spaces,
            # but it's the only way to get set degree until added to the JSON
            if info["name"] == self.default_field:
                info["degree"] = None
            else:
                info["degree"] = info["name"].count(" ") + 1
            subsets.append(info)

        # List of set names
        sets_: list[str] = []
        for set_ in data["rawData"]["sets"].values():
            set_name = set_["elementName"]
            sizes[set_name] = set_["size"]
            sets_.append(set_name)

        # List of all members (data points) of the sets
        membs = []
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
        devs = self.query_devs(membs, count, sets_, sizes)
        data_model = DataModel(
            membs=membs, sets=sets_, sizes=sizes, count=count, devs=devs, subsets=subsets
        )
        return data_model

    def parse_grammar(self, grammar: dict[str, Any]) -> Model:
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