"""JSON round trip, валидация формата и атомарность загрузки."""

import json
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path

import pytest

from src.catalog import Catalog
from src.constants import FORMAT_VERSION, PART_FIELDS
from src.errors import CatalogFileError, CorruptedFileError, UnsupportedVersionError
from src.part import AviationPart
from src.storage import load_catalog, save_catalog


def write_document(tmp_path: Path, document: object) -> Path:
    """Записать произвольный JSON-документ для проверки загрузчика."""
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    return path


def test_round_trip(make_part: Callable[..., AviationPart], tmp_path: Path) -> None:
    """Все поля, строковые ID, Unicode и порядок переживают сохранение/загрузку."""
    items = [make_part(item_id="0017"), make_part(item_id="Z-2", name="Клапан")]
    path = tmp_path / "catalog.json"
    save_catalog(Catalog(items), path)
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document == {
        "format_version": FORMAT_VERSION,
        "items": [asdict(item) for item in items],
    }
    restored = Catalog([make_part(item_id="old")])
    load_catalog(restored, path)
    assert list(restored) == list(restored) == items
    assert "old" not in restored
    assert restored.get("0017") == items[0]


def test_empty_round_trip(
    make_part: Callable[..., AviationPart], tmp_path: Path
) -> None:
    """Загрузка пустого каталога удаляет прежнее содержимое."""
    path = tmp_path / "empty.json"
    save_catalog(Catalog(), path)
    catalog = Catalog([make_part()])
    load_catalog(catalog, path)
    assert len(catalog) == 0


@pytest.mark.parametrize("version", [0, FORMAT_VERSION + 1, -1])
def test_unsupported_version_is_atomic(
    make_part: Callable[..., AviationPart], tmp_path: Path, version: int
) -> None:
    """Неизвестная целочисленная версия отклоняется без изменения каталога."""
    item = make_part()
    catalog = Catalog([item])
    path = write_document(tmp_path, {"format_version": version, "items": []})
    with pytest.raises(UnsupportedVersionError):
        load_catalog(catalog, path)
    assert catalog.get(item.item_id) is item
    assert list(catalog) == [item]


@pytest.mark.parametrize(
    "document",
    [
        None,
        [],
        {},
        {"items": []},
        {"format_version": True, "items": []},
        {"format_version": "1", "items": []},
        {"format_version": FORMAT_VERSION},
        {"format_version": FORMAT_VERSION, "items": {}},
        {"format_version": FORMAT_VERSION, "items": [], "extra": 0},
    ],
)
def test_invalid_document_shape(
    make_part: Callable[..., AviationPart], tmp_path: Path, document: object
) -> None:
    """Неверные корень, версия и структура вызывают CorruptedFileError."""
    item = make_part()
    catalog = Catalog([item])
    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, write_document(tmp_path, document))
    assert list(catalog) == [item]


@pytest.mark.parametrize("field", PART_FIELDS)
@pytest.mark.parametrize("bad_value", [None, [], True])
def test_bad_second_record_is_atomic(
    make_part: Callable[..., AviationPart],
    tmp_path: Path,
    field: str,
    bad_value: object,
) -> None:
    """Ошибка типа во второй записи не удаляет старые и не добавляет новые детали."""
    original = make_part(item_id="old")
    catalog = Catalog([original])
    good_record = asdict(make_part(item_id="new-1"))
    bad_record = asdict(make_part(item_id="new-2"))
    bad_record[field] = bad_value
    path = write_document(
        tmp_path,
        {
            "format_version": FORMAT_VERSION,
            "items": [good_record, bad_record],
        },
    )
    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)
    assert list(catalog) == [original]
    assert catalog.get("old") is original
    assert "new-1" not in catalog


@pytest.mark.parametrize(
    "fault", ["missing", "extra", "blank", "duplicate", "not-object"]
)
def test_invalid_record_is_atomic(
    make_part: Callable[..., AviationPart], tmp_path: Path, fault: str
) -> None:
    """Ошибки полей и дубликат ID в середине файла сохраняют исходный каталог."""
    original = make_part(item_id="old")
    catalog = Catalog([original])
    first = asdict(make_part(item_id="new-1"))
    second = asdict(make_part(item_id="new-2"))
    if fault == "missing":
        del second["manufacturer"]
    elif fault == "extra":
        second["extra"] = "unsupported"
    elif fault == "blank":
        second["name"] = " "
    elif fault == "duplicate":
        second["item_id"] = first["item_id"]
    records = [first, None if fault == "not-object" else second]
    path = write_document(
        tmp_path, {"format_version": FORMAT_VERSION, "items": records}
    )
    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)
    assert list(catalog) == [original]


@pytest.mark.parametrize("content", [b'{"items":', b"\xff\xfe", b""])
def test_invalid_json_is_atomic(
    make_part: Callable[..., AviationPart], tmp_path: Path, content: bytes
) -> None:
    """Синтаксические ошибки и неверная кодировка не затрагивают каталог."""
    original = make_part()
    catalog = Catalog([original])
    path = tmp_path / "bad.json"
    path.write_bytes(content)
    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)
    assert list(catalog) == [original]


def test_file_errors(catalog: Catalog, tmp_path: Path) -> None:
    """Отсутствующий файл и запись в каталог оборачиваются в предметную ошибку."""
    with pytest.raises(CatalogFileError):
        load_catalog(catalog, tmp_path / "missing.json")
    with pytest.raises(CatalogFileError):
        save_catalog(catalog, tmp_path)
