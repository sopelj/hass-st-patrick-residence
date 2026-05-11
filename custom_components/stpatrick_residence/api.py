"""API for St Patrick's Residence."""
from __future__ import annotations

import re
import json
from collections import defaultdict
from datetime import datetime
from typing import TYPE_CHECKING, cast

import requests
from bs4 import BeautifulSoup
from googletrans import Translator

from .const import BASE_URL, MEAL_TYPE_MAPPING

if TYPE_CHECKING:
    from typing import TypedDict, NotRequired
    from requests import Session

    class ContentItem(TypedDict):
        IdContent: int
        DateStart: str
        DateEnd: str
        Title: str
        Timestamp: str
        Texte: str
        Texte2: str
        Image: str

    class MenuItem(TypedDict):
        title: str
        content: str

    class MenuMealData(TypedDict):
        appetizer: NotRequired[str]
        dessert: NotRequired[str]
        choice_1: NotRequired[str]
        choice_2: NotRequired[str]

    class MenuData(TypedDict):
        lunch: MenuMealData
        dinner: MenuMealData


def br_to_nl(html) -> str:
    """Convert <br> tags to newlines."""
    return re.sub(r"<br\s?/?>", "\n", html)


def clean_text(html) -> str:
    """Remove HTML tags and extra whitespace."""
    html = br_to_nl(html)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text().strip()


def extract_items(text: str, title: str = "") -> Menu:
    items = [i for t in text.split("\n") if (i := t.strip())]
    output = {}
    for i, item in enumerate(items):
        if match := re.match(r"^([1-9])\.\s(.*)\b$", item):
            num, choice = match.groups()
            output[f"choice_{num}"] = choice
        elif "dessert" not in title and i == 0:
            output["appetizer"] = item
        else:
            output["dessert"] = item
    return cast("Menu", output)


def remap_item(item: ContentItem) -> tuple[str, MenuItem]:
    content = clean_text(item["Texte"])
    parts = content.split("\n")
    main_meal_type = "lunch" if item["DateStart"].endswith("13:00:00") else "dinner"
    other_type = main_meal_type

    if parts[0] in MEAL_TYPE_MAPPING:
        other_type = MEAL_TYPE_MAPPING.get(parts[0], main_meal_type)
        parts = parts[1:]
        content = "\n".join(parts)

    if parts and parts[0] in MEAL_TYPE_MAPPING:
        other_type = MEAL_TYPE_MAPPING.get(parts[0], main_meal_type)
        content = "\n".join(parts[1:])

    if (text_2 := item.get("Texte2")) and ((cleaned_2 := clean_text(text_2)) != content):
        content += f"\n\n{cleaned_2}\n"

    return main_meal_type, extract_items(content, other_type)


async def translate_item(text: str):
    return await translator.translate(content, src="fr", dest="en")


class LiveTourApi:
    def __init__(self, password: str) -> None:
        self._password = password
        self._session = requests.Session()

    def login(self) -> None:
        """Perform the login flow on the session."""
        credentials = {"email": "", "login": "1", "passwd": self._password}
        # Post to login-check endpoint
        r = self._session.post(
            f"{BASE_URL}/actions/login.check.ajax.php", data=credentials
        )
        r.raise_for_status()
        assert r.content == b"success"
        # Now post again to index to get visitor ID Cookie
        r = self._session.post(
            f"{BASE_URL}/index", data=credentials
        )
        r.raise_for_status()

    def get_menu(self) -> bytes:
        r = self._session.get(
            f"{BASE_URL}/load/residenceinfos-contents?section=menus",
        )
        r.raise_for_status()
        return r.content

    def get_menu_for_date(self, date_str: str) -> dict[str, str]:
        content = self.get_menu()
        soup = BeautifulSoup(content, "html.parser")
        if not (script_tag := soup.find("script")):
            raise ValueError("No soup found")

        menu_script = str(script_tag.contents[0])
        match = re.search(
            r"var allMessagesByDate = (.*?)(?=;)",
            menu_script.replace("\n", ""),
            re.MULTILINE,
        )
        if not match:
            raise ValueError("No menu found")

        data: dict[str, list[ContentItem]] = json.loads(match.group(1))
        if not (today := data.get(date_str)):
            raise ValueError("No menu found for this date")

        menu: dict[str, list[MenuData]] = defaultdict(dict)
        for item in sorted(today, key=lambda x: x["DateStart"]):
            title, remapped_item = remap_item(item)
            menu[title] |= remapped_item
        return menu
