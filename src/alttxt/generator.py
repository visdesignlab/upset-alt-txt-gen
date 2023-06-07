import re

from alttxt import phrases

from alttxt.types import Granularity
from alttxt.types import Level
from alttxt.tokenmap import TokenMap


class AltTxtGen:
    def __init__(
        self,
        level: Level,
        granularity: Granularity,
        map: TokenMap,
    ) -> None:
        self.descriptions = phrases.DESCRIPTIONS
        self.granularity = granularity
        self.level = level
        self.map = map

    def quantiles(self) -> list[list[float]]:
        quants: list[list[float]] = []
        return quants

    @property
    def text(self) -> str:
        text_desc = ""

        # Get the description template for the level and granularity
        match self.level:
            case Level.ZERO:
                text_desc = self.descriptions[f"level_{Level.ZERO.value}"][
                    self.granularity.value
                ]

            case Level.ONE:
                text_desc = self.descriptions[f"level_{Level.ONE.value}"][
                    self.granularity.value
                ]

            case Level.TWO:
                text_desc = self.descriptions[f"level_{Level.TWO.value}"][
                    self.granularity.value
                ]

            case Level.THREE:
                text_desc = self.descriptions[f"level_{Level.THREE.value}"][
                    self.granularity.value
                ]

            case _:
                raise TypeError(f"Expected {Level.list()}. Got {self.level}.")

        return self.replaceTokens(text_desc)

    def replaceTokens(self, text: str) -> str:
        """
        Replace tokens in the text with their corresponding values,
        as defined in self.map.
        """
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

        return text
