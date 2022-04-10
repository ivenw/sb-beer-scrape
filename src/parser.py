from typing import Protocol, Callable
from dataclasses import dataclass
import pandas as pd
from alive_progress import alive_bar, alive_it
from bs4 import BeautifulSoup as bs, ResultSet, Tag
from pydantic.main import ModelMetaclass


@dataclass
class Item(Protocol):
    ...


class CssSelectorParser(Protocol):
    def __init__(self):
        self.beers: list
        self.data: pd.DataFrame

    def parse_container(self, container: Tag) -> None:
        ...

    def turn_items_to_frame(self) -> None:
        ...

    def clean_up_frame(self) -> None:
        ...


def load_page_source_file(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()


def turn_page_into_soup(page_source: str) -> bs:
    with alive_bar(total=1, title="Parsing soup...", bar=None) as bar:
        soup = bs(page_source, "html.parser")
        bar(1)
    return soup


def parse_containers(
    containers: ResultSet[Tag], parser: CssSelectorParser
) -> pd.DataFrame:
    for container in alive_it(containers, title="Parsing containers..."):
        parser.parse_container(container)

    parser.turn_items_to_frame()
    parser.clean_up_frame()

    return parser.data


def items_to_dataframe(items: dict[str, str | None]) -> pd.DataFrame:
    df = pd.DataFrame(items)
    return df
