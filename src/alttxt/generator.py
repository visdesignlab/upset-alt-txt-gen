import re
from typing import Pattern

from alttxt import phrases
from alttxt.models import GrammarModel

from alttxt.enums import Explanation, Verbosity, Level
from alttxt.tokenmap import TokenMap
from alttxt.glossary import Glossary

from typing import Any

import json


class AltTxtGen:
    def __init__(
        self,
        level: Level,
        structured: bool,
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
        self.level: Level = level
        self.structured: bool = structured
        self.map: TokenMap = map
        self.grammar: GrammarModel = grammar

    @property
    def text(self) -> str:
        # Start with the UpSet explanation, if any
        text_desc: str = ""

        # Get the description template for the level, verbosity, and sort
        # L0 and L1 don't care about sort/aggregation

        if self.level == Level.ONE:
            text_desc += self.descriptions["level_1"]["upset_introduction"]
            text_desc += self.descriptions["level_1"]["dataset_properties"]

        elif self.level == Level.TWO:
            text_desc += self.descriptions["level_2"]["set_description"]
            text_desc += self.descriptions["level_2"]["intersection_description"]
            text_desc += self.descriptions["level_2"]["statistical_information"]

        elif self.level == Level.DEFAULT:
            # Default level is combination of L1 and L2

            # A short alternative text description
            altText = self.descriptions["AltText"]

            # A short description of the technique used in plot visualization
            technique = self.descriptions["level_1"]["technical_description"]

            # Structured text starts here
            introduction = self.descriptions["level_1"]["upset_introduction"]
            text_desc += introduction
            text_desc += " "

            dataset_properties = self.descriptions["level_1"]["dataset_properties"]
            text_desc += dataset_properties
            text_desc += " "

            set_description = self.descriptions["level_2"]["set_description"]
            text_desc += set_description
            text_desc += " "

            query_and_filters = self.descriptions["level_2"]["queries_and_filters"]
            text_desc += query_and_filters
            text_desc += " "

            selection_description = self.descriptions["level_2"]["selection_description"]
            text_desc += selection_description
            text_desc += " "

            intersection_description = self.descriptions["level_2"][
                "intersection_description"
            ]
            text_desc += intersection_description
            text_desc += " "

            statistical_information = self.descriptions["level_2"][
                "statistical_information"
            ]
            text_desc += statistical_information
            text_desc += " "

            trend_analysis = self.descriptions["level_3"]["trend_analysis"]
            text_desc += trend_analysis
            text_desc += " "

            if self.structured:
                # Helper function to replace periods with newlines and bullet points
                def add_bullet_points(text: str) -> str:
                    # add bullet point to the first sentence
                    text = "* " + text.strip()

                    parts = text.split('. ')

                    if len(parts) > 1:
                        # add \n* to each part except the last one, and only add * to the first one
                        p = parts[0] + ".\n* " + ("\n* ".join(parts[1:]))
                        return p
                    else:
                        return text

                try:
                    # Construct the dictionary for markdown content
                    data_to_write_as_md = {}
                    data_to_write_as_md["UpSet Introduction"] = self.replaceTokens(introduction)
                    data_to_write_as_md["Dataset Properties"] = self.replaceTokens(dataset_properties)
                    data_to_write_as_md["Queries and Filters"] = add_bullet_points(self.replaceTokens(query_and_filters))
                    if self.grammar.selection_type == 'row' or len(self.grammar.bookmarked_intersections) > 0: 
                        data_to_write_as_md["Intersection Selection"] = self.replaceTokens(selection_description)
                    data_to_write_as_md["Set Properties"] = add_bullet_points(self.replaceTokens(set_description))
                    data_to_write_as_md["Intersection Properties"] = add_bullet_points(self.replaceTokens(intersection_description))
                    data_to_write_as_md["Statistical Information"] = add_bullet_points(self.replaceTokens(statistical_information))
                    data_to_write_as_md["Trend Analysis"] = add_bullet_points(self.replaceTokens(trend_analysis))
                except Exception as e:
                    print(f"Exception while constructing markdown content: {str(e)}")

                markdown_content = ""
                for section, content in data_to_write_as_md.items():
                    markdown_content += f"# {section}\n{content}\n\n"

                # add glossary to markdown_content, from glossary.json
                markdown_content += "# Glossary\n"
                for term, definition in Glossary.items():
                    markdown_content += f"* **{term}**: {definition}\n"

                final_output = {
                    "techniqueDescription": self.replaceTokens(technique),
                    "shortDescription": self.replaceTokens(altText),
                    "longDescription": markdown_content,
                }

                # return the structured final output as a json content
                return final_output

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
        match: Pattern[str] = re.compile(r"((?<=[\.\?!]\s)(\w+)|(^\w+))")

        def cap(match) -> str:
            return match.group().capitalize()

        return match.sub(cap, text)
