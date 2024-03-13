from typing import Any, Callable, Tuple, Union, Optional
from alttxt.models import DataModel, GrammarModel, Subset
from alttxt.enums import SubsetField, IndividualSetSize, IntersectionTrend, SortBy, IntersectionType, SortOrder
import statistics
from alttxt.regionclass import *
import math
from collections import Counter


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
    def __init__(self, data: DataModel, grammar: GrammarModel, title: Optional[str] = None) -> None:
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
            "dataset_description": f"The dataset shows attributes of {self.grammar.metaData.description}. " if self.grammar.metaData.description else "",
            # Set description as set name
            "set_description": f"{self.grammar.metaData.items}" if self.grammar.metaData.items else "elements",
            # largest by what factor
            "largest_factor": f" {self.sort_subsets_by_key(SubsetField.SIZE, True)[0].name} is the largest by a factor of {self.calculate_largest_factor()}." if self.calculate_largest_factor() >= 2 else "",
            # set intersection categorization text based on intersection type and size
            "empty_set_presence": f" The empty intersection is present with a size of {self.get_empty_intersection_size()}." if (self.categorize_subsets().get('the empty intersection') and self.categorize_subsets().get('the empty intersection')!='largest_data_region') else "",
            "all_set_presence": f" An all set intersection is present with a size of {self.get_all_set_intersection_size()}." if self.get_all_set_intersection_size()!= None else f" An all set intersection is not present.",
            "intersection_trend_analysis":f"{self.calculate_intersection_trend()}" if self.grammar.sort_by == SortBy.SIZE else "",
            "individual_set_presence": f"{self.individual_set_presence()}",
            "low_set_presence": f"{self.low_set_presence()}",
            "high_set_presence": f"{self.high_set_presence()}",
            "medium_set_presence": f"{self.medium_set_presence()}",
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
            # Visual set sizes, sorted
            "sort_visible_sets": self.sort_visible_sets,
            # List of sorted visible set names and sizes
            "list_sorted_visible_sets": self.list_sorted_visible_sets,
            # Largest visible set name
            "max_set_name": self.sort_visible_sets()[0][0],
            # Largest visible set size
            "max_set_size": self.sort_visible_sets()[0][1],
            # max set percentage
            "max_set_percentage": self.calculate_max_min_set_presence(self.sort_visible_sets()[0][0]),
            # Smallest visible set name
            "min_set_name": self.sort_visible_sets()[-1][0],
            # Smallest visible set size
            "min_set_size": self.sort_visible_sets()[-1][1],
            # min set percentage
            "min_set_percentage": self.calculate_max_min_set_presence(self.sort_visible_sets()[-1][0]),
            # Set Divergence
            "set_divergence": self.calculate_set_divergence,
            # largest intersection name and size
            "max_intersection_name": self.calculate_max_intersection()[0],
            "max_intersection_size": self.calculate_max_intersection()[1],
            # size of the largest set/intersection
            "min_size": min(self.data.count),
            # size of the smallest set/intersection
            "max_size": max(self.data.count),
            # Average size of all intersections
            "avg_size": self.avg_size,
            # Median size of all intersections
            "median_size": self.median_size,
            # 25th percentile for size
            "25perc_size": self.get_subset_percentile(SubsetField.SIZE, 25),
            # 75th percentile for size
            "75perc_size": self.get_subset_percentile(SubsetField.SIZE, 75),
            # Counts populated intersections 
            "pop_intersect_count": len(self.data.subsets),
            # Counts non-empty visible intersections
            "non_empty_visible_intersect_count": self.count_non_empty_visible_subsets,
            # Counts non-empty intersections
            "non_empty_intersect_count": self.count_non_empty_subsets,
            # Number of visible non-empty intersections
            "visible_non_empty_intersect_count": self.count_non_empty_visible_subsets,
            # Number of total non-empty intersections
            "total_non_empty_intersect_count": self.count_non_empty_subsets,
            # a non terminal symbol, might move later
            "pop_non-empty_intersections": f"There are {self.count_non_empty_subsets()} non-empty intersections, all of which are shown in the plot" if self.count_non_empty_subsets() == self.count_non_empty_visible_subsets()
            else f"There are {self.count_non_empty_subsets()} non-empty intersections, {self.count_non_empty_visible_subsets()} of which are shown in the plot",
            # Sort type for intersections
            "sort_type": self.grammar.sort_by.value,
            "sort_order": self.grammar.sort_order.value,
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
            "max_int_size": self.sort_subsets_by_key(SubsetField.SIZE, True)[0].size,
            "max_int_name": self.sort_subsets_by_key(SubsetField.SIZE, True)[0].name,
            "min_int_size": self.sort_subsets_by_key(SubsetField.SIZE, True)[-1].size,
            "min_int_name": self.sort_subsets_by_key(SubsetField.SIZE, True)[-1].name,
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
            "category_of_subsets": self.categorize_subsets
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

    def dev_info(self) -> dict[str, float]:
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

            result += f"{sort[i].name} ({sort[i].size}), "
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
        Returns the average size of all visible non-empty set intersections,
        rounded to an int.
        """
        count = 0
        total = 0
        for intersection in self.data.subsets:
            if intersection.size > 0:  # Check if the intersection is non-empty
                total += intersection.size
                count += 1

        if count > 0:
            average = total / count
        else:
            average = 0  # Avoid division by zero if there are no non-empty intersections

        return str(int(average))
    
    def median_size(self) -> str:
        """
        Returns the median size of all set intersections,
        rounded to an int.
        """
        sort: list[Subset] = self.sort_subsets_by_key(SubsetField.SIZE, False)
        
        # Calculate the middle index
        mid = len(sort) // 2  # Divide and get floor

        # Check if the number of subsets is even
        if len(sort) % 2 == 0:  # Even number of elements
            median_val = (sort[mid - 1].size + sort[mid].size) / 2
        else:  # Odd number of elements
            median_val = sort[mid].size

        return str(int(median_val))


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
    
    def sort_visible_sets(self) -> dict[str, int]:
        """
        Returns a dictionary mapping visible set names to their sizes,
        sorted by size in descending order.
        """
        return sorted(self.grammar.visible_set_sizes.items(), key=lambda item: item[1], reverse=True)

    
    def list_sorted_visible_sets(self) -> str:
        """
        Returns a string of the visible set names and sizes. The string should contain the 2nd largest set name with size, 
        followed by the 3rd largest set name with size, and so on. The string should end with the smallest set name with size.
        Example string: "[SET2name] with [set2size], [SET3name] with [set3size],.. , and [SETnname] with [setnsize]"
        """
        # Sort the sets by size in descending order and exclude the largest set
        sorted_by_size = sorted(self.grammar.visible_set_sizes.items(), key=lambda item: item[1], reverse=True)[1:]

        # Format the sorted sets into the desired string format
        if len(sorted_by_size) > 1:
            set_strings = [f"{set_name} with {size}" for set_name, size in sorted_by_size[:-1]]
            last_set_string = f"{sorted_by_size[-1][0]} with {sorted_by_size[-1][1]}"
            return ", ".join(set_strings) + ", and " + last_set_string
        elif sorted_by_size:
            # If there is only one set after excluding the largest
            return f"{sorted_by_size[0][0]} with {sorted_by_size[0][1]}"
        else:
            # If there are no sets to list (empty or only one set was visible initially)
            return "No sets to list"
        
    def count_non_empty_visible_subsets(self) -> int:
        """
        Counts the number of subsets with a size greater than zero.

        Returns:
            int: The count of non-empty subsets.
        """
        non_empty_count = 0

        # Iterate through each subset in the list
        for subset in self.data.subsets:
            # Check if the size of the subset is greater than zero
            if subset.size > 0:
                non_empty_count += 1

        return non_empty_count
    
    def count_non_empty_subsets(self) -> int:
        """
        Counts the number of subsets with a size greater than zero.

        Returns:
            int: The count of non-empty subsets.
        """
        non_empty_count = 0 

        # Iterate through each subset in the list
        for subset in self.data.all_subsets:
            # Check if the size of the subset is greater than zero
            if subset.size > 0:
                non_empty_count += 1

        return non_empty_count
    
    def calculate_max_min_set_presence(self, maxmin_sized_set_name) -> str:
        """
        Calculate the percentage of non-empty intersections where the largest and smallest sets are present.
        """
        # Counters for the number of non-empty intersections including the largest and smallest sets
        maxmin_set_count = 0

        # Total number of non-empty intersections
        total_non_empty = sum(1 for subset in self.data.all_subsets if subset.size > 0)

        # Iterate through all subsets
        for subset in self.data.all_subsets:
            if subset.size > 0:  # Check only non-empty subsets
                if maxmin_sized_set_name in subset.name:
                    maxmin_set_count += 1

        # Calculate percentages
        maxmin_set_percentage = (maxmin_set_count / total_non_empty) * 100 if total_non_empty else 0

        return f"{maxmin_set_percentage:.1f}%"

    def calculate_max_intersection(self) -> dict[str, int]:
        """
        Calculate the largest intersection size and name that contains more than one set.
        """
        largest_size = 0
        largest_subset = None

        for subset in self.data.subsets:
            if subset.degree > 1 and subset.size > largest_size:
                largest_size = subset.size
                largest_subset = subset

        # 'largest_subset' now holds the subset with more than one set that has the largest size
        if largest_subset is not None:
            return largest_subset.name, largest_subset.size
        else:
            return None, 0
        
    def calculate_min_intersection(self) -> dict[str, int]:
        """
        Calculate the smallest intersection size and name that contains more than one set.
        """
        smallest_size = float('inf')
        smallest_subset = None

        for subset in self.data.subsets:
            if subset.degree > 1 and subset.size < smallest_size:
                smallest_size = subset.size
                smallest_subset = subset

        # 'smallest_subset' now holds the subset with more than one set that has the smallest size
        if smallest_subset is not None:
            return smallest_subset.name, smallest_subset.size
        else:
            return None, 0
        
   
    def calculate_set_divergence(self):
        # Assuming self.data.subsets is a list of Subset objects with a 'size' attribute
        # First, find the max and min set sizes
        max_set_size = self.sort_visible_sets()[0][1]
        min_set_size = self.sort_visible_sets()[-1][1]
        
        # Calculate the divergence percentage
        divergence_percentage = (min_set_size / max_set_size) * 100

        # Determine the divergence category
        if divergence_percentage < 26.67:
            return IndividualSetSize.DIVERGINGALOT.value
        elif 26.68 <= divergence_percentage <= 53.34:
            return IndividualSetSize.DIVERGING.value
        elif 53.35 <= divergence_percentage <= 79.99:
            return IndividualSetSize.DIVERGINGABIT.value
        else: # divergence_percentage >= 80
            return IndividualSetSize.IDENTICAL.value
        

    def calculate_change_trend(self):
        # Extract sizes from the sorted list of tuples (sorted_by_size)
        intersection_sizes = [self.data.subsets[i].size for i in range(len(self.data.subsets))]
        
        # Calculate the standard deviation of the intersection sizes
        std_dev = statistics.stdev(intersection_sizes)
        mean_size = statistics.mean(intersection_sizes)
        
        # Determine the trend based on the standard deviation
        # Adjust the threshold as necessary for your specific data and requirements
        threshold = 0.1  # Example threshold for deciding between gradual and drastic
        relative_std_dev = std_dev / mean_size
        
        if std_dev == 0:
            return IntersectionTrend.CONSTANT.value
        elif relative_std_dev < threshold:
            return IntersectionTrend.GRADUAL.value
        else:
            return IntersectionTrend.DRASTIC.value
        
    def calculate_largest_factor(self):
        # Ensure the list is sorted in descending order
        sorted_sizes = self.sort_subsets_by_key(SubsetField.SIZE, True)
        # Calculate the factor
        if len(sorted_sizes) >= 2:
            largest_size = sorted_sizes[0].size
            second_largest_size = sorted_sizes[1].size
            
            # Avoid division by zero
            if second_largest_size > 0:
                factor = largest_size / second_largest_size
                decimal_part = factor - math.floor(factor)
                # Apply ceiling for > 0.8, otherwise floor
                if decimal_part > 0.78:
                    adjusted_factor = math.ceil(factor)
                else:
                    adjusted_factor = math.floor(factor)
                return int(adjusted_factor)
        return None  


    def categorize_subsets(self):
        """
        Categorize the subsets into small, medium, large and largest regions based on their size.
        """
        results = {}
        sorted_subsets = sorted(self.data.subsets, key=lambda subset: subset.size, reverse=True)
        
        largest_subset = sorted_subsets.pop(0)  # Remove the largest
        
        median_size = statistics.median([subset.size for subset in sorted_subsets])
        
        region_classification = RegionClassification()
        
        region_classification.set_largest(largest_subset)
        
        close_to_zero_threshold = median_size * 1.2  # Define what 'close to zero' means
        
        for subset in sorted_subsets:
            deviation = subset.size - median_size
            
            if deviation < 0 and abs(deviation) > abs(median_size-close_to_zero_threshold):
                region_classification.add_to_small_region(subset)
            elif deviation == 0 or abs(deviation) <= abs(median_size-close_to_zero_threshold):
                region_classification.add_to_medium_region(subset)
            else:  # deviation > 0 and not close to zero
                region_classification.add_to_large_region(subset)


        regions = {
        'largest_data_region': [region_classification.largest_data_region],
        'large_data_region': region_classification.large_data_region,
        'medium_data_region': region_classification.medium_data_region,
        'small_data_region': region_classification.small_data_region,
        # Assuming largest_data_region is a single subset, not a list
        
        }


        total_sizes = {region: sum(subset.size for subset in subsets) for region, subsets in regions.items()}

        for region_name, subsets in regions.items():
            # Initialize dictionary to store sizes for special classifications
            special_sizes = {}
            # Initialize Counter for other classifications
            classification_sizes = Counter()

            for subset in subsets:
                # Handle 'the empty set' and 'all set' by directly logging their sizes
                # if subset.classification in ['the empty set', 'all set']:
                #     special_sizes[subset.classification] = subset.size
                if subset.classification in ['the empty set']:
                    special_sizes[subset.classification] = subset.size
                # elif subset.degree == self.data.all_sets_length:
                #     special_sizes[IntersectionType.ALL_SET] = subset.size
                else:
                    classification_sizes[subset.classification] += subset.size

                    

            # Calculate percentages based on sizes for other classifications
            percentages = {cls: (size / total_sizes[region_name] * 100) for cls, size in classification_sizes.items()}
            
            # Update results with percentages and direct sizes for special cases
            results[region_name] = {**percentages, **special_sizes}

        classification_to_regions = {}
        
        threshold_percentage = 35.0  # Define the threshold for inclusion

        for region, classifications in results.items():
                for classification, value in classifications.items():
                    # Direct inclusion for single-region classifications or exceeding threshold
                    if classification.value not in classification_to_regions or value >= threshold_percentage:
                        classification_to_regions.setdefault(classification.value, {}).update({region: value})
                    else:
                        # Include only if the percentage exceeds the threshold
                        existing_region, existing_value = next(iter(classification_to_regions[classification.value].items()))
                        if value > existing_value:
                            classification_to_regions[classification.value].update({region: value})
                        # classification_to_regions[classification.value].update({region: value})


            # Refine mapping based on the new rules
        for classification, regions_percentages in classification_to_regions.items():
            if len(regions_percentages) > 1:
                    # Filter regions by threshold and select the highest if none exceed the threshold
                above_threshold_regions = {region: pct for region, pct in regions_percentages.items() if pct >= threshold_percentage}

            # If no regions meet the threshold, choose the one with the highest percentage
                if not above_threshold_regions:
                    highest_region = max(regions_percentages, key=regions_percentages.get)
                    classification_to_regions[classification] = {highest_region}
                else:
                    # Include all regions that meet the threshold
                    classification_to_regions[classification] = set(above_threshold_regions.keys())
            else:
                # If the classification is present in only one region, include it regardless of the percentage
                classification_to_regions[classification] = set(regions_percentages.keys())

        # Handle special cases such as 'the empty set' and 'all set'
        # Assuming they should be directly mapped without considering the threshold
        for special_case in ['the empty set', 'all set']:
            if special_case in results:
                for region in results[special_case]:
                    classification_to_regions[special_case] = {region}


        final_output = {cls: {regions} if isinstance(regions, str) else set(regions) for cls, regions in classification_to_regions.items()}
        
        return final_output

    

    def get_empty_intersection_size(self):
    # Iterate through subsets to find 'the empty intersection'
        for subset in self.data.subsets:
            if subset.classification.value == 'the empty intersection':
                return subset.size
        # Return 0 or None if 'the empty intersection' is not found
        return None

    def get_all_set_intersection_size(self):
        for subset in self.data.subsets:
            if subset.degree == self.data.all_sets_length:
                return subset.size
        # Return 0 or None if 'all set' intersection is not found
        return None
    
    def individual_set_presence(self) -> str:
        categorization = self.categorize_subsets()
        individual_set_regions = categorization.get('individual set')

        if individual_set_regions:
            # Convert set to list to index
            regions_list = list(individual_set_regions)
            if len(regions_list) == 1:
                return f" The individual set intersections are {regions_list[0].replace('_data_region', '')} in size."
            else:
                regions_formatted = [region.replace('_data_region', '') for region in regions_list]
                return f" The individual set intersections are in {' and '.join(regions_formatted)} intersections."
        else:
            return " No individual set intersections are present."
        
    def medium_set_presence(self) -> str:
        categorization = self.categorize_subsets()
        medium_set_regions = categorization.get('medium set')

        if medium_set_regions:
            # Convert set to list to index
            regions_list = list(medium_set_regions)
            if len(regions_list) == 1:
                return f" The medium degree set intersections can be seen among {regions_list[0].replace('_data_region', '')} sized intersections."
            else:
                regions_formatted = [region.replace('_data_region', '') for region in regions_list]
                return f" The medium degree set intersections can be seen among {' and '.join(regions_formatted)} sized intersections."
        else:
            return ""
        
    def low_set_presence(self) -> str:
        categorization = self.categorize_subsets()
        low_set_regions = categorization.get('low set')

        if low_set_regions:
            # Convert set to list to index
            regions_list = list(low_set_regions)
            if len(regions_list) == 1:
                return f" The low degree set intersections lie in {regions_list[0].replace('_data_region', '')} sized intersections."
            else:
                regions_formatted = [region.replace('_data_region', '') for region in regions_list]
                return f" The low degree set intersections lie in {' and '.join(regions_formatted)} sized intersections."
        else:
            return ""
        
    def high_set_presence(self) -> str:
        categorization = self.categorize_subsets()

        high_set_regions = categorization.get('high order set')

        if high_set_regions:
            # Convert set to list to index
            regions_list = list(high_set_regions)
            if len(regions_list) == 1:
                if regions_list[0] == 'largest_data_region':
                    return " The high order set intersections are the largest."
                return f" Among the {regions_list[0].replace('_data_region', '')} sized intersections, the high order set intersections are significantly present."
            else:
                regions_formatted = [region.replace('_data_region', '') for region in regions_list]
                return f" In {' and '.join(regions_formatted)} sized intersections, the high order set intersections are significantly present."
        else:
            return " No high order intersections are present."
        

    def calculate_intersection_trend(self) -> str:
        intersection_trend = self.calculate_change_trend()

        max_int_size = self.sort_subsets_by_key(SubsetField.SIZE, True)[0].size
        min_int_size =  self.sort_subsets_by_key(SubsetField.SIZE, True)[-1].size
        
        if self.grammar.sort_order == SortOrder.DESCENDING:
            return f" The intersection sizes peak at a value of {max_int_size} and then {intersection_trend} flatten down to {min_int_size}."
            
        else:
            return f" The intersection sizes start from a value of {min_int_size} and then {intersection_trend} rise up to {max_int_size}."

   