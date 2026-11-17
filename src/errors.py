"""Предметные исключения каталога."""


class CatalogError(Exception):
    """Базовая ошибка приложения."""


class InvalidPartError(CatalogError):
    """Поля авиационной детали нарушают инварианты."""


class DuplicateIdError(CatalogError):
    """Деталь с таким идентификатором уже существует."""


class ItemNotFoundError(CatalogError):
    """Деталь с указанным идентификатором отсутствует."""


class UnsupportedVersionError(CatalogError):
    """Версия JSON-документа не поддерживается."""


class CorruptedFileError(CatalogError):
    """Содержимое файла не соответствует формату каталога."""


class CatalogFileError(CatalogError):
    """Операционная система не позволила прочитать или записать файл."""
