"""Операции каталога, поиск и протоколы коллекции."""

from collections.abc import Callable
from typing import cast

import pytest

from src.catalog import Catalog
from src.errors import DuplicateIdError, InvalidPartError, ItemNotFoundError
from src.part import AviationPart


def test_add_get_remove(
    catalog: Catalog, make_part: Callable[..., AviationPart]
) -> None:
    """Добавленная деталь доступна по ID, удалённая больше не доступна."""
    item = make_part()
    catalog.add(item)
    assert catalog.get(item.item_id) is item
    assert len(catalog) == 1
    assert item.item_id in catalog
    catalog.remove(item.item_id)
    assert len(catalog) == 0
    assert item.item_id not in catalog
    with pytest.raises(ItemNotFoundError):
        catalog.get(item.item_id)


def test_duplicate_keeps_original(
    catalog: Catalog, make_part: Callable[..., AviationPart]
) -> None:
    """Повторный ID не заменяет исходную деталь и не меняет размер каталога."""
    original = make_part()
    catalog.add(original)
    with pytest.raises(DuplicateIdError):
        catalog.add(make_part(name="Другая деталь"))
    assert list(catalog) == [original]
    assert catalog.get(original.item_id) is original


def test_unknown_id(catalog: Catalog) -> None:
    """Для отсутствующего ID get и remove вызывают предметную ошибку."""
    with pytest.raises(ItemNotFoundError):
        catalog.get("missing")
    with pytest.raises(ItemNotFoundError):
        catalog.remove("missing")


def test_reject_wrong_object(catalog: Catalog) -> None:
    """Каталог отклоняет объект другого типа."""
    with pytest.raises(InvalidPartError):
        catalog.add(cast(AviationPart, object()))
    assert len(catalog) == 0


def test_search(catalog: Catalog, make_part: Callable[..., AviationPart]) -> None:
    """Поиск категории точный, названия - по подстроке без учёта регистра."""
    first = make_part()
    second = make_part(item_id="ENG-002", name="Корпус турбины")
    third = make_part(item_id="GEAR-001", name="Стойка шасси", category="Шасси")
    for item in (first, second, third):
        catalog.add(item)
    assert catalog.find_by_category(" Двигатель ") == (first, second)
    assert catalog.find_by_category("двигатель") == ()
    assert catalog.find_by_name(" ТУРБИНЫ ") == (first, second)
    assert catalog.find_by_name("стойка") == (third,)
    assert catalog.find_by_name("unknown") == ()
    assert catalog.find_by_category("unknown") == ()
    assert catalog.find_by_name("") == (first, second, third)


def test_unicode_casefold(make_part: Callable[..., AviationPart]) -> None:
    """Используется полное Unicode-сравнение без регистра."""
    item = make_part(name="Straße")
    assert Catalog([item]).find_by_name("STRASSE") == (item,)


def test_results_are_independent(
    catalog: Catalog, make_part: Callable[..., AviationPart]
) -> None:
    """Результаты поиска - неизменяемые снимки, независимые от каталога."""
    item = make_part()
    catalog.add(item)
    names = catalog.find_by_name("турбины")
    categories = catalog.find_by_category("Двигатель")
    assert isinstance(names, tuple) and isinstance(categories, tuple)
    separate_list = list(names)
    separate_list.clear()
    assert len(catalog) == 1
    catalog.remove(item.item_id)
    assert names == categories == (item,)


def test_iteration_order(make_part: Callable[..., AviationPart]) -> None:
    """Два перебора имеют один порядок; повторное добавление помещает в конец."""
    first = make_part(item_id="Z-2")
    second = make_part(item_id="A-1")
    catalog = Catalog([first, second])
    assert list(catalog) == list(catalog) == [first, second]
    catalog.remove(first.item_id)
    catalog.add(first)
    assert list(catalog) == [second, first]
    assert catalog.find_by_category(first.category) == (second, first)


def test_empty_catalog(catalog: Catalog) -> None:
    """Пустая коллекция поддерживает все протоколы и поиск."""
    assert len(catalog) == 0
    assert list(catalog) == []
    assert "missing" not in catalog
    assert [] not in catalog
    assert catalog.find_by_name("") == ()


def test_replace_all_is_atomic(make_part: Callable[..., AviationPart]) -> None:
    """Дубликат в конце новой коллекции сохраняет весь исходный каталог."""
    original = make_part(item_id="original")
    catalog = Catalog([original])
    with pytest.raises(DuplicateIdError):
        catalog.replace_all([make_part(), make_part()])
    assert list(catalog) == [original]
