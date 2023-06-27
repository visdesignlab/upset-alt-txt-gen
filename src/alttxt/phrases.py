from alttxt.types import AggregateBy
from alttxt.types import SortBy

"""
The context-free grammar which the alt text is generated from-
not to be confused with the JSON export of the data, which is
also referred to as a grammar.

Syntax:
The "level_x" keys denote the semantic level of the contained descriptions.
Within the level keys, the "low", "medium", and "high" keys denote the granularity, 
AKA verbosity, of the contained grammar. These level/granularity combinations
are used as start symbols, with the specific combination being chosen by command-line args.
Each starting phrase contains a variety of symbols. Terminal symbols are enclosed in {{}}.
Non-terminal symbols are enclosed in [[]]. Terminal symbols are evaluated by the TokenMap
class, which has to perform some computation to get the value of the token. Non-terminal
are evaluated by the grammar itself, and mappings for non-terminals are defined in the 
"symbols" key within the grammar, which is itself a dict. Note that non-terminals can 
technically be terminal, as long as their mapping doesn't contain any values that need
to be computed by the TokenMap. Note that when feeding symbols to both the TokenMap 
and the grammar, the symbols must be stripped of their enclosing brackets.
"""
DESCRIPTIONS = {
    "level_0": {
        "low": "[[l0_low_desc]].",
        "medium": "[[l0_low_desc]]. [[l0_med_desc]].",
        "high": "[[l0_low_desc]]. [[l0_med_desc]]. [[l0_high_desc]].",
    },
    "level_1": {
        "low": "[[l1_low_desc]].",
        "medium": "[[l1_low_desc]]. [[l1_med_desc]].",
        "high": "[[l1_low_desc]]. [[l1_med_desc]]. [[l1_high_desc]]",
    },
    # L2 splits generation by sort and aggregation
    # The phrases are designed so that the aggregation can be appended to the sort
    "level_2": {
        "sort": {
            SortBy.CARDINALITY: "[[InUpSet]], [[sort_set_info]]. [[int_max_min_set]]. "
            "The average cardinality is {{avg_card}}, with a 25th percentile of "
            "{{25perc_card}} and a 75th percentile of {{75perc_card}}. ",
            SortBy.DEGREE: "[[InUpSet]], [[sort_set_info]]. There are {{list_degree_info}}. ",
            SortBy.DEVIATION: "[[InUpSet]], [[sort_set_info]]. There are {{list_deviation_info}}. ",
        },
        # Aggregation info is on hold for the summer. I initially created these to describe aggregations,
        # but since only the multinet UpSet implementation supports aggregations, these are currently unused.
        # Note that the current Parser.py implementation only supports parsing non-aggregated JSON. The format
        # of the processedData field in the JSON changes when aggregation is introduced, so the parser also
        # needs to be updated when these are re-added.
        "aggregation": {
            AggregateBy.SETS: "intersections are aggregated by set. "
            "There are {{list_set_info}}.",
            AggregateBy.DEGREE: "intersections are aggregated by degree. "
            "There are {{list_degree_info}}.",
            AggregateBy.DEVIATION: "intersections are aggregated by deviation. "
            "{{count_pos_dev}} have a positive deviation, with a total "
            "cardinality of {{pos_dev_card}}. {{count_neg_dev}} have a "
            "negative deviation, with a total cardinality of {{neg_dev_card}}. "
            "The aggregation of positive deviations has an overall deviation of "
            "{{pos_dev_dev}}, while the aggregation of negative deviations "
            "has an overall deviation of {{neg_dev_dev}}.",
            AggregateBy.OVERLAP: "intersections are aggregated by overlaps of degree {{agg_degree}}. "
            "There are {{list_overlap_info}}",
            AggregateBy.NONE: "intersections are not aggregated. There are {{list_set_info}}.",
        },
    },
    "symbols": {
        # "This is an UpSet plot"
        "UpSet": "this is an UpSet plot",
        # Another title for an UpSet plot
        "InUpSet": "in this UpSet plot",
        # Basic description of an UpSet plot
        "l0_low_desc": "[[UpSet]], a data visualization tool "
        "which uses a matrix to display the mathematical properties of intersecting sets",
        # Explanation of rows, columns, and matrix entries
        "l0_med_desc": "the rows of the matrix represent sets or set intersections. "
        "The columns of the matrix are properties of intersections and variables in the dataset. "
        "Each entry in the matrix shows a property of the corresponding set intersection, or "
        "the distribution of a certain variable from the dataset in the corresponding intersection",
        # Column descriptions
        "l0_high_desc": "the first column shows which set intersection is visualized in that row. "
        "The second column shows the cardinality of each intersection. The third column shows "
        "the deviation of each set intersection, which represents how unexpected the cardinality "
        "of an intersection is given the size of its constituent sets. The remaining {{col_count}} columns "
        "show the average and quartiles of each variable from the dataset",
        # Title, caption, set list
        "l1_low_desc": "[[title_capt]]. [[set_list]]",
        # Number of non-empty intersections, max/min intersection size, and universal set size
        "l1_med_desc": "[[pop_intersections]]. [[max_min]], and [[universal_set_size]]",
        # Sort order and variable list
        "l1_high_desc": "[[sort_by]]. [[list_vars]]",
        # Title and caption
        "title_capt": "this UpSet plot is titled {{title}} and captioned {{caption}}",
        # Count and list set names
        "set_list": "{{set_count}} sets are displayed- {{list_set_names}}",
        # Number of non-empty intersections
        "pop_intersections": "{{pop_intersect_count}} non-empty set intersections are visualized",
        # Set intersection size range
        "max_min": "set intersections range in size from {{min_size}} to {{max_size}}",
        # Total number of items in all sets
        "universal_set_size": "a total of {{universal_set_size}} items are represented in all sets",
        # Intersections are sorted by
        "sort_by": "intersections are sorted by {{sort}}",
        # Number of visualized variables and their names
        "list_vars": "{{var_count}} variables are visualized- {{list_var_names}}",
        # Number of sets, non-empty intersections, and sort type
        "sort_set_info": "{{set_count}} sets are visualized, with {{pop_intersect_count}} non-empty intersections, "
        "sorted by {{sort_type}}",
        # Largest 10 intersections and 10th percentile of intersections
        "int_max_min_set": "the largest 10 intersections are {{list_max_10int}}. "
        "The 90th percentile for cardinality is {{90perc_card}}, and the 10th percentile "
        "is {{10perc_card}}. ",

        ## Artifacts from Filemon- unused currently but may be re-added ##
        # Listing the biggest and smallest sets
        "multi_max_min_card": "set membership comprised of {{list_max_membership}} "
        "have the highest total cardinality, totaling {{max_perc}} of these. "
        "In contrast, set membership consisting of {{list_min_membership}} "
        "has the lowest cardinality, amounting barely {{min_perc}} of all memberships",
        # Max and min singleton set
        "max_min_card": "the singleton set comprised of {{list_max_set_name}} has "
        "the highest cardinality, totaling {{max_set_perc}} of the entire dataset. "
        "However, the singleton set comprised of {{list_min_set_name}} "
        "has the lowest cardinality, amounting only {{min_set_perc}} of the dataset",
    },
}
