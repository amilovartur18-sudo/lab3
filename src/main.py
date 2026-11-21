"""Консольный интерфейс: python -m src.main --help."""

import argparse
from collections.abc import Iterable, Sequence
from pathlib import Path

from src.catalog import Catalog
from src.constants import ADD_COMMAND_EXAMPLE, DEFAULT_CATALOG_FILE
from src.errors import CatalogError
from src.part import AviationPart
from src.storage import load_catalog, save_catalog


def create_parser() -> argparse.ArgumentParser:
    """Описать команды и аргументы консольного приложения."""
    parser = argparse.ArgumentParser(
        description="Каталог авиационных деталей",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            f"{ADD_COMMAND_EXAMPLE}\n\n"
            "Просмотр созданного каталога:\n"
            "  python -m src.main --file demo_catalog.json list"
        ),
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=Path(DEFAULT_CATALOG_FILE),
        help="Путь к JSON-каталогу (по умолчанию: %(default)s)",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="Показать все детали")
    commands.add_parser("count", help="Показать количество деталей")

    add_parser = commands.add_parser(
        "add",
        help="Добавить деталь",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=ADD_COMMAND_EXAMPLE,
    )
    add_parser.add_argument(
        "--id", dest="item_id", required=True, help="Уникальный строковый ID детали"
    )
    add_parser.add_argument("--name", required=True, help="Название детали")
    add_parser.add_argument("--category", required=True, help="Категория детали")
    add_parser.add_argument("--year", type=int, required=True, help="Год выпуска")
    add_parser.add_argument(
        "--manufacturer", required=True, help="Производитель детали"
    )
    add_parser.add_argument(
        "--aircraft-model", required=True, help="Совместимая модель самолёта"
    )

    for command, help_text in (
        ("get", "Получить деталь"),
        ("remove", "Удалить деталь"),
    ):
        subparser = commands.add_parser(command, help=help_text)
        subparser.add_argument("item_id", help="Идентификатор детали")

    category_parser = commands.add_parser("find-category", help="Поиск по категории")
    category_parser.add_argument("category")
    name_parser = commands.add_parser("find-name", help="Поиск по части названия")
    name_parser.add_argument("query")
    return parser


def print_parts(items: Iterable[AviationPart]) -> None:
    """Вывести все поля найденных деталей или сообщение об отсутствии результата."""
    found = False
    for item in items:
        found = True
        print(
            f"{item.item_id} | {item.name} | {item.category} | {item.year} | "
            f"{item.manufacturer} | {item.aircraft_model}"
        )
    if not found:
        print("Детали не найдены.")


def execute_command(args: argparse.Namespace, catalog: Catalog) -> None:
    """Выполнить команду; записывать каталог только после добавления или удаления."""
    if args.command == "add":
        item = AviationPart(
            item_id=args.item_id,
            name=args.name,
            category=args.category,
            year=args.year,
            manufacturer=args.manufacturer,
            aircraft_model=args.aircraft_model,
        )
        catalog.add(item)
        save_catalog(catalog, args.file)
        print(f"Добавлена деталь {item.item_id}.")
    elif args.command == "remove":
        catalog.remove(args.item_id)
        save_catalog(catalog, args.file)
        print(f"Удалена деталь {args.item_id}.")
    elif args.command == "get":
        print_parts((catalog.get(args.item_id),))
    elif args.command == "find-category":
        print_parts(catalog.find_by_category(args.category))
    elif args.command == "find-name":
        print_parts(catalog.find_by_name(args.query))
    elif args.command == "count":
        print(len(catalog))
    elif args.command == "list":
        print_parts(catalog)


def main(argv: Sequence[str] | None = None) -> None:
    """Загрузить каталог и обработать команду; предметные ошибки завершать кодом 2."""
    parser = create_parser()
    args = parser.parse_args(argv)
    catalog = Catalog()
    try:
        if args.file.exists():
            load_catalog(catalog, args.file)
        execute_command(args, catalog)
    except CatalogError as error:
        parser.exit(2, f"Ошибка: {error}\n")


if __name__ == "__main__":
    main()
