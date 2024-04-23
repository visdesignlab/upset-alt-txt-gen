from pathlib import Path
import pytest

from alttxt.parser import Parser

def test_practice():
    parser = Parser(Path("data/movie.json"))
    assert parser is not None