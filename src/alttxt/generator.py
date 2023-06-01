import re

from alttxt import phrases

from alttxt.models import DataModel
from alttxt.models import GrammarModel
from alttxt.types import Granularity
from alttxt.types import Level
from alttxt.types import Orientation

from typing import cast


Model = DataModel | GrammarModel


class AltTxtGen:
    def __init__(
        self,
        orientation: Orientation,
        data: Model,
        grammar: Model,
        level: Level,
        granularity: Granularity,
    ) -> None:
        self.data = cast(DataModel, data)
        self.descriptions = phrases.DESCRIPTIONS
        self.orientation = orientation
        self.grammar = cast(GrammarModel, grammar)
        self.granularity = granularity
        self.level = level

    def quantiles(self) -> list[list[float]]:
        quants: list[list[float]] = []
        return quants

    @property
    def text(self) -> str:
        text_desc = ""
        match self.level:
            case Level.ZERO:
                text_desc = self.descriptions[f"level_{Level.ZERO.value}"][
                    self.granularity.value
                ]

            case Level.ONE:
                text_desc = self.descriptions[f"level_{Level.ONE.value}"][
                    self.granularity.value
                ]
                text_desc = re.sub(r"{{caption}}", f"{self.grammar.caption}", text_desc)
                text_desc = re.sub(r"{{title}}", f"{self.grammar.title}", text_desc)
                text_desc = re.sub(r"{{total}}", f"{len(self.data.sets)}", text_desc)
                text_desc = re.sub(
                    r"{{list_set_names}}",
                    f'{", ".join(self.data.sets[:-1])} and {self.data.sets[-1]}',
                    text_desc,
                )
                text_desc = re.sub(r"{{x_min}}", f"{min(self.data.count)}", text_desc)
                text_desc = re.sub(r"{{x_max}}", f"{max(self.data.count)}", text_desc)
                text_desc = re.sub(
                    r"{{x_inc}}",
                    f"{self.data.count[1] - self.data.count[0]}",
                    text_desc,
                )
                text_desc = re.sub(
                    r"{{universal_set_size}}",
                    f"{sum(self.data.sizes.values())}",
                    text_desc,
                )

            case Level.TWO:
                _max_idx, _min_idx = self.data.count.index(
                    max(self.data.count)
                ), self.data.count.index(min(self.data.count))
                max_sets, max_size = self.data.membs[_max_idx], max(self.data.count)
                min_sets, min_size = self.data.membs[_min_idx], min(self.data.count)

                text_desc = self.descriptions[f"level_{Level.TWO.value}"][
                    self.granularity.value
                ]
                text_desc = re.sub(
                    r"{{max_perc}}",
                    f"{100*max_size/sum(self.data.count):.2f}%",
                    text_desc,
                )
                text_desc = re.sub(
                    r"{{min_perc}}",
                    f"{100*min_size/sum(self.data.count):.2f}%",
                    text_desc,
                )

                if len(max_sets) > 1:
                    text_desc = re.sub(
                        r"{{list_max_membership}}",
                        f'{", ".join(list(max_sets)[:-1])} and {list(max_sets)[-1]}',
                        text_desc,
                    )
                else:
                    text_desc = re.sub(
                        r"{{list_max_membership}}",
                        f"{list(max_sets).pop()}",
                        text_desc,
                    )

                if len(min_sets) > 1:
                    text_desc = re.sub(
                        r"{{list_min_membership}}",
                        f'{", ".join(list(min_sets)[:-1])} and {list(min_sets)[-1]}',
                        text_desc,
                    )
                else:
                    text_desc = re.sub(
                        r"{{list_min_membership}}",
                        f"{list(min_sets).pop()}",
                        text_desc,
                    )

                if (
                    self.granularity.value == "medium"
                    or self.granularity.value == "high"
                ):

                    def fetch_max_set(set_sizes):
                        return max(set_sizes, key=set_sizes.get)

                    def fetch_min_set(set_sizes):
                        return min(set_sizes, key=set_sizes.get)

                    max_set_size = self.data.sizes[fetch_max_set(self.data.sizes)]
                    min_set_size = self.data.sizes[fetch_min_set(self.data.sizes)]

                    text_desc = re.sub(
                        r"{{list_max_set_name}}",
                        f"{fetch_max_set(self.data.sizes)}",
                        text_desc,
                    )
                    text_desc = re.sub(
                        r"{{list_min_set_name}}",
                        f"{fetch_min_set(self.data.sizes)}",
                        text_desc,
                    )

                    text_desc = re.sub(
                        r"{{max_set_perc}}",
                        f"{100*max_set_size/sum(self.data.sizes.values()):.2f}%",
                        text_desc,
                    )
                    text_desc = re.sub(
                        r"{{min_set_perc}}",
                        f"{100*min_set_size/sum(self.data.sizes.values()):.2f}%",
                        text_desc,
                    )

                if self.granularity.value == "high":
                    _max_idx, _min_idx = self.data.devs.index(
                        max(self.data.devs)
                    ), self.data.devs.index(min(self.data.devs))
                    max_dev_set, max_dev_val = self.data.membs[_max_idx], max(
                        self.data.devs
                    )
                    min_dev_set, min_dev_val = self.data.membs[_min_idx], min(
                        self.data.devs
                    )

                    text_desc = re.sub(
                        r"{{max_dev}}",
                        f"{max_dev_val}",
                        text_desc,
                    )
                    text_desc = re.sub(
                        r"{{min_dev}}",
                        f"{min_dev_val}",
                        text_desc,
                    )

                    if len(max_dev_set) > 1:
                        text_desc = re.sub(
                            r"{{list_max_dev_membership}}",
                            f'{", ".join(list(max_dev_set)[:-1])} and {list(max_dev_set)[-1]}',
                            text_desc,
                        )
                    else:
                        text_desc = re.sub(
                            r"{{list_max_dev_membership}}",
                            f"{list(max_dev_set).pop()}",
                            text_desc,
                        )

                    if len(min_dev_set) > 1:
                        text_desc = re.sub(
                            r"{{list_min_dev_membership}}",
                            f'{", ".join(list(min_dev_set)[:-1])} and {list(min_dev_set)[-1]}',
                            text_desc,
                        )
                    else:
                        text_desc = re.sub(
                            r"{{list_min_dev_membership}}",
                            f"{list(min_dev_set).pop()}",
                            text_desc,
                        )

            case Level.THREE:
                text_desc = self.descriptions[f"level_{Level.THREE.value}"][
                    self.granularity.value
                ]

            case _:
                raise TypeError(f"Expected {Level.list()}. Got {self.level}.")

        return text_desc
