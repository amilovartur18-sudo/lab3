"""Сохранение каталога и атомарная загрузка JSON формата версии 1."""

import json
from dataclasses import asdict
from pathlib import Path

from src.catalog import Catalog
from src.constants import FORMAT_VERSION, JSON_INDENT, PART_FIELDS
from src.errors import (
    CatalogFileError,
    CorruptedFileError,
    DuplicateIdError,
    InvalidPartError,
    UnsupportedVersionError,
)
from src.part import AviationPart


def save_catalog(catalog: Catalog, path: str | Path) -> None:
    """Записать версию формата и все поля деталей в UTF-8 JSON."""
    document = {
        "format_version": FORMAT_VERSION,
        "items": [asdict(item) for item in catalog],
    }
    try:
        Path(path).write_text(
            json.dumps(document, ensure_ascii=False, indent=JSON_INDENT) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        raise CatalogFileError(f"Не удалось сохранить каталог: {path}.") from error


def part_from_record(record: object, index: int) -> AviationPart:
    """Проверить структуру одной записи JSON и создать предметный объект."""
    if not isinstance(record, dict) or set(record) != set(PART_FIELDS):
        raise CorruptedFileError(f"Запись {index}: неверный набор полей детали.")
    try:
        return AviationPart(**record)
    except (TypeError, InvalidPartError) as error:
        raise CorruptedFileError(f"Запись {index}: {error}") from error


def parse_document(document: object) -> list[AviationPart]:
    """Проверить корневую структуру, версию формата и каждую запись документа."""
    if not isinstance(document, dict):
        raise CorruptedFileError("Корень JSON должен быть объектом.")
    version = document.get("format_version")
    if type(version) is not int:
        raise CorruptedFileError("format_version должен быть целым числом.")
    if version != FORMAT_VERSION:
        raise UnsupportedVersionError(f"Версия формата {version} не поддерживается.")
    if set(document) != {"format_version", "items"}:
        raise CorruptedFileError("Ожидаются только поля format_version и items.")
    records = document["items"]
    if not isinstance(records, list):
        raise CorruptedFileError("Поле items должно быть списком.")
    return [part_from_record(record, index) for index, record in enumerate(records, 1)]


def load_catalog(catalog: Catalog, path: str | Path) -> None:
    """Полностью заменить каталог; при любой ошибке чтения/проверки сохранить его."""
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as error:
        raise CatalogFileError(f"Не удалось прочитать каталог: {path}.") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise CorruptedFileError("Файл не является корректным UTF-8 JSON.") from error

    items = parse_document(document)
    try:
        catalog.replace_all(items)
    except DuplicateIdError as error:
        raise CorruptedFileError("В файле повторяется ID детали.") from error
