from fastapi import APIRouter
from fastapi import FastAPI
from pathlib import Path

from alttxt.types_ import Granularity
from alttxt.types_ import Level
from alttxt.types_ import Orientation

from alttxt.generic import Grammar
from alttxt.generic import RawData

from alttxt.generator import AltTxtGen

from typing import Any


app = FastAPI(title="An UpSet Plot Alt Text Generator")
api_router = APIRouter()


DATASETS = {
    "movies.json": RawData(Path("../../data/movies.json")).model,
    "simpson.json": RawData(Path("../../data/simpson.json")).model,
    "grammar.json": Grammar(Path("../../data/grammar.json")).model,
}


@api_router.get("/generate", status_code=200)
def generate(
    data: str,
    grammar: str,
    level: Level = Level.ONE,
    granularity: Granularity = Granularity.MEDIUM,
) -> dict[str, Any]:
    """Fetch GET"""
    data_model = DATASETS[data]
    grammar_model = DATASETS[grammar]
    alttext = AltTxtGen(
        Orientation.VERTICAL, data_model, grammar_model, level, granularity
    )
    return {
        "data": data_model,
        "grammar": grammar_model,
        "level": level.value,
        "granularity": granularity.value,
        "text": alttext.text,
    }


app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
