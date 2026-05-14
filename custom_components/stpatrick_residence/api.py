"""API for St Patrick's Residence."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import TYPE_CHECKING, NotRequired, TypedDict, cast

import httpx
from bs4 import BeautifulSoup
from googletrans import Translator

from .const import BASE_URL, MEAL_TYPE_MAPPING

if TYPE_CHECKING:

    class ContentItem(TypedDict):
        """Content item from the API."""

        IdContent: int
        DateStart: str
        DateEnd: str
        Title: str
        Timestamp: str
        Texte: str
        Texte2: str
        Image: str


class MenuMealData(TypedDict):
    """Menu meal data."""

    appetizer: NotRequired[str]
    dessert: NotRequired[str]
    choice_1: NotRequired[str]
    choice_2: NotRequired[str]


class MenuData(TypedDict):
    """Menu data."""

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


def extract_items(text: str, title: str = "") -> MenuMealData:
    """Extract items from text and format them as meal items."""
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
    return cast("MenuMealData", output)


def remap_item(item: ContentItem) -> tuple[str, MenuMealData]:
    """Remap the item to match the format of the menu."""
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


async def translate_meals(meal_data: MenuData) -> str:
    """TRranslate text to English."""
    async with Translator() as translator:
        for meal in meal_data.values():
            for key, text in meal.items():
                meal[key] = await translator.translate(text, "en", "fr")
        return meal_data


class LiveTourApi:
    """API for St Patrick's Residence internal site."""

    def __init__(self, client: httpx.AsyncClient, password: str) -> None:
        """Set credentials and cookies."""
        self._client = client
        self._password = password
        self._cookies: httpx.Cookies = httpx.Cookies()

    async def login(self) -> None:
        """Perform the login flow on the session."""
        credentials = {"email": "", "login": "1", "passwd": self._password}

        # Post to login-check endpoint
        r = await self._client.post(f"{BASE_URL}/actions/login.check.ajax.php", data=credentials, cookies=self._cookies)
        r.raise_for_status()

        if r.content != b"success":
            raise ValueError("Login Failed")

        # Now post again to index to get visitor ID Cookie
        r = await self._client.post(
            f"{BASE_URL}/index", data=credentials,
        )
        r.raise_for_status()

        # Store cookies with credentials
        self._cookies.update(r.cookies)

    async def get_menu(self) -> bytes:
        """Get the raw menu html."""
        r = await self._client.get(
            f"{BASE_URL}/load/residenceinfos-contents?section=menus",
            cookies=self._cookies,
        )
        r.raise_for_status()
        return r.content

    async def get_menu_for_date(self, date_str: str) -> MenuData:
        """Get the menu for a specific date."""
        content = await self.get_menu()
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

        menu: MenuData = defaultdict(dict)
        for item in sorted(today, key=lambda x: x["DateStart"]):
            title, remapped_item = remap_item(item)
            menu[title] |= remapped_item
        return menu
