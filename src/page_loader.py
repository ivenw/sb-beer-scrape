import logging
import math
import re
from typing import cast
from re import Match

from alive_progress import alive_bar
from playwright.sync_api import Page, Route, sync_playwright

ITEMS_PER_PAGE: int = 30
AGE_CHECK_SELECTOR: str = ".css-qw0trq"
COOKIE_ACCEPT_SELECTOR: str = ".css-1sa6t7h"
TOTAL_ITEMS_SELECTOR: str = ".css-gf0e7o"
MORE_BUTTON_SELECTOR: str = ".css-o1dwno.e3v8jw31 > button"


def block_bloat(route: Route) -> None:
    """Handle bloat by blocking all requests to css, images, and fonts."""
    excluded_resource_types = ["stylesheet", "image", "font"]
    if route.request.resource_type in excluded_resource_types:
        route.abort()
    else:
        route.continue_()


def confirm_age_cookies(page: Page) -> None:
    page.click(AGE_CHECK_SELECTOR)
    page.click(COOKIE_ACCEPT_SELECTOR)


def get_total_items(page: Page) -> int:
    pattern = re.compile(r"\d+")
    total_items_string = cast(str, page.locator(TOTAL_ITEMS_SELECTOR).text_content())
    return int(cast(Match[str], pattern.search(total_items_string)).group())


def exhaust_more_button(page: Page, total_items: int) -> None:
    total_item_groups = math.ceil(total_items / ITEMS_PER_PAGE)

    # TODO this is a problematic approach as it takes longer the further down
    # the page we go.
    with alive_bar(total=total_items, title="Loading page") as bar:
        for i in range(total_item_groups):
            try:
                page.click(MORE_BUTTON_SELECTOR)
                logging.info(f"Loaded item group {i+1} of {total_item_groups}")
                bar(ITEMS_PER_PAGE)
            except:
                logging.info("No more items to load.")
                bar(total_items % ITEMS_PER_PAGE)
                break


def save_page(page: Page, file_path: str) -> None:
    with open(file_path, "w") as f:
        f.write(page.content())


def load_page(page_url: str, output: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.route("**/*", block_bloat)
        page.goto(page_url)
        confirm_age_cookies(page)
        total_items = get_total_items(page)
        exhaust_more_button(page, total_items)
        save_page(page=page, file_path=output)
        browser.close()
