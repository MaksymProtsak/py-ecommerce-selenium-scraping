import csv
from dataclasses import dataclass, fields
from urllib.parse import urljoin

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup, Tag

import requests
from selenium.webdriver.common.by import By

BASE_URL = "https://webscraper.io/"
HOME_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/")
COMPUTERS_ULR = urljoin(BASE_URL, "test-sites/e-commerce/more/computers/")
PHONES_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/phones/")
LAPTOPS_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/computers/laptops/")
TABLETS_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/computers/tablets/")
TOUCHES_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/phones/touch/")

LINKS_F_NAME = {
    HOME_URL: "home",
    COMPUTERS_ULR: "computers",
    PHONES_URL: "phones",
    LAPTOPS_URL: "laptops",
    TABLETS_URL: "tablets",
    TOUCHES_URL: "touch",
}


@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: int


PRODUCTS = [field.name for field in fields(Product)]


def create_page_link(base_url: str, next_page_url: str) -> str:
    return urljoin(base_url, next_page_url)


def get_soup_page(url: str) -> BeautifulSoup:
    res = requests.get(url, ).content
    soup = BeautifulSoup(res, "html.parser")
    return soup


def get_cards(soup_page: BeautifulSoup) -> list[Tag]:
    cards = soup_page.select(".card")
    return cards


def get_product_link(soup_card: Tag) -> str:
    return soup_card.select(".title")[0].attrs["href"]


def reviews_from_row(row: str) -> int:
    row = str(row).replace('\t', "").replace('\n', "").split()[0]
    return int(row)


def pars_single_card(card: Tag) -> Product:
    products = []
    card_link = get_product_link(card)
    product_full_link = create_page_link(BASE_URL, card_link)
    bs_page = get_soup_page(product_full_link)
    product_card = bs_page.select(".card")[0]

    # product_swatches = product_card.select(".btn.swatch")
    # swatchers_value = [
    #     swatcher["value"]
    #     for swatcher in product_swatches
    # ]
    # browser = Chrome()
    # browser.get(product_full_link)
    # buttons = browser.find_elements(By.CSS_SELECTOR, ".btn.swatch")
    # for button in buttons:
    #     button.click()
    #     price = browser.find_elements(By.CSS_SELECTOR, ".price")[0].text
    #     print(button.text, price)
    # breakpoint()

    title = card.select(".title")[0]["title"]
    description = card.select(".description")[0].contents[0]
    price = str(card.select(".price")[0].contents[0]).replace("$", "")
    review = product_card.select(".review-count")[0]
    r_count = reviews_from_row(review.text)
    r_rating = len(review.select(".ws-icon-star"))
    product = Product(
        title=str(title),
        description=str(description),
        price=float(price),
        rating=r_rating,
        num_of_reviews=r_count,
    )
    return product


def write_to_csv(products: list[Product], name) -> None:
    with open(f"{name}.csv", "w", newline="") as file:
        writer = csv.writer(file)
        for product in products:
            writer.writerow([product])


def get_all_products() -> None:
    page_link = create_page_link(HOME_URL, "")
    for page_link in (HOME_URL, COMPUTERS_ULR, PHONES_URL, LAPTOPS_URL, TABLETS_URL, TOUCHES_URL):
        bs_page = get_soup_page(page_link)
        cards = get_cards(bs_page)
        parsed_cards = [pars_single_card(card) for card in cards]
        f_name = LINKS_F_NAME[page_link]
        write_to_csv(parsed_cards, f_name)


if __name__ == "__main__":
    get_all_products()
