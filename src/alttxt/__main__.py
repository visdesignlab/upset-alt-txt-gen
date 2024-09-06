import argparse
import os
import sys

from alttxt.generator import AltTxtGen
from alttxt.models import DataModel, GrammarModel
from alttxt.parser import Parser
from alttxt.tokenmap import TokenMap

from alttxt.enums import Level

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
        default=Level.DEFAULT,
        help="Semantic level. Defaults to %(default)s.",
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        default=None,
        help="Title of the plot. Defaults to %(default)s.",
    )
    parser.add_argument(
        "-st",
        "--structured",
        action="store_true",
        help="Alt-text structured text with appropriate headers. Returns JSON file with structured text.",
    )

    parser.add_argument(
        "-pa",
        "--pattern-analysis",
        action="store_true",
        help="Generate and output a pattern analysis table.",
    )

    args: argparse.Namespace = parser.parse_args(argv)

    try:
        upset_parser: Parser = Parser(Path(args.data))
        grammar: GrammarModel = upset_parser.get_grammar()
        data: DataModel = upset_parser.get_data()
    except Exception as e:
        print(f"Exception while parsing: {str(e)}")
        return 1

    title: str = args.title

    tokenMap = TokenMap(data, grammar, title)

    alttext = AltTxtGen(args.level, args.structured, tokenMap, grammar)

    patterns = {
        "intersection_trend_analysis": tokenMap.get_token("intersection_trend_analysis"),
        "set_divergence": tokenMap.get_token("set_divergence"),
        "largest_factor": tokenMap.calculate_largest_factor(),
        "set_size": {
            "set_divergence": tokenMap.get_token("set_divergence"),
        },
        "intersection_degree": {
            "individual_set_presence": tokenMap.get_token("individual_set_presence"),
            "low_set_presence": tokenMap.get_token("low_set_presence"),
            "medium_set_presence": tokenMap.get_token("medium_set_presence"),
            "high_set_presence": tokenMap.get_token("high_set_presence"),
        },
        "special_intersections": {
            "no_set": tokenMap.get_token("empty_set_presence"),
            "all_set": tokenMap.get_token("all_set_presence"),
        },
        "intersection_size_distribution": {
            "trend": tokenMap.get_token("intersection_trend_analysis"),
        }
    }

    print(90 * "-")
    print(
        f"DATASET={os.path.basename(args.data)}\tLEVEL={args.level.value}\t"
        "VERBOSITY={args.verbosity.value}\tEXPLAIN_UPSET={args.explain_upset.value}\tTITLE={title}"
    )
    print(90 * "-")

    if args.pattern_analysis:
        print("PATTERN ANALYSIS")
        print(90 * "-")
        for key, value in patterns.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for k, v in value.items():
                    print(f"\t{k}: {v}")
            else:
                print(f"{key}: {value}")
        print(90 * "-")

    print("TEXT DESCRIPTION")
    print(90 * "-")
    print(alttext.text)

    return 0


if __name__ == "__main__":
    SystemExit(main())
