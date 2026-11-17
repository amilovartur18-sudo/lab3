"""Каталог с доступом к деталям через словарный индекс."""

from collections.abc import Iterable, Iterator

from src.errors import DuplicateIdError, InvalidPartError, ItemNotFoundError
from src.part import AviationPart


class Catalog:
    """Хранить детали в порядке добавления; ID сравнивать с учётом регистра."""

    def __init__(self, items: Iterable[AviationPart] = ()) -> None:
        """Создать каталог из последовательности корректных уникальных деталей."""
        self._items: dict[str, AviationPart] = {}
        for item in items:
            self.add(item)

    def add(self, item: AviationPart) -> None:
        """Добавить деталь или вызвать ошибку типа/повторного ID."""
        if not isinstance(item, AviationPart):
            raise InvalidPartError("В каталог можно добавлять только AviationPart.")
        if item.item_id in self._items:
            raise DuplicateIdError(f"Деталь с ID {item.item_id!r} уже существует.")
        self._items[item.item_id] = item

    def get(self, item_id: str) -> AviationPart:
        """Получить деталь за O(1) в среднем; при отсутствии вызвать ошибку."""
        try:
            return self._items[item_id]
        except KeyError:
            raise ItemNotFoundError(f"Деталь с ID {item_id!r} не найдена.") from None

    def remove(self, item_id: str) -> None:
        """Удалить деталь по ID или вызвать ItemNotFoundError."""
        try:
            del self._items[item_id]
        except KeyError:
            raise ItemNotFoundError(f"Деталь с ID {item_id!r} не найдена.") from None

    def find_by_category(self, category: str) -> tuple[AviationPart, ...]:
        """Найти точную категорию с учётом регистра и без внешних пробелов."""
        category = category.strip()
        return tuple(item for item in self._items.values() if item.category == category)

    def find_by_name(self, query: str) -> tuple[AviationPart, ...]:
        """Найти подстроку в названии без учёта регистра; пустая строка находит всё."""
        query = query.strip().casefold()
        return tuple(
            item for item in self._items.values() if query in item.name.casefold()
        )

    def replace_all(self, items: Iterable[AviationPart]) -> None:
        """Заменить содержимое только после успешной проверки всех новых деталей."""
        replacement = Catalog(items)
        self._items = replacement._items

    def __len__(self) -> int:
        """Вернуть количество деталей за O(1)."""
        return len(self._items)

    def __iter__(self) -> Iterator[AviationPart]:
        """Перебирать детали в порядке добавления; после повторного добавления в конце."""
        return iter(self._items.values())

    def __contains__(self, item_id: object) -> bool:
        """Проверить наличие строкового ID за O(1) в среднем."""
        return isinstance(item_id, str) and item_id in self._items
