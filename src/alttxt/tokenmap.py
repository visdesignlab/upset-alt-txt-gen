from typing import Any, Callable, Tuple, Union, Optional
from alttxt.models import DataModel, GrammarModel, Subset
from alttxt.enums import SubsetField


class TokenMap:
    """
    This class maps tokens from the grammar to strings.
    Each string is either defined directly in the mapping,
    or is the result of a function call. Functions called
    should be defined in this class, and should return a string.
    Result strings can contain tokens, which are represented
    surrounded by curly braces, e.g. {{token}}.
    While this class returns a string for each token fed to it,
    it is not responsible for the actual substitution of tokens
    or the overall generation of the text description.
    """
    def __init__(self, data: DataModel, grammar: GrammarModel, title: Optional[str] = None, attribute: Optional[str] = None) -> None:
        """
        Initialize the Grammar class. Note that internal values 
        are not recomputed if the data or grammar are changed.
        Params:
            data: Imported from a data file generated by Upset
            grammar: Imported from a grammar file generated by Upset
            title: The title of the plot, if any
        """
        self.data: DataModel = data
        self.grammar: GrammarModel = grammar
        self.title: Optional[str] = title
        self.dataset_description: Optional[str] = attribute

        # This defines the mapping of tokens to strings/functions
        # As with the rest of this class, the curly braces surrounding
        # tokens are left out.
        # Generally, tokens which are easy to compute are done in the map,
        # whereas more complex tokens are done in functions.
        # Since functions are only executed on run, they can be used to
        # optimize by moving expensive tokens into fuctions.
        self.map: dict[str, Union[str, float, int, Callable[[], str]]] = {
            # Title of the plot as a phrase (with verb), with null check
            "title": f"is titled: {self.title}" if self.title else "has no title",
            # Dataset description as attribute name
            "dataset_description": f"The dataset shows attributes of {self.dataset_description}" if self.dataset_description else "",
            # Total number of elements in all sets, duplicates appear to be counted
            "universal_set_size": sum(self.data.sizes.values()),
            # Number of sets
            "set_count": len(self.data.sets),
            # Number of visible sets
            "visible_set_count": len(self.grammar.visible_sets),
            # List of set names
            "list_set_names": self.list_set_names,
            # List of visible set names
            "list_visible_set_names": self.list_visible_set_names,
            # size of the largest set/intersection
            "min_size": min(self.data.count),
            # size of the smallest set/intersection
            "max_size": max(self.data.count),
            # Average size of all intersections
            "avg_size": self.avg_size,
            # 25th percentile for size
            "25perc_size": self.get_subset_percentile(SubsetField.SIZE, 25),
            # 75th percentile for size
            "75perc_size": self.get_subset_percentile(SubsetField.SIZE, 75),
            # Counts populated intersections 
            "pop_intersect_count": len(self.data.subsets),
            # Sort type for intersections
            "sort_type": self.grammar.sort_by.value,
            # Number of intersections of each degree
            "list_degree_count": self.degree_count,
            # Number of intersections of each degree, their average size, and their average deviation
            "list_degree_info": self.degree_str(False),
            # Number of intersections of each degree, their average size, 
            # their average deviation, and their total size
            "list_degree_info_verbose": self.degree_str(True),
            # 10 largest intersections by size- includes name, size, deviation
            "list_max_10int": self.max_n_intersections(10),
            # Largest 5 intersections by size, including name, size, deviation
            "list_max_5int": self.max_n_intersections(5),
            # List all intersections in order of size, including name, size, deviation
            "list_all_int": self.max_n_intersections(len(self.data.subsets)),
            # 90th percentile for size
            "90perc_size": self.get_subset_percentile(SubsetField.SIZE, 90),
            # 10th percentile for size
            "10perc_size": self.get_subset_percentile(SubsetField.SIZE, 10),
            # Total number of attributes
            "var_count": len(self.grammar.visible_atts),
            # List of attribute names
            "list_var_names": ", ".join(self.grammar.visible_atts),
            # Number of intersections with positive deviation
            "pos_dev_count": self.dev_info()["pos_count"],
            # Number of intersections with negative deviation
            "neg_dev_count": self.dev_info()["neg_count"],
            # Total size of positive deviation intersections
            "pos_dev_size": self.dev_info()["pos_size_total"],
            # Total size of negative deviation intersections
            "neg_dev_size": self.dev_info()["neg_size_total"],
            # Average positive deviation
            "avg_pos_dev": self.dev_info()["pos_avg"],
            # Average negative deviation
            "avg_neg_dev": self.dev_info()["neg_avg"],
            # Sizes of visible sets, listed
            "list_set_sizes": self.set_sizes,
            # 10 largest deviations, listed
            "list10_dev_outliers": self.dev_outliers(10),
            # 5 largest deviations, listed
            "list5_dev_outliers": self.dev_outliers(5),
        }

    ###############################
    #       Public methods        #
    ###############################

    def get_token(self, token: str) -> str:
        """
        Return the string associated with the given token.
        If the token is unmapped, does not substitute it.
        Instead, returns it with curly braces around it.
        If the mapped value is not a string, float, int, or function,
        raises an exception.
        """
        if token not in self.map:
            # Substitute single curly braces so that the while loop doesn't go forever
            return "{" + token + "}"

        result: Any = self.map[token]
        if type(result) == float:
            return str(round(result, 2))
        elif type(result) == int:
            return str(result)
        elif type(result) == str:
            return result
        elif callable(result):
            return result()
        else:
            raise Exception("Invalid token type: " + str(type(result)))
    
    ###############################
    #           Helpers           #
    ###############################

    def sort_subsets_by_key(self, key: SubsetField, descending: bool = True) -> "list[Subset]":
        """
        Returns the list of subsets from self.data.subsets,
        sorted by a specified key. The key must be a valid field
        in the dict or an error will be raised.
        Params:
          key: The key to sort by. Must be a valid field in the Subset class.
          descending: Whether to sort in descending order
        """
        return sorted(self.data.subsets, key=lambda x:
                       getattr(x, key.value), reverse=descending)

    def degree_info(self, max_degree: int) -> "Tuple[list[int], list[float], list[float], list[int]]":
        """
        Returns information about intersections of degrees up to max_degree.
        The information, in order, is:
            - The number of intersections of each degree
            - The average size of intersections of each degree
            - The average deviation of intersections of each degree
        
        This function only works if the data is not aggregated. 
        Params:
            max_degree: The maximum degree to count to.
            Intersections with a degree greater than this are ignored.
            The returned lists will have length max_degree + 1. Since
            the lists are initialized with all 0s, all degree counts are accurate,
            but far more may be included than necessary.
        Returns:
            A tuple containing the four lists, 
            where the list index corresponds to the degree.
            For the first list, 
            the value at an index is the number of intersections with that degree.
            For the second list, 
            the value at an index is the average size of intersections with that degree.
            For the third list, 
            the value at an index is the average deviation of intersections with that degree.
            For the fourth list,
            the value at an index is the total size of intersections with that degree.
        """

        # 1 is added to each so that the max degree is included
        total_sizes: list[int] = [0] * (max_degree + 1)
        devs: list[float] = [0.0] * (max_degree + 1)
        degree_count: list[int] = [0] * (max_degree + 1)
        degree_count[0] = 1

        # Total all three values
        for subset in self.data.subsets:
            if subset.name == "Unincluded":
                total_sizes[0] += subset.size
                devs[0] += subset.dev
            
            degree = subset.degree
            if degree > max_degree:
                continue
            degree_count[degree] += 1
            total_sizes[degree] += subset.size
            devs[degree] += subset.dev
        
        # Convert totals to averages
        avg_sizes: list[float] = [0.0] * (max_degree + 1)
        for i in range(1, max_degree + 1):
            if degree_count[i] != 0:
                avg_sizes[i] = float(total_sizes[i]) / float(degree_count[i])
                devs[i] /= degree_count[i]
            # No need for else clause since the lists are initialized with 0s            

        return degree_count, avg_sizes, devs, total_sizes

    def dev_info(self) -> "dict[str, float]":
        """
        Returns a dictionary containing information about deviation.
        These overarching values are gathered only from non-empty intersections
        whose deviation is not 0.
        Dictionary keys:
            "pos_count": number of intersections with positive deviation
            "neg_count": number of intersections with negative deviation
            "pos_avg": average positive deviation
            "neg_avg": average negative deviation
            "pos_size_total": total size of positive deviations
            "neg_size_total": total size of negative deviations
            "pos_size_avg": average size of positive deviations
            "neg_size_avg": average size of negative deviations
        """
        pos_count: int = 0
        neg_count: int = 0
        pos_dev_total: int = 0
        neg_dev_total: int = 0
        pos_size_total: int = 0
        neg_size_total: int = 0

        for subset in self.data.subsets:
            if subset.dev > 0:
                pos_count += 1
                pos_dev_total += subset.dev
                pos_size_total += subset.size
            elif subset.dev < 0:
                neg_count += 1
                neg_dev_total += subset.dev
                neg_size_total += subset.size

        return {
            "pos_count": pos_count,
            "neg_count": neg_count,
            "pos_avg": pos_dev_total / pos_count if pos_count > 0 else 0,
            "neg_avg": neg_dev_total / neg_count if neg_count > 0 else 0,
            "pos_size_total": pos_size_total,
            "neg_size_total": neg_size_total,
            "pos_size_avg": pos_size_total / pos_count if pos_count > 0 else 0,
            "neg_size_avg": neg_size_total / neg_count if neg_count > 0 else 0,
        }

    ###############################
    #       Token functions       #
    ###############################

    def get_subset_percentile(self, field: SubsetField, perc: int) -> str:
        """
        Gets a percentile value for a specific field in this.data.subsets.
        Params:
          field: The field to get the percentile of.
          perc: The percentile to get. Must be between 0 and 100.
        """
        set_sort: list[Subset] = self.sort_subsets_by_key(field, False)
        index = int(len(set_sort) * perc / 100)
        return str(getattr(set_sort[index], field.value))

    def dev_outliers(self, n: int) -> str:
        """
        Returns a string listing the n largest intersections by absolute deviation,
        including the set name and its deviation
        """
        pos_sort: list[Subset] = self.sort_subsets_by_key(SubsetField.DEVIATION, True)
        neg_sort: list[Subset] = self.sort_subsets_by_key(SubsetField.DEVIATION, False)

        result: str = ""
        for i in range(0, n):
            if abs(pos_sort[0].dev) >= abs(neg_sort[0].dev):
                next_int: Subset = pos_sort.pop(0)
            else:
                next_int: Subset = neg_sort.pop(0)

            result += f"{next_int.name} ({next_int.dev}), "

        # Trim the trailing ', '
        return result[:-2]
            

    def set_sizes(self) -> str:
        """
        Returns string listing the size of each visible set.
        String is formatted as follows:
          "Set1: 10, Set2: 20, Set3: 30"
        """
        result: str = ""
        for setID, size in sorted(self.data.sizes.items(), key=lambda x: x[1], reverse=True):
            # Trim "Set_" from the setID if extant to make it match up with the name field
            set_name: str = setID[4:] if setID.startswith("Set_") else setID
            if set_name in self.grammar.visible_sets:
                result += f"{set_name}: {size}, "

        # Trim the trailing ', '
        return result[:-2]

    def max_n_intersections(self, n: int) -> str:
        """
        Returns a string listing the n largest intersections
        by size, including their name, size, and deviation
        Params:
          n: Number of sets to list
        """
        sort: list[Subset] = self.sort_subsets_by_key(SubsetField.SIZE, True)
        result: str = ""
        for i in range(0, n):
            if i >= len(sort):
                break

            result += f"{sort[i].name} ({sort[i].size}, {sort[i].dev}), "
            if i == n - 2:
                result += "and "

        # Trim the trailing ', '
        return result[:-2]

    def degree_count(self) -> str:
        """
        Returns a string describing the number of subsets with each degree.

        """
        result: str = ""

        for degree, count in enumerate(self.degree_info(20)[0]):
            if count == 0:
                continue
            result += f"{count} subsets with degree {degree}, "
        
        return result[:-2] # Remove trailing comma and space

    def degree_str(self, verbose = False) -> str:
        """
        Returns a string describing the number of intersections of each degree,
        their average size, and if verbose, their average deviation and total size.
        Maximum degree listed is 20.

        Params:
            verbose: Whether to include average deviation and total size for each degree
        """
        result: str = ""
        counts, avg_sizes, devs, total_sizes \
                = self.degree_info(20)

        # Start at 1 to skip the 0-degree/unincluded intersection
        for i in range(1, len(counts)):
            if counts[i] == 0:
                continue

            result += f"{counts[i]} subsets with degree {i} ({round(avg_sizes[i], 2)}"
            if verbose:
                result += f", {round(devs[i], 2)}, {total_sizes[i]}"
            result += "), "
        
        return result[:-2]

    def avg_size(self) -> str:
        """
        Returns the average size of all set intersections,
        rounded to an int
        """
        count: int = 0
        total: int = 0
        for intersection in self.data.subsets:
            total += intersection.size
            count += 1
        
        return str(int(total / count))

    def list_set_names(self) -> str:
        """
        Returns a string of the set names separated by commas,
        with the last two separated by "and".
        """
        return ", ".join(self.data.sets[:-1]) + " and " + self.data.sets[-1]
    
    def list_visible_set_names(self) -> str:
        """
        Returns a string of the visible set names separated by commas,
        with the last two separated by "and".
        """
        return ", ".join(self.grammar.visible_sets[:-1]) + " and " \
                + self.grammar.visible_sets[-1]