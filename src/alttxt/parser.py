import json


from alttxt.enums import AggregateBy, SortBy, SortVisibleBy, SortOrder, IntersectionType
from alttxt.models import (
    BookmarkedIntersectionModel,
    Subset,
    DataModel,
    FilterModel,
    GrammarModel,
    PlotModel,
    MetaDataModel,
)

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
            raise Exception(
                f"Invalid data format: {type(data)} "
                "should be Path or dict[str, dict[str, Any]]"
            )

        # Currently aggregated data is unsupported.
        # When support is added, this should change to a match statement
        # which feeds the data to different functions based on the aggregation type
        if AggregateBy(self.data["firstAggregateBy"]) != AggregateBy.NONE:
            raise Exception(
                f"Cannot parse aggregated data, please provide non-aggregated data."
            )

    def trim_set_name(self, set_name: str) -> str:
        """
        Trims the set name to remove the 'Set_' prefix, if it exists.
        """
        return set_name[4:] if set_name.startswith("Set_") else set_name

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
        
    def classify_subset(self, degree: int, num_individual_sets: int) -> IntersectionType:
        """
        Classifies a subset based on its degree and the number of individual sets.
        """
        if degree == 1:
            return IntersectionType.INDIVIDUAL
        if degree == 0:
            return IntersectionType.EMPTY
        if degree == num_individual_sets:
            return IntersectionType.HIGHORDER_SET
        
        if num_individual_sets == 3:
            if degree == 2:
                return IntersectionType.MEDIUM_SET
               
        elif num_individual_sets == 4:
            if degree == 2:
                return IntersectionType.LOW_SET
            elif degree == 3:
                return IntersectionType.MEDIUM_SET
            
        elif num_individual_sets == 5:
            if degree == 2:
                return IntersectionType.LOW_SET
            elif degree == 3:
                return IntersectionType.MEDIUM_SET
            elif degree == 4:
                return IntersectionType.HIGHORDER_SET
        
        elif num_individual_sets == 6:
            if degree == 2:
                return IntersectionType.LOW_SET
            elif degree == 3:
                return IntersectionType.MEDIUM_SET
            elif degree == 4:
                return IntersectionType.MEDIUM_SET
            elif degree == 5:
                return IntersectionType.HIGHORDER_SET
        
        else:
            if 2 <= degree <= 3:
                return IntersectionType.LOW_SET
            elif 4 <= degree <= (num_individual_sets // 2):
                return IntersectionType.MEDIUM_SET
            else:
                return IntersectionType.HIGHORDER_SET
    
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
        data_visible_subsets = data["accessibleProcessedData"]["values"]
        for item in data_visible_subsets.values():
            # Name of the set/intersection/aggregation-
            # a list of set names in the case of intersections
            name: str = item.get("elementName", self.default_field)
            if name.lower() == "unincluded":
                name = "the empty intersection"
            else:
            # Replace underscores with hyphens if underscores are present
                name = name.replace('_', '-') if '_' in name else name
            
            # size
            size: int = int(item.get("size", self.default_field))
            # Deviation - rounded to 2 decimals
            # Backwards compatibility (<v0.2.7)
            try:
                dev: float = round(item.get("attributes", self.default_field)["deviation"], 2)
            except KeyError:
                dev: float = round(item.get("deviation", self.default_field), 2)

            # Degree
            degree: int = int(item.get("degree", self.default_field))
            # Classification
            classification = self.classify_subset(degree, len(data["visibleSets"]))

            # Process setMembership to store only the names of sets with "Yes" membership
            setMembership = {self.trim_set_name(key): value for key, value in item.get("setMembership", {}).items() if value == "Yes"}

            # Only store the keys (set names) that have "Yes" as their value
            yes_sets = {key.replace('_','-') for key, value in setMembership.items() if value == "Yes"}

            subsets.append(Subset(name=name, size=size, dev=dev, degree=degree, classification=classification, setMembership=yes_sets))

        lowercase_data_visible_subsets = {k.lower(): k for k in data_visible_subsets.keys()}

        all_subsets: list[Subset] = []
        data_all_subsets = data["processedData"]["values"]
        count: list[int] = []
        for key, item in data_all_subsets.items():

            # Convert key to lowercase for case-insensitive comparison
            lower_key = key.lower()

            if lower_key in lowercase_data_visible_subsets:
                # Use the original case key from the visible subsets
                original_key = lowercase_data_visible_subsets[lower_key]
                item["elementName"] = data_visible_subsets[original_key]["elementName"]
            # Name of the set/intersection/aggregation-
            # a list of set names in the case of intersections
            name: str = item.get("elementName", self.default_field)
            if name.lower() == "unincluded":
                name = "the empty intersection"
            # size
            size: int = int(item.get("size", self.default_field))
            # Deviation - rounded to 2 decimals
            # Backwards compatibility (<v0.2.7)
            try:
                dev: float = round(item.get("attributes", self.default_field)["deviation"], 2)
            except KeyError:
                dev: float = round(item.get("deviation", self.default_field), 2)

            # Degree - the degree might not be available in the raw data, handle accordingly
            degree: int = item.get("degree")
            if degree is not None:
                degree = int(degree)
            else:
                degree = 0  # or some default value

            all_sets_length = len(data["allSets"])

            classification = self.classify_subset(degree, all_sets_length)

            setMembership = {self.trim_set_name(key): value for key, value in item.get("setMembership", {}).items() if value == "Yes"}
        
            # Only store the keys (set names) that have "Yes" as their value
            yes_sets = {key for key, value in setMembership.items() if value == "Yes"}
            
            count.append(size)
            all_subsets.append(Subset(name=name, size=size, dev=dev, degree=degree, classification=classification, setMembership=yes_sets))

        # List of set names
        sets_: list[str] = []
        for set_ in data["allSets"]:
            set_name: str = set_["name"]
            sizes[set_name] = set_["size"]

        #     # Remove the 'Set_' prefix from the set name, if extant-
        #     # must be done after prev steps
            set_name = self.trim_set_name(set_name)
            sets_.append(set_name.replace('_', '-'))

        
        # Initialize deviations
        data_model = DataModel(sets=sets_, sizes=sizes, count=count, subsets=subsets, all_subsets=all_subsets, all_sets_length=all_sets_length)
    
        return data_model

    def parse_grammar(self, grammar: "dict[str, Any]") -> GrammarModel:
        """
        Parses the state data from the JSON export from the UpSet Multinet implementation
        into a GrammarModel.
        The grammar param must be a state + data export, not just the state export.
        """
        # Currently removed as they don't exist in the grammar exports from multinet
        # TODO: Re-add title when it is added to the grammar export. Caption likely won't be
        # caption = grammar["caption"]
        # title = grammar["title"]

        # Dictionary mapping visible set names to their sizes
        visible_set_sizes: dict[str, int] = {}

        first_aggregate_by = AggregateBy(grammar["firstAggregateBy"])
        second_aggregate_by = AggregateBy(grammar["secondAggregateBy"])

        first_overlap_degree = int(grammar["firstOverlapDegree"])
        second_overlap_degree = int(grammar["secondOverlapDegree"])

        sort_visible_by = SortVisibleBy(grammar["sortVisibleBy"])

        sort_by = SortBy(grammar["sortBy"].lower())

        sort_order = SortOrder(grammar["sortByOrder"].lower())

        filters = FilterModel(
            max_visible=grammar["filters"]["maxVisible"],
            min_visible=grammar["filters"]["minVisible"],
            hide_empty=grammar["filters"]["hideEmpty"],
            hide_no_set=grammar["filters"]["hideNoSet"],
        )

        plots = PlotModel(
            scatterplots=grammar["plots"]["scatterplots"],
            histograms=grammar["plots"]["histograms"],
        )

        if "plotInformation" in grammar:
            metaData = MetaDataModel(
                description=grammar["plotInformation"]["description"],
                sets=grammar["plotInformation"]["sets"],
                items=grammar["plotInformation"]["items"],
            )
        else:
            metaData = MetaDataModel(
                description="",
                sets="",
                items="",
            )

        collapsed: list[str] = grammar["collapsed"]
        visible_sets: list[str] = grammar["visibleSets"]
        all_set_names: list[str] = list(map(lambda x: x["name"], grammar["allSets"]))
        visible_atts: list[str] = grammar["visibleAttributes"]

        # Iterate through the visible sets
        for set_name in visible_sets:
            # Check if the set name exists in the data dictionary
            if set_name in all_set_names:
                # Add the set name and its size to the dictionary
                # Remove the 'Set_' prefix from the set name, if extant
                # visible_set_sizes expects "Thriller", rather than "Set_Thriller"
                name = self.trim_set_name(set_name)

                visible_set_sizes[name] = grammar["allSets"][all_set_names.index(set_name)]["size"]
            else:
                # If the set name is not found, you can choose to handle it as you see fit
                print(f"Warning: Set {set_name} not found in data")

        def convert_intersection(id: str) -> BookmarkedIntersectionModel:
            """
            Converts an intersection from the grammar data into a BookmarkedIntersectionModel.
            """
            intersection = grammar['processedData']['values'].get(str(id), {})
            atts = list(filter(lambda a: a != 'deviation', list(intersection['attributes'].keys())))
            att_means = []
            for att in atts:
                att_means.append(
                    intersection['attributes'][att].get('mean', 0.0)
                )
            return BookmarkedIntersectionModel(
                atts=atts,
                att_means=att_means,
                id=id,
                label=intersection.get('elementName', self.default_field),
                size=intersection.get('size', 0),
            )
                

        bookmarked_intersections = list(
            map(
                convert_intersection,
                # Backwards compatibility (<v0.2.8)
                # if bookmarks is not present, use bookmarkedIntersections
                # this may introduce some issues with using bookmarks
                # if removed, this is a breaking change for API calls, and so should likely be moved into a major version
                map(lambda b: b.get('id', None), grammar.get("bookmarks", grammar.get("bookmarkedIntersections", [])))
            )
        )

        selected_intersection = convert_intersection(
            grammar.get('rowSelection').get('id', None) 
          ) if grammar.get('rowSelection') else None

        # Remove the 'Set_' prefix from each visible set name, if extant
        for i in range(len(visible_sets)):
            visible_sets[i] = self.trim_set_name(visible_sets[i])
        
        set_query = grammar.get("setQuery", None)
        if set_query:
            set_query = {
                "name": set_query["name"],
                "query": {
                    self.trim_set_name(key): value for key, value in set_query["query"].items()
                }
            }

        grammar_model = GrammarModel(
            first_aggregate_by=first_aggregate_by,
            second_aggregate_by=second_aggregate_by,
            first_overlap_degree=first_overlap_degree,
            second_overlap_degree=second_overlap_degree,
            sort_visible_by=sort_visible_by,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters,
            collapsed=collapsed,
            visible_sets=visible_sets,
            visible_atts=visible_atts,
            visible_set_sizes=visible_set_sizes,
            plots=plots,
            metaData=metaData,
            bookmarked_intersections=bookmarked_intersections,
            selected_intersection=selected_intersection,
            selection_type=grammar.get("selectionType", None),
            set_query=set_query,
        )

        return grammar_model
