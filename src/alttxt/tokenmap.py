from enum import Enum
from typing import Any
from alttxt.models import DataModel
from alttxt.models import GrammarModel

from alttxt.types import AggregateBy, Orientation

from pprint import pprint


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
    def __init__(self, data: DataModel, grammar: GrammarModel, orientation: Orientation )-> None:
        """
        Initialize the Grammar class. Note that internal values 
        are not recomputed if the data or grammar are changed.
        Params:
            data: Imported from a data file generated by Upset
            grammar: Imported from a grammar file generated by Upset
        """
        self.data = data
        self.grammar = grammar

        # Computations for commonly-used values are done here
        # and stored as class attributes.
        _max_idx = self.data.count.index(max(self.data.count))
        _min_idx = self.data.count.index(min(self.data.count))
        self.max_sets, self.max_size = self.data.membs[_max_idx], max(self.data.count)
        self.min_sets, self.min_size = self.data.membs[_min_idx], min(self.data.count)
        self.total_data = sum(self.data.count)
        self.max_set = max(self.data.sizes, key=self.data.sizes.get)
        self.min_set = min(self.data.sizes, key=self.data.sizes.get)
        self.max_set_size = self.data.sizes[self.max_set]
        self.min_set_size = self.data.sizes[self.min_set]
        self.total_set_size = sum(self.data.sizes.values())

        # This defines the mapping of tokens to strings/functions
        # As with the rest of this class, the curly braces surrounding
        # tokens are left out.
        # Generally, tokens which are easy to compute are done in the map,
        # whereas more complex tokens are done in functions.
        # Since functions are only executed on run, they can be used to
        # optimize by moving expensive tokens into fuctions.
        self.map = {
            "set_count": len(self.data.sets),
            "list_set_names": self.list_set_names,
            "min_size": min(self.data.count),
            "max_size": max(self.data.count),
            "x_inc": self.data.count[1] - self.data.count[0],
            # Total number of elements in all sets, counting duplicates multiple times
            "universal_set_size": sum(self.data.sizes.values()),
            "min_perc": str(round(100 * self.min_size / self.total_data, 2)) + "%",
            "max_perc": str(round(100 * self.max_size / self.total_data, 2)) + "%",
            "list_max_membership": self.list_max_membership,
            "list_min_membership": self.list_min_membership,
            "list_max_set_name": self.max_set,
            "list_min_set_name": self.min_set,
            "max_set_perc": str(round(100 * self.max_set_size / self.total_set_size, 2)) + "%",
            "min_set_perc": str(round(100 * self.min_set_size / self.total_set_size, 2)) + "%",
            "max_dev": max(self.data.devs),
            "min_dev": min(self.data.devs),
            "list_max_dev_membership": self.list_max_dev_membership,
            "list_min_dev_membership": self.list_min_dev_membership,
            "list_set_info": self.list_set_info,
            "avg_card": self.avg_card,
            "25perc_card": self.perc_card_25,
            "75perc_card": self.perc_card_75,
            # Counts populated intersections for non-aggregated data;
            # otherwise, counts populated aggregates
            "pop_intersect_count": len(self.data.subsets),
            "sort_type": self.grammar.sort_by,
            # Currently raises an exception on aggregated plots
            "list_degree_info": self.list_degree_info,
            # 10 largest intersections by cardinality
            "list_max_10int": self.max_n_intersections(10),
            # Number of intersections below the 10th percentile
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

        result = self.map[token]
        if type(result) == float:
            return str(round(result, 2))
        elif type(result) == int:
            return str(result)
        elif type(result) == str:
            return result
        elif callable(result):
            return result()
        elif issubclass(type(result), Enum):
            return str(result.value)
        else:
            raise Exception("Invalid token type: " + str(type(result)))
    
    ###############################
    #           Helpers           #
    ###############################

    def sort_subsets_by_key(self, key: str, descending: bool = True) -> list:
        """
        Returns the list of subsets from self.data.subsets,
        sorted by a specified key. The key must be a valid field
        in the dict or an error will be raised.
        Params:
          key: The key to sort by. Must be a valid string.
          descending: Whether to sort in descending order
        """
        return sorted(self.data.subsets, key=lambda x: x[key], reverse=descending)

    def count_degrees(self, max_degree: int) -> list[int]:
        """
        Returns information about how many set intersections have
        a given degree. The index of the returned list is the degree,
        and the value is the number of intersections with that degree.
        
        The unincluded subset is the only one with degree 0, 
        so the 0 index is always 1.

        This function only works if the data is not aggregated. 
        If called with data that has been aggregated, it will raise.
        Params:
            max_degree: The maximum degree to count to.
            Intersections with a degree greater than this are ignored.
            The returned list will have length max_degree + 1. Since
            the list is initialized with all 0s, all degree counts are accurate,
            but far more may be included than necessary.
        """
        if self.grammar.first_aggregate_by != AggregateBy.NONE:
            raise Exception("Cannot count degrees on aggregated data")

        result: list[int] = [0] * (max_degree + 1) # Add 1 so that max_degree is included
        result[0] = 1

        for subset in self.data.subsets:
            if subset["name"] == "Unincluded":
                continue
            
            degree = subset["degree"]
            if degree > max_degree:
                continue
            result[degree] += 1
        
        return result

    def get_subset_percentile(self, field: str, perc: int) -> Any:
        """
        Gets a percentile value for a specific field in this.data.subsets.
        Params:
          field: The field to get the percentile of.
          perc: The percentile to get. Must be between 0 and 100.
        """
        set_sort = self.sort_subsets_by_key(field)
        index = int(len(set_sort) * perc / 100)
        return set_sort[index][field]

    ###############################
    #       Token functions       #
    ###############################

    def max_n_intersections(self, n: int) -> str:
        """
        Returns a string listing the n largest intersections
        by cardinality 
        Params:
          n: Number of sets to list
        """
        sort = self.sort_subsets_by_key("card", True)
        result = ""
        for i in range(0, n):
            if n >= len(sort):
                break

            result += f"{sort[i]['name']}, "
            if i == n - 2:
                result += "and "

        # Trim the trailing ', '
        return result[:-2]

    def list_degree_info(self) -> str:
        """
        Returns a string describing the degree of each set.
        If sets are not aggregated, this simply counts the number
        of subsets with each degree, to a maximum degree of 50.
        If sets are aggregated by degree, this returns information
        about each degree aggregate: the degree, the number of sets,
        If sets are aggregated by anything else, a warning message is returned,
        as the implementation currently does not support listing degree info
        for non-degree aggregation types.
        """
        result = ""

        if self.grammar.first_aggregate_by == AggregateBy.NONE:
            for degree, count in enumerate(self.count_degrees(50)):
                if count == 0:
                    continue
                result += f"{count} subsets with degree {degree}, "

        elif self.grammar.first_aggregate_by == AggregateBy.DEGREE:
            for agg in self.data.subsets:
                result += f"{agg['count']} subsets of degree {agg['name'].split(' ')[1]} "
                "with total cardinality {agg['card']} and deviation {agg['dev']}; "
        else:
            return "(Cannot list degree info for non-degree aggregation types)"

        return result[:-2] # Remove trailing comma and space

    def perc_card_25(self) -> str:
        """
        Returns the 25th percentile of set cardinalities
        """
        return self.get_subset_percentile("card", 25)

    def perc_card_75(self) -> str:
        """
        Returns the 75th percentile of set cardinalities
        """
        return self.get_subset_percentile("card", 75)

    def avg_card(self) -> str:
        """
        Returns the average cardinality of all set intersections,
        rounded to an int
        """
        count: int = 0
        total: int = 0
        for intersection in self.data.subsets:
            total += intersection["card"]
            count += 1
        
        return str(int(total / count))

    def list_set_info(self):
        """
        Return a string containing a series of sentences with 
        information about each set. Length varies depending on
        the number of sets. For use when the plot is aggregated by set
        """
        pass

    def list_max_dev_membership(self):
        """
        Return the union of sets that has the highest deviation
        from its expected cardinality
        """
        _max_dev_idx = self.data.devs.index(self.map["max_dev"])
        max_dev_set = self.data.membs[_max_dev_idx]
        
        if len(max_dev_set) > 1:
            return ", ".join(list(max_dev_set)[:-1]) + " and " + list(max_dev_set)[-1]
        else:
            return list(max_dev_set)[0]

    def list_min_dev_membership(self):
        """
        Return the union of sets that has the lowest deviation
        from its expected cardinality
        """
        _min_dev_idx = self.data.devs.index(self.map["min_dev"])
        min_dev_set = self.data.membs[_min_dev_idx]
    
        if len(min_dev_set) > 1:
            return ", ".join(list(min_dev_set)[:-1]) + " and " + list(min_dev_set)[-1]
        else:
            return list(min_dev_set)[0]

    def list_max_membership(self) -> str:
        """
        Returns a string of the set names with the maximum number of
        memberships, separated by commas, with the last two separated by "and".
        """
        if len(self.max_sets) > 1:
            return ", ".join(list(self.max_sets)[:-1]) + " and " + list(self.max_sets)[-1]
        else:
            return list(self.max_sets)[0]

    def list_min_membership(self) -> str:
        """
        Returns a string of the set names with the minimum number of
        memberships, separated by commas, with the last two separated by "and".
        """
        if len(self.min_sets) > 1:
            return ", ".join(list(self.min_sets)[:-1]) + " and " + list(self.min_sets)[-1]
        else:
            return list(self.min_sets)[0]

    def list_set_names(self) -> str:
        """
        Returns a string of the set names separated by commas,
        with the last two separated by "and".
        """
        return ", ".join(self.data.sets[:-1]) + " and " + self.data.sets[-1]