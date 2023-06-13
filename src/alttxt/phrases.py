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
    "level_2": {
        "low": "This is an upset plot. Set membership comprised of {{list_max_membership}} "
        "have the highest unconditional frequency count totaling {{max_perc}} of "
        "these. In contrast, set membership consisting of {{list_min_membership}} "
        "has the lowest frequency count amounting barely {{min_perc}} of all "
        "memberships.",
        "medium": "This is an upset plot. Set membership comprised of {{list_max_membership}} "
        "have the highest unconditional frequency count totaling {{max_perc}} of "
        "these. In contrast, set membership consisting of {{list_min_membership}} "
        "has the lowest frequency count amounting barely {{min_perc}} of all "
        "memberships. The singleton set comprised of {{list_max_set_name}} has "
        "the highest unconditional frequency count totaling {{max_set_perc}} of "
        "the entire dataset. However, the single set comprised of {{list_min_set_name}} "
        "has the lowest frequency count amounting only {{min_set_perc}} of the "
        "dataset.",
        "high": "This is an upset plot. Set membership comprised of {{list_max_membership}} "
        "have the highest unconditional frequency count totaling {{max_perc}} of "
        "these. In contrast, set membership consisting of {{list_min_membership}} "
        "has the lowest frequency count amounting barely {{min_perc}} of all "
        "memberships. The singleton set comprised of {{list_max_set_name}} has "
        "the highest unconditional frequency count totaling {{max_set_perc}} of "
        "the entire dataset. However, the single set comprised of {{list_min_set_name}} "
        "has the lowest frequency count amounting only {{min_set_perc}} of the "
        "dataset. Lastly, set membership comprised of {{list_max_dev_membership}} "
        "has the highest deviation from its expected cardinality with a numeric deviation "
        "of {{max_dev}}. On the contrary, the set membership comprised of "
        "{{list_min_dev_membership}} has the lowest deviation with a numeric deviation "
        "equal to {{min_dev}}.",
    },
    "symbols": {
        # Basic description of an UpSet plot
        "l0_low_desc": "this is an UpSet plot, a data visualization tool "
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
        "list_vars": "{{var_count}} variables are visualized- {{list_var_names}}"
    },
}
