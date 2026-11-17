"""Общие фикстуры для создания каталогов и деталей."""

from collections.abc import Callable
from typing import Any

import pytest

from src.catalog import Catalog
from src.part import AviationPart


@pytest.fixture
def make_part() -> Callable[..., AviationPart]:
    """Дать фабрику с допустимыми значениями и возможностью подменить любое поле."""

    def create_part(**changes: Any) -> AviationPart:
        """Создать деталь, включая намеренно ошибочные данные для тестов."""
        fields: dict[str, Any] = {
            "item_id": "ENG-001",
            "name": "Лопатка турбины",
            "category": "Двигатель",
            "year": 2024,
            "manufacturer": "Учебный завод",
            "aircraft_model": "Учебный самолёт А",
        }
        fields.update(changes)
        return AviationPart(**fields)

    return create_part


@pytest.fixture
def catalog() -> Catalog:
    """Создать независимый пустой каталог для каждого теста."""
    return Catalog()
