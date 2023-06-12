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
"symbols" key within the grammar, which is itself a dict. Note that when feeding symbols to
both the TokenMap and the grammar, the symbols must be stripped of their enclosing brackets.
"""
DESCRIPTIONS = {
    "level_0": {
        "low": "[[l0_low_desc]]",
        "medium": "[[l0_low_desc]] [[l0_med_desc]]",
        "high": "[[l0_low_desc]] [[l0_med_desc]] [[l0_high_desc]]",
    },
    "level_1": {
        "low": "This an UpSet plot that plots the {{title}}. A total of {{total}} "
        "co-occuring sets are displayed. They read from left to right "
        "as: {{list_set_names}}.",
        "medium": "This an UpSet plot of {{caption}} that plots the {{title}}. A total "
        "of {{total}} co-occuring sets are displayed. They read from left "
        "to right as: {{list_set_names}}. Visually, the plot is comprised of "
        "three components. Component 1 -- interlocking set sizes representing "
        "{{caption}} are plotted on the y-axis from {{min_size}} to {{max_size}}. "
        "Underneath is a graphical table of set membership showing a total of "
        "{{total}} {{caption}} observed across {{universal_set_size}} different "
        "patterns.",
        "high": "This an UpSet plot of {{caption}} that plots the {{title}}. A total "
        "of {{total}} co-occuring sets are displayed. They read from left "
        "to right as: {{list_set_names}}. Visually, the plot is comprised of "
        "three components. Component 1 -- interlocking set sizes representing "
        "{{caption}} are plotted on the y-axis from {{min_size}} to {{max_size}}. "
        "Underneath is a graphical table of set membership showing a total of "
        "{{total}} {{caption}} observed across {{universal_set_size}} different "
        "patterns. To the left is a smaller bar chart showing the unconditional "
        "frequency count of each set plotted on the x-axis from values from "
        "{{set_size_min}} to {{set_size_max}} in increments of {{set_size_inc}}. "
        "Sets are {{list_set_names}}.",
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
        "l0_low_desc": "This is an UpSet plot, a data visualization tool "
        "which uses a matrix to display the mathematical properties of intersecting sets.",
        "l0_med_desc": "The rows of the matrix represent sets or set intersections. "
        "The columns of the matrix are properties of intersections and variables in the dataset. "
        "Each entry in the matrix shows a property of the corresponding set intersection, or "
        "the distribution of a certain variable from the dataset in the corresponding intersection.",
        "l0_high_desc": "The first column shows which set intersection is visualized in that row. "
        "The second column shows the cardinality of each intersection. The third column shows "
        "the deviation of each set intersection, which represents how unexpected the cardinality "
        "of an intersection is given the size of its constituent sets. The remaining {{col_count}} columns "
        "show the average and quartiles of each variable from the dataset."
    },
}
