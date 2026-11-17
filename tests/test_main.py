"""Проверка пользовательских сценариев CLI."""

from pathlib import Path

import pytest

from src.main import main


def add_arguments() -> list[str]:
    """Вернуть аргументы создания демонстрационной детали."""
    return [
        "add",
        "--id",
        "0017",
        "--name",
        "Лопатка турбины",
        "--category",
        "Двигатель",
        "--year",
        "2024",
        "--manufacturer",
        "Учебный завод",
        "--aircraft-model",
        "Модель А",
    ]


def test_cli_workflow(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Добавление, оба поиска, получение, список, количество и удаление работают."""
    prefix = ["--file", str(tmp_path / "parts.json")]
    main(prefix + add_arguments())
    assert "Добавлена деталь 0017" in capsys.readouterr().out
    for command in (
        ["list"],
        ["get", "0017"],
        ["find-name", "ТУРБИНЫ"],
        ["find-category", "Двигатель"],
    ):
        main(prefix + command)
        assert "Лопатка турбины" in capsys.readouterr().out
    main(prefix + ["count"])
    assert capsys.readouterr().out.strip() == "1"
    main(prefix + ["remove", "0017"])
    assert "Удалена деталь 0017" in capsys.readouterr().out
    main(prefix + ["list"])
    assert "Детали не найдены" in capsys.readouterr().out


def test_cli_error_preserves_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Повторный ID завершает CLI кодом 2 и сохраняет прежние байты файла."""
    path = tmp_path / "parts.json"
    prefix = ["--file", str(path)]
    main(prefix + add_arguments())
    before = path.read_bytes()
    with pytest.raises(SystemExit) as error:
        main(prefix + add_arguments())
    assert error.value.code == 2
    assert "уже существует" in capsys.readouterr().err
    assert path.read_bytes() == before


def test_cli_corruption_preserves_file(tmp_path: Path) -> None:
    """Повреждённый файл не перезаписывается при попытке добавить деталь."""
    path = tmp_path / "parts.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(SystemExit) as error:
        main(["--file", str(path)] + add_arguments())
    assert error.value.code == 2
    assert path.read_text(encoding="utf-8") == "{broken"


def test_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Справка завершается успешно и перечисляет команды."""
    with pytest.raises(SystemExit) as error:
        main(["--help"])
    assert error.value.code == 0
    assert "find-name" in capsys.readouterr().out
