import re

from alttxt import phrases
from alttxt.models import GrammarModel

from alttxt.types import Granularity
from alttxt.types import Level
from alttxt.tokenmap import TokenMap


class AltTxtGen:
    def __init__(
        self,
        level: Level,
        granularity: Granularity,
        map: TokenMap,
        grammar: GrammarModel,
    ) -> None:
        self.descriptions = phrases.DESCRIPTIONS
        self.granularity = granularity
        self.level = level
        self.map = map
        self.grammar = grammar

    def quantiles(self) -> list[list[float]]:
        quants: list[list[float]] = []
        return quants

    @property
    def text(self) -> str:
        text_desc = ""

        # Get the description template for the level, granularity, sort, and aggregation
        match self.level:
            # L0 and L1 don't care about sort/aggregation
            case Level.ZERO:
                text_desc = self.descriptions["level_0"][
                    self.granularity.value
                ]

            case Level.ONE:
                text_desc = self.descriptions["level_1"][
                    self.granularity.value
                ]

            case Level.TWO:
                # L2 cares about sort
                text_desc = self.descriptions["level_2"]["sort"][self.grammar["sort_by"]]
                # And aggregation
                text_desc += self.descriptions["level_2"]["aggregation"][self.grammar["first_aggregate_by"]]
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
        # First, loop until all non-terminals are replaced.
        while "[[" in text:
            tokens = re.split(r"\[\[|\]\]", text)
            isToken = text.lstrip().startswith("[[")
            result = list()

            for token in tokens:
                if isToken:
                    result.append(self.descriptions["symbols"][token])
                else:
                    result.append(token)
                isToken = not isToken
            
            text = "".join(result)

        # Now, loop and replace all terminals.
        while "{{" in text:
            tokens = re.split(r"{{|}}", text)
            isToken = text.lstrip().startswith("{{")
            result = list()

            for token in tokens:
                if isToken:
                    result.append(self.map.get_token(token))
                else:
                    result.append(token)
                isToken = not isToken
            
            text = "".join(result)
        
        #TODO: Capitalize first letter of each sentence.

        return text
