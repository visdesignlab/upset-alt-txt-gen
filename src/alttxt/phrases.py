from alttxt.enums import SortBy, Explanation, SortOrder, SortVisibleBy
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
    "level_1": {
        "technical_description": "[[UpSet]]. [[learn_more]].",
        "upset_introduction": "[[short_description]]",
        "dataset_properties": "[[l1_desc]].",
    },
    # L2 splits generation by sort- verbosity is TBA
    "level_2": {
        "set_description": "[[set_divergence]] [[set_description]].",
        "intersection_description": "[[sort_by]]. {{pop_non-empty_intersections}}."
        " {{list_max_5int}}.",
        "statistical_information": "[[size_percs]]. [[maxmin_set_percentages_info]].",
    },
    "level_3": {
        "trend_analysis": "[[intersection_trend_change]][[factor_analysis]][[categorization_of_subsets]]",

    }, # L3 note: observe which sets are not present in many large intersections
    "AltText": "[[short_description]]",
    # These are all of the non-terminal symbols that are used in the grammar
    "symbols": {
        # "This is an UpSet plot"
        "UpSet": "This is an UpSet plot that visualizes set intersections",
        # Another title for an UpSet plot
        "InUpSet": "in this UpSet plot",
        # Learn more about UpSet plots
        "learn_more": "To learn about UpSet plots, visit https://upset.app",
        # Dataset properties
        "l1_desc": "{{dataset_description}}The dataset contains {{set_count}} sets and {{universal_set_size}} elements,"
        " of which {{visible_set_count}} sets are shown in the plot",
        # Set Properties
        "set_description": "The largest set is {{max_set_name}} with {{max_set_size}} {{set_description}}"
        ", followed by {{list_sorted_visible_sets}}",
        # Set Diversion Calculation
        "set_divergence": "The set sizes are {{set_divergence}}, ranging from {{min_set_size}} to {{max_set_size}}.",
        # Intersection Trend Analysis
        "intersection_trend_change": "{{intersection_trend_analysis}}",
        # Largest Set Factor Analysis
        "factor_analysis": "{{largest_factor}}",
        # Categorization of Subsets in Different Trends
        "categorization_of_subsets": "{{empty_set_presence}}{{all_set_presence}}{{individual_set_presence}}{{low_set_presence}}{{medium_set_presence}}{{high_set_presence}}",
        # Title, caption, set list
        "l1_low_desc": "[[title]]. The dataset contains {{set_count}} total sets, "
        "with {{universal_set_size}} elements. {{visible_set_count}} sets are shown in the plot",
        # Number of non-empty intersections, max/min intersection size, and universal set size
        "l1_med_desc": ": {{list_visible_set_names}}. [[pop_intersections]]",
        # Sort order and variable list
        "l1_high_desc": "[[max_min]]. [[sort_by]]. [[set_names_sizes]]",
        # Title and caption
        "title": "this UpSet plot {{title}}",
        # Count and list set names
        "set_list": "{{visible_set_count}} sets are displayed- their names and sizes are: {{list_set_sizes}}",
        # Set intersection size range
        "max_min": "set intersections range in size from {{min_size}} to {{max_size}}",
        # Total number of items in all sets
        "universal_set_size": "a total of {{universal_set_size}} items are represented in all sets",
        # Intersections are sorted by
        "sort_by": "The plot is sorted by {{sort_type}} in {{sort_order}} order",
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
        "size_percs": "The average intersection size is {{avg_size}}, and the median is {{median_size}}. "
        "The 90th percentile is {{90perc_size}}, and the 10th percentile is {{10perc_size}}",
        # Degree info list,
        "degree_info": "number of intersections of each degree and their average size "
        "are as follows: {{list_degree_info}}",
        # Degree info list, with total size
        "degree_info_verbose": "number of intersections of each degree, their average size, "
        "their average deviation, and their total size are as follows: {{list_degree_info_verbose}}",
        # Deviation info, split by positive and negative deviations
        "deviation_info": "{{pos_dev_count}} intersections have a positive deviation, with a total "
        "size of {{pos_dev_size}}. {{neg_dev_count}} have a "
        "negative deviation, with a total size of {{neg_dev_size}}. "
        "The average positive deviation is {{avg_pos_dev}}, and the average "
        "negative deviation is {{avg_neg_dev}}",
        "maxmin_set_percentages_info": "The largest set, {{max_set_name}}, is present in {{max_set_percentage}} of all non-empty intersections."
        " The smallest set, {{min_set_name}}, is present in {{min_set_percentage}} of all non-empty intersections",
        "short_description": "This is an UpSet plot that shows the intersections of {{visible_set_count}} sets."
        " [[learn_more]]."
        "{{highest_dominant_set}}"
        " {{largest_intersections}}."
        "{{two_set_intersection}}"
        "{{other_large_intersections}}"
        " {{all_set_index}}",
    },
}
