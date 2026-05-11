from custom_components.stpatrick_residence.api import br_to_nl, clean_text, extract_items, remap_item

from . import DINNER_APPETIZER, LUNCH, LUNCH_DESSERT


def test_clean_text():
    assert clean_text(
        '<div class="dateInfos_title">Entr\u00e9e</div>\nChampignons et Bleu d\'Auvergne',
    ) == "Entr\u00e9e\nChampignons et Bleu d'Auvergne"


def test_br_to_nl():
    assert br_to_nl("Soupe aux lentilles<br /><br />1. Foie de veau oignons et bacon<br />2. Orzotto aux crevettes<br />") == "Soupe aux lentilles\n\n1. Foie de veau oignons et bacon\n2. Orzotto aux crevettes\n"


def test_remap_item() -> None:
    assert remap_item(DINNER_APPETIZER) == ("dinner", {"appetizer": "Champignons et Bleu d'Auvergne"})
    assert remap_item(LUNCH) == ("lunch", {"appetizer": "Soupe aux lentilles", "choice_1": "Foie de veau oignons et bacon", "choice_2": "Orzotto aux crevettes", "dessert": "Pur\xe9e de pommes de terre et l\xe9gumes"})
    assert remap_item(LUNCH_DESSERT) == ("lunch", {"dessert": "Dessert du jour"})


def test_extract_items() -> None:
    text = """Soupe aux lentilles

    1. Foie de veau oignons et bacon
    2. Orzotto aux crevettes
    Purée de pommes de terre et légumes
    """
    assert extract_items(text) == {
        "appetizer": "Soupe aux lentilles",
        "choice_1": "Foie de veau oignons et bacon",
        "choice_2": "Orzotto aux crevettes",
        "dessert": "Purée de pommes de terre et légumes",
    }
