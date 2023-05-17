import argparse
import re
import sys

from alttxt import phrases

from alttxt.generic import RawData
from alttxt.generic import Grammar

from alttxt.models import DataModel
from alttxt.models import GrammarModel
from alttxt.types_ import Direction
from alttxt.types_ import Granularity
from alttxt.types_ import Level

from pathlib import Path
from typing import Optional


Model = DataModel | GrammarModel


class AltTxt:
    def __init__(
        self,
        direction: Direction,
        data_model: Model,
        grammar_model: Model,
        level: Level,
        granularity: Granularity
    ) -> None:
        self.direction = direction
        self.data_model = data_model
        self.grammar_model = grammar_model
        self.descriptions = phrases.DESCRIPTIONS
        self.level = level
        self.granularity = granularity

    def quantiles(self) -> list[list[float]]:
        quants: list[list[float]] = []
        return quants

    @property
    def text(self) -> str:
        text_desc = ''
        match self.level:
            case Level.ZERO.value:
                text_desc = self.descriptions[f'level_{Level.ZERO.value}'][self.granularity.value]

            case Level.ONE.value:
                text_desc = self.descriptions[f'level_{Level.ONE.value}'][self.granularity.value]
                # text_desc = re.sub(r'{caption}', f'{self.grammar.caption}', text_desc)
                # text_desc = re.sub(r'{title}', f'{self.grammar.title}', text_desc)
                text_desc = re.sub(r'\{total\}', f'{sum(self.data_model.count)}', text_desc)

            case Level.TWO.value:
                text_desc = self.descriptions[f'level_{Level.TWO.value}'][self.granularity.value]

            case Level.THREE.value:
                text_desc = self.descriptions[f'level_{Level.THREE.value}'][self.granularity.value]

            case _:
                raise TypeError(f'Expected {Level.list()}. Got {self.level}.')

        return text_desc


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog='alttxt', add_help=False)

    parser.add_argument(
        '-V', '--version',
        action='version',
        version='%(prog)s 0.1',
        help='Show program version number and exit.',
    )
    parser.add_argument(
        '-h', '--help',
        action='help',
        default=argparse.SUPPRESS,
        help='Show this help message and exit.',
    )
    parser.add_argument(
        '--data',
        required=True,
        type=Path,
        help='Relative path to data file.',
    )
    parser.add_argument(
        '--grammar',
        required=True,
        type=Path,
        help='Relative path to grammar file.',
    )
    parser.add_argument(
        '--level',
        type=Level,
        choices=list(Level), # Enum values here don't work unless listed. Argparser does support using Enum as actions
        default=Level.ONE.value,
        help='Semantic level for contextually aware alt-text. Defaults to %(default)s.',
    )
    parser.add_argument(
        '--granularity',
        type=Granularity,
        choices=list(Granularity),
        default=Granularity.MEDIUM.value,
        help='Alt-text granularity/specificity. Defaults to %(default)s.',
    )

    args = parser.parse_args(argv)

    rawdata = RawData(Path(args.data)).model
    grammar = Grammar(Path(args.grammar)).model
    alttext = AltTxt(Direction.HORIZONTAL, rawdata, grammar, args.level.value, args.granularity)

    print(alttext.text)

    # import pyupset as pyu
    # pyu.plot(rawdata)
    return 0


if __name__ == '__main__':
    SystemExit(main())
