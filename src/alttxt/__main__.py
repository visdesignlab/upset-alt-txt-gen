import argparse
from lib2to3.pgen2 import grammar
import os
from pprint import pprint
import sys

from alttxt.generator import AltTxtGen
from alttxt.models import DataModel, GrammarModel
from alttxt.parser import Parser
from alttxt.tokenmap import TokenMap

from alttxt.enums import Verbosity
from alttxt.enums import Level
from alttxt.enums import Orientation

from pathlib import Path
from typing import Optional

# Entry point for the program
def main(argv: Optional["list[str]"] = None) -> int:
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
        "-l",
        "--level",
        type=Level,
        choices=list(Level),
        default=Level.ONE,
        help="Semantic level. Defaults to %(default)s.",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        type=Verbosity,
        choices=list(Verbosity),
        default=Verbosity.MEDIUM,
        help="Alt-text verbosity. Defaults to %(default)s.",
    )

    args = parser.parse_args(argv)

    
    upset_parser: Parser = Parser(Path(args.data))
    grammar: GrammarModel = upset_parser.get_grammar()
    data: DataModel = upset_parser.get_data()

    tokenMap = TokenMap(data, grammar, Orientation.VERTICAL)
    
    alttext = AltTxtGen(
        args.level, args.verbosity, tokenMap, grammar
    )

    print(90 * "-")
    print(
        f"DATASET={os.path.basename(args.data)}\tLEVEL={args.level.value}\tGRANULARITY={args.verbosity.value}"
    )
    print(90 * "-")
    print(alttext.text)

    return 0


if __name__ == "__main__":
    SystemExit(main())