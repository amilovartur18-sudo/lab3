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

ADD_COMMAND_EXAMPLE: str = (
    "Пример создания JSON-каталога и добавления первой детали:\n\n"
    "  python -m src.main --file demo_catalog.json add \\\n"
    "    --id DEMO-001 \\\n"
    '    --name "Лопатка турбины" \\\n'
    '    --category "Двигатель" \\\n'
    "    --year 2024 \\\n"
    '    --manufacturer "Учебный завод" \\\n'
    '    --aircraft-model "Учебный самолёт А"\n\n'
    "Если файла нет, он создаётся после успешного добавления детали.\n"
    "При повторном добавлении требуется новый уникальный ID."
)
