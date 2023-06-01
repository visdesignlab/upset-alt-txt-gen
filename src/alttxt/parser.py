import json

from alttxt.types import AggregateBy
from alttxt.types import FileType
from alttxt.types import SortBy
from alttxt.types import SortVisibleBy

from alttxt.models import BookmarkedIntersectionModel
from alttxt.models import DataModel
from alttxt.models import FilterModel
from alttxt.models import GrammarModel
from alttxt.models import PlotModel

from pathlib import Path
from collections import Counter
from typing import Any


Model = DataModel | GrammarModel


class Parser:
    def __init__(self, file_path: Path, file_type: FileType) -> None:
        self._data = self.load_file(file_path, file_type)

    def load_file(self, file_path: Path, file_type: FileType) -> Model:
        match file_type:
            case FileType.SETDATA:
                with open(file_path) as f:
                    setdata = f.read().splitlines()
                    parsed_data = self.__parse_setdata(setdata)

            case FileType.RAWDATA:
                with open(file_path) as f:
                    rawdata = json.load(f)
                    parsed_data = self.__parse_rawdata(rawdata)

            case FileType.GRAMMAR:
                with open(file_path) as f:
                    grammar = json.load(f)
                    parsed_data = self.__parse_grammar(grammar)

            case FileType.MATDATA:
                with open(file_path) as f:
                    matdata = json.load(f)
                    parsed_data = self.__parse_matdata(matdata)

            case FileType.TBLDATA:
                with open(file_path) as f:
                    tbldata = json.load(f)
                    parsed_data = self.__parse_tbldata(tbldata)

            case _:
                raise TypeError(f"Expected {FileType.list()}. Got {file_type}.")

        return parsed_data

    def __query_devs(
        self,
        membs: list[frozenset[str]],
        count: list[int],
        sets: list[str],
        sizes: dict[str, int],
    ) -> list[float]:
        """
        Computes the `disproportionality` w.r.t. expected `count`.
        Assumes marginal independence of the sets. Weakly adapted
        from Lex et al `UpSet: Visualizing Intersecting Sets`.
        """
        devs = [0.0] * len(membs)
        nval = sum(count)
        for i, membership in enumerate(membs):
            devs[i] = count[i] / nval
            residue = 1.0
            for set_ in membership:
                residue *= sizes[set_] / nval
            for set_ in filter(lambda set_: set_ not in membership, sets):
                residue *= 1 - sizes[set_] / nval
            devs[i] -= residue
        devs = list(map(lambda dev: round(100 * dev, 1), devs))
        return devs

    def __parse_setdata(self, setdata: list[str]) -> Model:
        # parse_line = lambda line: re.sub(r'\[|\]|\(|\)', '', line).split(', ')
        # parse_sets = list(map(parse_line, setdata))
        # sets, count = [], []
        # for parse_set in parse_sets:
        #     new_set = set()
        #     for element in parse_set[:-1]:
        #         if 'Not in' not in element:
        #             element = element.split(' ').pop()
        #             new_set.add(element)
        #     sets.append(new_set)
        #     count.append(parse_set[-1])
        #     sizes: dict[str, int] = {}
        #     stdev = self.__query_devs(sets, count, sizes)
        #     data_model = DataModel(sets=sets, sizes=count, count=count, devs=stdev)
        # return data_model
        return DataModel(membs=[], sets=[], sizes={}, count=[], devs=[])

    def __parse_rawdata(self, rawdata: dict[str, dict[str, Any]]) -> Model:
        sizes: dict[str, int] = {}
        sets_: list[str] = []
        for set_ in rawdata["sets"].values():
            set_name = set_["elementName"]
            sizes[set_name] = set_["size"]
            sets_.append(set_name)
        membs = []
        for elem in rawdata["items"].values():
            membership = frozenset(
                [
                    key
                    for key, value in elem.items()
                    if key in rawdata["setColumns"] and value == 1
                ]
            )
            if len(membership):
                membs.append(membership)
        count = list(Counter(membs).values())
        membs = list(Counter(membs).keys())
        devs = self.__query_devs(membs, count, sets_, sizes)
        data_model = DataModel(
            membs=membs, sets=sets_, sizes=sizes, count=count, devs=devs
        )
        return data_model

    def __parse_matdata(self, matdata: list[str]) -> Model:
        return DataModel(membs=[], sets=[], sizes={}, count=[], devs=[])

    def __parse_tbldata(self, tbldata: list[str]) -> Model:
        return DataModel(membs=[], sets=[], sizes={}, count=[], devs=[])

    def __parse_grammar(self, grammar: dict[str, Any]) -> Model:
        caption = grammar["caption"]
        title = grammar["title"]
        first_aggregate_by = AggregateBy(grammar["firstAggregateBy"])
        second_aggregate_by = AggregateBy(grammar["secondAggregateBy"])

        first_overlap_degree = int(grammar["firstOverlapDegree"])
        second_overlap_degree = int(grammar["secondOverlapDegree"])

        sort_visible_by = SortVisibleBy(grammar["sortVisibleBy"])

        sort_by = SortBy(grammar["sortBy"])

        filters = FilterModel(
            max_visible=grammar["filters"]["maxVisible"],
            min_visible=grammar["filters"]["minVisible"],
            hide_empty=grammar["filters"]["hideEmpty"],
        )

        plots = PlotModel(
            scatterplots=grammar["plots"]["scatterplots"],
            histograms=grammar["plots"]["histograms"],
            wordclouds=grammar["plots"]["wordClouds"],
        )

        collapsed = grammar["collapsed"]
        visible_sets = grammar["visibleSets"]
        visible_atts = grammar["visibleAttributes"]

        bookmarked_intersections = list(
            map(
                lambda bookmarked_intersection: BookmarkedIntersectionModel(
                    **bookmarked_intersection
                ),
                grammar["bookmarkedIntersections"],
            )
        )

        grammar_model = GrammarModel(
            caption=caption,
            title=title,
            first_aggregate_by=first_aggregate_by,
            second_aggregate_by=second_aggregate_by,
            first_overlap_degree=first_overlap_degree,
            second_overlap_degree=second_overlap_degree,
            sort_visible_by=sort_visible_by,
            sort_by=sort_by,
            filters=filters,
            collapsed=collapsed,
            visible_sets=visible_sets,
            visible_atts=visible_atts,
            plots=plots,
            bookmarked_intersections=bookmarked_intersections,
        )

        return grammar_model
