"""Проверка инвариантов предметной модели."""

from collections.abc import Callable
from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from src.constants import MAX_YEAR, MIN_YEAR, TEXT_FIELDS
from src.errors import InvalidPartError
from src.part import AviationPart


def test_valid_part(make_part: Callable[..., AviationPart]) -> None:
    """Все обязательные поля сохраняются в dataclass."""
    item = make_part()
    assert is_dataclass(item)
    assert item.item_id == "ENG-001"
    assert item.name == "Лопатка турбины"
    assert item.category == "Двигатель"
    assert item.year == 2024
    assert item.manufacturer == "Учебный завод"
    assert item.aircraft_model == "Учебный самолёт А"


@pytest.mark.parametrize("field", TEXT_FIELDS)
@pytest.mark.parametrize("value", ["", " \t\n", None, 123, [], True])
def test_invalid_text_field(
    make_part: Callable[..., AviationPart], field: str, value: object
) -> None:
    """Пустые строки и неверные типы отклоняются предметной ошибкой."""
    with pytest.raises(InvalidPartError):
        make_part(**{field: value})


@pytest.mark.parametrize(
    "year", [MIN_YEAR - 1, MAX_YEAR + 1, True, "2024", 2024.5, None]
)
def test_invalid_year(make_part: Callable[..., AviationPart], year: object) -> None:
    """Год должен быть целым числом допустимого диапазона; bool не подходит."""
    with pytest.raises(InvalidPartError):
        make_part(year=year)


@pytest.mark.parametrize("year", [MIN_YEAR, MAX_YEAR])
def test_year_boundaries(make_part: Callable[..., AviationPart], year: int) -> None:
    """Обе границы диапазона включены."""
    assert make_part(year=year).year == year


def test_trim_and_string_id(make_part: Callable[..., AviationPart]) -> None:
    """Внешние пробелы удаляются, ведущие нули строкового ID сохраняются."""
    item = make_part(
        item_id=" 0017 ",
        name=" Лопатка ",
        category=" Двигатель ",
        manufacturer=" Завод ",
        aircraft_model=" Модель А ",
    )
    assert item.item_id == "0017"
    assert item.name == "Лопатка"
    assert item.category == "Двигатель"
    assert item.manufacturer == "Завод"
    assert item.aircraft_model == "Модель А"


@pytest.mark.parametrize("field", TEXT_FIELDS + ("year",))
def test_part_is_immutable(make_part: Callable[..., AviationPart], field: str) -> None:
    """Через полученный объект нельзя изменить ID или нарушить его инварианты."""
    with pytest.raises(FrozenInstanceError):
        setattr(make_part(), field, "changed")
