import asyncio
from email import parser
import logging
import functools
from typing import Awaitable, Callable, Coroutine, Iterable, Any, List

import numpy as np
import pandas as pd
from alive_progress import alive_bar, alive_it
from bs4 import BeautifulSoup as bs
from pydantic import BaseModel

BEER_CONTAINER: str = ".css-fmawtr.e1yt52hj6"
BEER_SELECTORS: dict[str, str] = {
    "url": ".css-fmawtr.e1yt52hj6",
    "picture_url": ".css-r8u85c.ecqr8e60",
    "style": ".css-1asvk4j.e1f2zvku0",
    "brewery": ".css-rh4jwl.e1yt52hj7",
    "name": ".css-4t8tuz.e1yt52hj7",
    "id": ".css-b2o0pl.e1yt52hj7",
    "country_of_origin": ".css-1sf43kc.e1f2zvku0:nth-child(1)",
    "volume": ".css-1sf43kc.e1f2zvku0:nth-child(2)",
    "abv": ".css-1sf43kc.e1f2zvku0:nth-child(3)",
    "price": ".css-1l6tt3v.e1f2zvku0",
    "bitterness": ".css-1o1jj0l.eof5z0g0:nth-child(1) > .css-1z0jnr4.e16t9rkf0",
    "body": ".css-1o1jj0l.eof5z0g0:nth-child(1) > .css-1z0jnr4.e16t9rkf0",
    "sweetness": ".css-1o1jj0l.eof5z0g0:nth-child(1) > .css-1z0jnr4.e16t9rkf0",
    "description": ".css-1qrr7kn.e1f2zvku0",
    "food_recommendation": ".css-1pnp1bx.eof5z0g0",
}


class Beer(BaseModel):
    id: int | None = None
    url: str | None = None
    picture_url: str | None = None
    brewery: str | None = None
    name: str | None = None
    style: str | None = None
    country_of_origin: str | None = None
    volume: int | None = None
    abv: float | None = None
    price: float | None = None
    bitterness: int | None = None
    body: int | None = None
    sweetness: int | None = None
    description: str | None = None
    food_recommendation: list[str] | None = None


def load_page_source_file(file_path: str) -> str:
    with alive_bar(total=1, title="Loading page source...", bar=None) as bar:
        with open(file_path, "r") as f:
            bar(1)
            return f.read()


def get_parser(key: str, selector: str) -> functools.partial[Coroutine]:
    if key in ["bitterness", "body", "sweetness"]:
        return functools.partial(_taste_parser, selector)

    elif key == "food_recommendation":
        return functools.partial(_recommendation_parser, selector)

    elif key == "volume":
        return functools.partial(_volume_parser, selector)

    elif key == "abv":
        return functools.partial(_abv_parser, selector)

    elif key == "price":
        return functools.partial(_price_parser, selector)

    elif key == "url":
        return _url_parser

    elif key in ["picture_url"]:
        return functools.partial(_image_url_parser, selector)

    elif key == "id":
        return functools.partial(_id_parser, selector)

    else:
        return functools.partial(_text_parser, selector)


async def _taste_parser(selector: str, beer_container: bs) -> int | None:
    try:
        return int(
            beer_container.select_one(selector).get("type").replace("taste-clock-", "")
        )
    except AttributeError:
        return None


async def _recommendation_parser(selector: str, beer_container: bs) -> list[str]:
    try:
        return [
            food_recommendation.get_text()
            for food_recommendation in beer_container.select(selector)
        ]
    except AttributeError:
        return None


async def _volume_parser(selector: str, beer_container: bs) -> int:
    return int(beer_container.select_one(selector).text.strip(" ml"))


async def _price_parser(selector: str, beer_container: bs) -> float:
    return float(
        beer_container.select_one(selector)
        .text.strip("*")
        .replace(":", ".")
        .replace("-", "0")
    )


async def _abv_parser(selector: str, beer_container: bs) -> float:
    return float(beer_container.select_one(selector).text.strip(" %").replace(",", "."))


async def _url_parser(beer_container: bs) -> str:
    return beer_container.get("href")


async def _image_url_parser(selector, beer_container: bs) -> str | None:
    try:
        return beer_container.select_one(selector).get("src")
    except AttributeError:
        return None


async def _id_parser(selector: str, beer_container: bs) -> int:
    return int(beer_container.select_one(selector).text.replace("Nr ", ""))


async def _text_parser(selector: str, beer_container: bs) -> str:
    try:
        return beer_container.select_one(selector).text.strip()
    except AttributeError:
        return None


def create_selector_parsers(selector_map: dict[str, str]) -> list[Callable]:
    return [get_parser(key, value) for key, value in selector_map.items()]


def beers_to_dataframe(beers: dict[str, str | int | float | None]) -> pd.DataFrame:
    df = pd.DataFrame(beers)
    return df


async def main():
    page_source = load_page_source_file("data/page_source.html")

    with alive_bar(total=1, title="Parsing soup...", bar=None) as bar:
        soup = bs(page_source, "html.parser")
        bar(1)

    parsers = create_selector_parsers(BEER_SELECTORS)

    beer_containers = soup.select(BEER_CONTAINER)

    beers = []
    for beer_container in alive_it(beer_containers, title="Parsing beers..."):
        print(*await asyncio.gather(*[i(beer_container) for i in parsers]))

    # df = beers_to_dataframe(beers)
    # df.to_csv("data/beers.csv", index=False)


if __name__ == "__main__":
    asyncio.run(main())
