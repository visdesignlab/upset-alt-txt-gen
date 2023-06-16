import argparse
import os
import sys

from alttxt.generic import Grammar
from alttxt.generic import RawData
from alttxt.generator import AltTxtGen
from alttxt.tokenmap import TokenMap

from alttxt.types import Granularity
from alttxt.types import Level
from alttxt.types import Orientation

from pathlib import Path
from typing import Optional

# Entry point for the program
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

    args = parser.parse_args(argv)

    rawdata = RawData(Path(args.data)).model
    grammar = Grammar(Path(args.grammar)).model
    tokenMap = TokenMap(rawdata, grammar, Orientation.VERTICAL)
    alttext = AltTxtGen(
        args.level, args.granularity, tokenMap, grammar
    )

    print(90 * "-")
    print(
        f"DATASET={os.path.basename(args.data)}\tGRAMMAR={args.grammar}\tLEVEL={args.level.value}\tGRANULARITY={args.granularity.value}"
    )
    print(90 * "-")
    print(alttext.text)

    return 0


if __name__ == "__main__":
    SystemExit(main())