import argparse
import os
import re
import sys

from alttxt import phrases

from alttxt.generic import RawData
from alttxt.generic import Grammar

from alttxt.models import DataModel
from alttxt.models import GrammarModel
from alttxt.types_ import Granularity
from alttxt.types_ import Level
from alttxt.types_ import Orientation

from pprint import pprint
from pathlib import Path
from typing import cast
from typing import Optional

from matplotlib import pyplot as plt
from upsetplot import from_memberships
from upsetplot import plot


plt.rcParams["font.size"] = 8
plt.rcParams["text.usetex"] = True
plt.rcParams["toolbar"] = "None"


Model = DataModel | GrammarModel


class AltTxt:
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
                        r"{{list_max_set_names}}",
                        f'{", ".join(list(max_sets)[:-1])} and {list(max_sets)[-1]}',
                        text_desc,
                    )
                else:
                    text_desc = re.sub(
                        r"{{list_max_set_names}}",
                        f"only {list(max_sets).pop()}",
                        text_desc,
                    )

                if len(min_sets) > 1:
                    text_desc = re.sub(
                        r"{{list_min_set_names}}",
                        f'{", ".join(list(min_sets)[:-1])} and {list(min_sets)[-1]}',
                        text_desc,
                    )
                else:
                    text_desc = re.sub(
                        r"{{list_min_set_names}}",
                        f"only {list(min_sets).pop()}",
                        text_desc,
                    )

            case Level.THREE:
                text_desc = self.descriptions[f"level_{Level.THREE.value}"][
                    self.granularity.value
                ]

            case _:
                raise TypeError(f"Expected {Level.list()}. Got {self.level}.")

        return text_desc


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog="alttxt", add_help=False)

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s 0.1",
        help="Show program version number and exit.",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )
    parser.add_argument(
        "-D",
        "--data",
        required=True,
        type=Path,
        help="Relative path to data file.",
    )
    parser.add_argument(
        "-G",
        "--grammar",
        required=True,
        type=Path,
        help="Relative path to grammar file.",
    )
    parser.add_argument(
        "-l",
        "--level",
        type=Level,
        choices=list(Level),
        default=Level.ONE,
        help="Semantic level. Defaults to %(default)s.",
    )
    parser.add_argument(
        "-g",
        "--granularity",
        type=Granularity,
        choices=list(Granularity),
        default=Granularity.MEDIUM,
        help="Alt-text granularity. Defaults to %(default)s.",
    )
    parser.add_argument(
        "--show-plot",
        action="store_true",
        default=False,
        help="Shows UpSet plot. Defaults to %(default)s.",
    )

    args = parser.parse_args(argv)

    rawdata = RawData(Path(args.data)).model
    grammar = Grammar(Path(args.grammar)).model
    alttext = AltTxt(
        Orientation.VERTICAL, rawdata, grammar, args.level, args.granularity
    )

    print(100 * "-")
    print(
        f"DATASET={os.path.basename(args.data)}\tGRAMMAR={args.grammar}\t\tLEVEL={args.level.value}\t\tGRANULARITY={args.granularity.value}"
    )
    print(100 * "-")
    print(alttext.text)

    if args.show_plot:
        fig_1, fig_2 = plt.figure(), plt.figure()
        membership_cardinality = from_memberships(rawdata.membs, data=rawdata.count)
        membership_deviation = from_memberships(rawdata.membs, data=rawdata.devs)
        plot(membership_cardinality, fig=fig_1, orientation=alttext.orientation)
        plot(membership_deviation, fig=fig_2, orientation=alttext.orientation)
        plt.show()

    return 0


if __name__ == "__main__":
    SystemExit(main())
