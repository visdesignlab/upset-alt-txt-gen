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
    # L2 splits generation by sort- verbosity is TBA
    "level_2": {
        "low": {
            SortBy.CARDINALITY: "",
            SortBy.DEGREE: "",
            SortBy.DEVIATION: "",
            },
        "medium": {
                SortBy.CARDINALITY: "[[InUpSet]], [[sort_set_info]]. [[largest_10_int]]. [[card_percs]].",
                SortBy.DEGREE: "[[InUpSet]], [[sort_set_info]]. [[degree_info]].",
                SortBy.DEVIATION: "[[InUpSet]], [[sort_set_info]]. [[deviation_info]]",
            },
        "high": "[[InUpSet]], [[sort_set_info]]. [[largest_10_int]]. [[card_percs]]. [[degree_info]]. [[deviation_info]]",
        
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
    # L3 note: observe which sets are not present in many large intersections
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
        "of an intersection is given the size of its constituent sets. The remaining {{var_count}} columns "
        "show the average and quartiles of each variable from the dataset",
        # Title, caption, set list
        "l1_low_desc": "[[title]]. [[set_list]]",
        # Number of non-empty intersections, max/min intersection size, and universal set size
        "l1_med_desc": "[[pop_intersections]]. [[max_min]], and [[universal_set_size]]",
        # Sort order and variable list
        "l1_high_desc": "[[sort_by]]. [[list_vars]]",
        # Title and caption
        "title": "this UpSet plot is titled {{title}}",
        # Count and list set names
        "set_list": "{{set_count}} sets are displayed- their names and sizes are: {{list_set_sizes}}",
        # Number of non-empty intersections
        "pop_intersections": "{{pop_intersect_count}} non-empty set intersections are visualized",
        # Set intersection size range
        "max_min": "set intersections range in size from {{min_size}} to {{max_size}}",
        # Total number of items in all sets
        "universal_set_size": "a total of {{universal_set_size}} items are represented in all sets",
        # Intersections are sorted by
        "sort_by": "intersections are sorted by {{sort_type}}",
        # Number of visualized variables and their names
        "list_vars": "{{var_count}} variables are visualized- {{list_var_names}}",
        # Number of sets, non-empty intersections, and sort type
        "sort_set_info": "{{set_count}} sets are visualized, with {{pop_intersect_count}} non-empty intersections, "
        "sorted by {{sort_type}}. Set names and sizes are: {{list_set_sizes}}",
        # Largest 10 intersections and 10th percentile of intersections
        "largest_10_int": "the largest 10 intersections are {{list_max_10int}}",
        # Average and 10th, 25th, 75th, and 90th percentile cardinalities
        "card_percs": "the average cardinality is {{avg_card}}, with a 10th percentile of {{10perc_card}}, "
        "25th percentile of {{25perc_card}}, 75th percentile of {{75perc_card}}, "
        "and 90th percentile of {{90perc_card}}",
        # Degree info list,
        "degree_info": "number of intersections of each degree, their average cardinality, "
        "and their average deviation are as follows: {{list_degree_info}}",
        # Deviation info, split by positive and negative deviations
        "deviation_info": "{{pos_dev_count}} intersections have a positive deviation, with a total "
        "cardinality of {{pos_dev_card}}. {{neg_dev_count}} have a "
        "negative deviation, with a total cardinality of {{neg_dev_card}}. "
        "The average positive deviation is {{avg_pos_dev}}, and the average "
        "negative deviation is {{avg_neg_dev}}",

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
