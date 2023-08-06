from alttxt.enums import SortBy, Explanation
from typing import Any

"""
The context-free grammar which the alt text is generated from-
not to be confused with the JSON export of the data, which is
also referred to as a grammar.

Syntax:
The "level_x" keys denote the semantic level of the contained descriptions.
Within the level keys, the "low", "medium", and "high" keys denote the verbosity, 
AKA verbosity, of the contained grammar. These level/verbosity combinations
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
DESCRIPTIONS: "dict[str, Any]" = {
    # Various levels of "explain upset"
    "upset_desc": {
        Explanation.NONE: "",
        Explanation.SIMPLE: "[[UpSet]]. [[learn_more]]. ",
        Explanation.FULL: "[[UpSet]], a data visualization that uses a matrix "
        "to display the size of intersecting sets, similar to a venn diagram. "
        "The rows of the matrix represent set intersections. "
        "The columns of the matrix correspond to sets. "
        "The intersecting sets in a particular row are indicated by whether "
        "the cell corresponding to a set is filled in. For example, "
        "for three sets A, B, and C, the row corresponding to "
        "the intersection of A and C has A and C filled in. "
        "Next to each row is a horizontal bar that visualizes the size of the intersection. [[learn_more]]. ",
    },
    "level_1": {
        "low": "[[l1_low_desc]].",
        "medium": "[[l1_low_desc]][[l1_med_desc]].",
        "high": "[[l1_low_desc]][[l1_med_desc]]. [[l1_high_desc]].",
    },
    # L2 splits generation by sort- verbosity is TBA
    "level_2": {
        "low": {
            SortBy.SIZE: "The largest 5 intersections, with their respective sizes and deviations, "
            "are {{list_max_5int}}. [[size_percs]].",
            SortBy.DEGREE: "There are {{list_degree_count}}.",
            SortBy.DEVIATION: "[[deviation_info]].",
            },
        "medium": {
                SortBy.SIZE: "The largest 10 intersections, with their respective sizes and deviations, "
                "are {{list_max_10int}}. [[size_percs]].",
                SortBy.DEGREE: "[[degree_info]].",
                SortBy.DEVIATION: "[[deviation_info]]. The largest 5 absolute deviations are {{list5_dev_outliers}}.",
            },
        "high": {
                SortBy.SIZE: "In order of size, the intersections (with their respective sizes and deviations) "
                "are: {{list_all_int}}. [[size_percs]].",
                SortBy.DEGREE: "[[degree_info]].",
                SortBy.DEVIATION: "[[deviation_info]]. The largest 10 absolute deviations are {{list10_dev_outliers}}.",
        },    
    # L3 note: observe which sets are not present in many large intersections
    },
    # These are all of the non-terminal symbols that are used in the grammar
    "symbols": {
        # "This is an UpSet plot"
        "UpSet": "this is an UpSet plot",
        # Another title for an UpSet plot
        "InUpSet": "in this UpSet plot",
        # Learn more about UpSet
        "learn_more": "to learn about UpSet plots, visit upset.app",
        # Title, caption, set list
        "l1_low_desc": "[[title]]. The dataset contains {{set_count}} total sets, "
        "with {{universal_set_size}} elements. {{visible_set_count}} sets are shown in the plot",
        # Number of non-empty intersections, max/min intersection size, and universal set size
        "l1_med_desc": ": {{list_visible_set_names}}. [[pop_intersections]]",
        # Sort order and variable list
        "l1_high_desc": "[[max_min]]. [[sort_by]]. [[set_names_sizes]].",
        # Title and caption
        "title": "this UpSet plot {{title}}",
        # Count and list set names
        "set_list": "{{visible_set_count}} sets are displayed- their names and sizes are: {{list_set_sizes}}",
        # Number of non-empty intersections
        "pop_intersections": "{{pop_intersect_count}} non-empty intersections are shown",
        # Set intersection size range
        "max_min": "set intersections range in size from {{min_size}} to {{max_size}}",
        # Total number of items in all sets
        "universal_set_size": "a total of {{universal_set_size}} items are represented in all sets",
        # Intersections are sorted by
        "sort_by": "intersections are sorted by {{sort_type}}",
        # Number of visualized variables and their names
        "list_vars": "{{var_count}} variables are visualized- {{list_var_names}}",
        # Number of sets, non-empty intersections, and sort type
        "sort_set_info": "{{visible_set_count}} sets are displayed out of {{set_count}} total, "
        "with {{pop_intersect_count}} non-empty intersections, "
        "sorted by {{sort_type}}",
        # Number of sets and their sizes
        "set_names_sizes": "set names and sizes are: {{list_set_sizes}}",
        # Largest 10 intersections and 10th percentile of intersections
        "largest_10_int": "the largest 10 intersections are {{list_max_10int}}",
        # Average and 10th, 25th, 75th, and 90th percentile sizeinalities
        "size_percs": "the average intersection size is {{avg_size}}. "
        "The 90th percentile is {{90perc_size}}, and the 10th percentile is {{10perc_size}}",
        # Degree info list,
        "degree_info": "number of intersections of each degree, their average size, "
        "and their average deviation are as follows: {{list_degree_info}}",
        # Deviation info, split by positive and negative deviations
        "deviation_info": "{{pos_dev_count}} intersections have a positive deviation, with a total "
        "size of {{pos_dev_size}}. {{neg_dev_count}} have a "
        "negative deviation, with a total size of {{neg_dev_size}}. "
        "The average positive deviation is {{avg_pos_dev}}, and the average "
        "negative deviation is {{avg_neg_dev}}",
    },
}
