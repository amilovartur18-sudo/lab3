"""Предметная модель авиационной детали."""

from dataclasses import dataclass

from src.constants import MAX_YEAR, MIN_YEAR, TEXT_FIELDS
from src.errors import InvalidPartError


@dataclass(frozen=True)
class AviationPart:
    """Неизменяемая деталь; уникальность item_id обеспечивает каталог."""

    item_id: str
    name: str
    category: str
    year: int
    manufacturer: str
    aircraft_model: str

    def __post_init__(self) -> None:
        """Проверить типы и значения, убрать внешние пробелы в строках."""
        for field_name in TEXT_FIELDS:
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise InvalidPartError(
                    f"Поле {field_name} должно быть непустой строкой."
                )
            object.__setattr__(self, field_name, value.strip())

        if type(self.year) is not int or not MIN_YEAR <= self.year <= MAX_YEAR:
            raise InvalidPartError(
                f"Год должен быть целым числом от {MIN_YEAR} до {MAX_YEAR}."
            )
