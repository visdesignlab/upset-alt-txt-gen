import re
from typing import Pattern

from alttxt import phrases
from alttxt.models import GrammarModel

from alttxt.enums import Explanation, Verbosity, Level
from alttxt.tokenmap import TokenMap

from typing import Any

class AltTxtGen:
    def __init__(
        self,
        level: Level,
        verbosity: Verbosity,
        explain: Explanation,
        map: TokenMap,
        grammar: GrammarModel,
    ) -> None:
        """
        Params:
        - level: The semantic level of the explanation to generate
        - verbosity: The verbosity of the explanation to generate
        - explain: How much of the UpSet explanation 
            (describing what an UpSet plot is) to include
        - map: The token map to use for replacing tokens in the description
        - grammar: The grammar model to use for generating the description
        """
        self.descriptions: "dict[str, Any]" = phrases.DESCRIPTIONS
        self.verbosity: Verbosity = verbosity
        self.level: Level = level
        # self.explain: Explanation = explain
        self.map: TokenMap = map
        self.grammar: GrammarModel = grammar

    @property
    def text(self) -> str:
        # Start with the UpSet explanation, if any
        # text_desc: str = self.descriptions["upset_desc"][self.explain]
        text_desc: str = ""
            
        # Get the description template for the level, verbosity, and sort
        # L0 and L1 don't care about sort/aggregation

        if self.level == Level.ONE:
            # text_desc += self.descriptions["level_1"][self.verbosity.value]
            text_desc += self.descriptions["level_1"]["upset_introduction"]
            text_desc += self.descriptions["level_1"]["dataset_properties"]

        elif self.level == Level.TWO:
            # L2 splits generation by sort type of the plot
            # text_desc += self.descriptions["level_2"]\
            #         [self.verbosity.value][self.grammar.sort_by]

            text_desc += self.descriptions["level_2"]["set_description"]
            text_desc += self.descriptions["level_2"]["intersection_description"]
            
        elif self.level == Level.DEFAULT:
            # Default level is combination of L1 and L2
            # text_desc += self.descriptions["level_1"][self.verbosity.value]
            text_desc += self.descriptions["level_1"]["upset_introduction"]
            text_desc += self.descriptions["level_1"]["dataset_properties"]
            text_desc += " "
            # text_desc += self.descriptions["level_2"]\
            #         [self.verbosity.value][self.grammar.sort_by]
            text_desc += self.descriptions["level_2"]["set_description"]
            text_desc += self.descriptions["level_2"]["intersection_description"]
            
        else:
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
            tokens: list[str] = re.split(r"{{|}}", text)
            isToken: bool = text.lstrip().startswith("{{")
            result: list[str] = list()

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
        match: Pattern[str] = re.compile(r'((?<=[\.\?!]\s)(\w+)|(^\w+))')

        def cap(match) -> str:
            return match.group().capitalize()

        return match.sub(cap, text)
