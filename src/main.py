from cProfile import run
import parser
import page_loader
import pathlib
from beer import BeerParser
import pandas as pd

PAGE_SOURCE_FILE = "data/page_source.html"
SYSTEMBOLAGET_URL = "https://www.systembolaget.se/sok/?categoryLevel1=%C3%96l&page=1"
ITEMS_PER_PAGE: int = 30
AGE_CHECK_SELECTOR: str = ".css-qw0trq"
COOKIE_ACCEPT_SELECTOR: str = ".css-1sa6t7h"
TOTAL_ITEMS_SELECTOR: str = ".css-gf0e7o"
MORE_BUTTON_SELECTOR: str = ".css-o1dwno.e3v8jw31 > button"

BEER_CONTAINER: str = ".css-fmawtr.e1yt52hj6"


def main():
    if not pathlib.Path(PAGE_SOURCE_FILE).is_file():
        print("Page source file not found.")
        page_loader.load_page(page_url=SYSTEMBOLAGET_URL, output=PAGE_SOURCE_FILE)
    else:
        print("Page source file found.")

    page_source = parser.load_page_source_file(PAGE_SOURCE_FILE)
    soup = parser.turn_page_into_soup(page_source)

    containers = soup.select(BEER_CONTAINER)
    data = parser.parse_containers(containers, BeerParser())

    data.to_csv("data/beer_data.csv", index=False)


if __name__ == "__main__":
    main()
