from dataclasses import dataclass
from parser import CssSelectorParser, Item
from bs4 import Tag


BEER_CONTAINER: str = ".css-fmawtr.e1yt52hj6"
BEER_SELECTORS: dict[str, str] = {
    # "url": ("link", ".css-fmawtr.e1yt52hj6"),
    "style": ".css-1asvk4j.e1f2zvku0",
    "picture_url": ".css-r8u85c.ecqr8e60",
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

# class Beer(BaseModel):
#     id: int | None = None
#     url: str | None = None
#     picture_url: str | None = None
#     brewery: str | None = None
#     name: str | None = None
#     style: str | None = None
#     country_of_origin: str | None = None
#     volume: int | None = None
#     abv: float | None = None
#     price: float | None = None
#     bitterness: int | None = None
#     body: int | None = None
#     sweetness: int | None = None
#     description: str | None = None
#     food_recommendation: list[str] | None = None


@dataclass
class Beer(Item):
    id: int | None
    # url: str | None
    picture_url: str | None
    brewery: str | None
    name: str | None
    style: str | None
    country_of_origin: str | None
    volume: int | None
    abv: float | None
    price: float | None
    bitterness: int | None
    body: int | None
    sweetness: int | None
    description: str | None
    food_recommendation: list[str] | None


class BeerParser(CssSelectorParser):
    def parse_container(self, container: Tag) -> Beer:
        beer = {}
        for key, selector in BEER_SELECTORS.items():
            try:
                selection = container.select(selector)
                if key == "picture_url":
                    beer[key] = selection[0].get("src")
                elif key == "id":
                    beer[key] = selection[0].get_text()
                elif key in ["bitterness", "body", "sweetness"]:
                    beer[key] = selection[0].get("type")
                elif key == "food_recommendation":
                    beer[key] = [food.get_text() for food in selection]

                else:
                    beer[key] = selection[0].get_text().strip()
            except:
                beer[key] = None
        return Beer(**beer)