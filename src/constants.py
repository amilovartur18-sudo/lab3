"""Общие константы приложения."""

FORMAT_VERSION: int = 1
MIN_YEAR: int = 1903
MAX_YEAR: int = 9999
DEFAULT_CATALOG_FILE: str = "catalog.json"
JSON_INDENT: int = 2
PART_FIELDS: tuple[str, ...] = (
    "item_id",
    "name",
    "category",
    "year",
    "manufacturer",
    "aircraft_model",
)
TEXT_FIELDS: tuple[str, ...] = tuple(field for field in PART_FIELDS if field != "year")
