from pprint import pprint
import re

from alttxt import phrases
from alttxt.models import GrammarModel

from alttxt.types import Verbosity, Level
from alttxt.tokenmap import TokenMap


class AltTxtGen:
    def __init__(
        self,
        level: Level,
        verbosity: Verbosity,
        map: TokenMap,
        grammar: GrammarModel,
    ) -> None:
        self.descriptions = phrases.DESCRIPTIONS
        self.verbosity = verbosity
        self.level = level
        self.map = map
        self.grammar = grammar

    def quantiles(self) -> list[list[float]]:
        quants: list[list[float]] = []
        return quants

    @property
    def text(self) -> str:
        text_desc: str = ""

        # Get the description template for the level, verbosity, and sort
        match self.level:
            # L0 and L1 don't care about sort/aggregation
            case Level.ZERO:
                text_desc = self.descriptions["level_0"][
                    self.verbosity.value
                ]

            case Level.ONE:
                text_desc = self.descriptions["level_1"][
                    self.verbosity.value
                ]

            case Level.TWO:
                # Only low and medium care about sort; high is always the same
                if self.verbosity != Verbosity.HIGH:
                    text_desc = self.descriptions["level_2"]\
                        [self.verbosity.value][self.grammar.sort_by]
                else:
                    text_desc = self.descriptions["level_2"]["high"]
                
            case _:
                raise TypeError(f"Expected {Level.list()}. Got {self.level}.")

        return self.replaceTokens(text_desc)

    def replaceTokens(self, text: str) -> str:
        """
        Replace tokens in the text with their corresponding values,
        as defined in self.map.
        Non-terminals, evaluated by the phrases mapping, are replaced first.
        Next, terminals are evaluated by the token map.
        """
        text = text.strip()

        # First, loop until all non-terminals are replaced.
        while "[[" in text:
            tokens: list[str] = re.split(r"\[\[|\]\]", text)
            isToken: bool = text.startswith("[[")
            result = list()

            # Bugfix for empty first token throwing off count
            if tokens[0] == "":
                tokens = tokens[1:]

            for token in tokens:
                if isToken:
                    result.append(self.descriptions["symbols"].get(token, ""))
                else:
                    result.append(token)
                isToken = not isToken
            
            text = "".join(result)

        # Now, loop and replace all terminals.
        while "{{" in text:
            tokens = re.split(r"{{|}}", text)
            isToken = text.lstrip().startswith("{{")
            result = list()

            # Bugfix for empty first token throwing off count
            if tokens[0] == "":
                tokens = tokens[1:]

            for token in tokens:
                if isToken:
                    result.append(str(self.map.get_token(token)))
                else:
                    result.append(token)
                isToken = not isToken
            
            text = "".join(result)

        # Capitalize the first letter of each sentence, and add a period to the end
        return self.cap_sentences(text)

    def cap_sentences(self, text: str) -> str:
        """
        Capitalize the first letter of each sentence in the provided string.
        Not the most robust implementation; may produce incorrect capitalizations
        after abbreviations, etc.
        """
        match = re.compile(r'((?<=[\.\?!]\s)(\w+)|(^\w+))')

        def cap(match):
            return match.group().capitalize()

        return match.sub(cap, text)
