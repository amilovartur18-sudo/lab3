# Лабораторная работа № 3. Каталог авиационных деталей

**Тема:** каталог объектов. **Вариант:** авиационные детали.

Программа позволяет добавлять, получать, удалять и искать авиационные детали,
сохранять каталог в JSON и полностью восстанавливать его из файла. Реализована
обязательная часть задания. Дополнительные задания не включены.

Быстрый переход: [демонстрация ошибок на защите](#error-examples) ·
[примеры по всем критериям](#defense-examples).

<a id="error-examples"></a>

## Демонстрация ошибок на защите

Этот раздел содержит подготовку детали и каталога, а затем отдельные команды,
которые намеренно вызывают ошибки. Их сообщения — ожидаемый результат проверки.

### Шаг 1. Запустить Python из папки проекта

В обычном терминале, где приглашение заканчивается на `%` или `$`, выполните:

```bash
cd ~/Downloads/lab3
source .venv/bin/activate
python
```

Если проект находится в другой папке, замените путь в команде `cd`.
Если окружение ещё не установлено, сначала выполните раздел [Установка](#установка).

После запуска Python появится `>>>`. Теперь вводите **Python-код из следующих
блоков**, а не команды `cd` или `source`. Символы `>>>` копировать не нужно.
Если вы уже видите `>>>` и Python запущен из `lab3`, повторно запускать его не надо.

### Шаг 2. Подготовить деталь и каталог

Один раз за текущую сессию Python вставьте весь блок:

```python
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from src.part import AviationPart
from src.catalog import Catalog
from src.storage import load_catalog

part = AviationPart(
    item_id="ENG-001",
    name="Лопатка турбины",
    category="Двигатель",
    year=2024,
    manufacturer="Завод",
    aircraft_model="Самолёт А",
)

catalog = Catalog([part])

temporary = TemporaryDirectory()
folder = Path(temporary.name)
```

Мы создали корректную деталь, каталог с этой деталью и временную папку для
проверочных файлов. Исходные файлы проекта изменяться не будут.

### Шаг 3. Вызывать ошибки по одной

Каждый блок ниже вводите отдельно в том же интерактивном Python.
После сообщения об ошибке интерпретатор снова покажет `>>>`, и можно продолжать.
Если вы перезапустили Python, сначала снова выполните подготовку из шага 2.

**InvalidPartError — неправильные данные детали.**

```python
replace(part, name="")
```

`replace` пытается создать новую деталь, скопировав поля `part`, но заменив
название пустой строкой. Проверка в `__post_init__` её отклоняет.
Последняя строка сообщения:

```text
src.errors.InvalidPartError: Поле name должно быть непустой строкой.
```

Фраза для защиты: «Пустое название нарушает инвариант, поэтому объект не создаётся».

**DuplicateIdError — повторный ID.**

```python
catalog.add(part)
```

Деталь `ENG-001` уже добавлена при создании `Catalog([part])`.

```text
src.errors.DuplicateIdError: Деталь с ID 'ENG-001' уже существует.
```

Фраза для защиты: «Метод add обнаруживает существующий ключ и запрещает дубликат».

**ItemNotFoundError — отсутствующий ID.**

```python
catalog.get("UNKNOWN")
```

```text
src.errors.ItemNotFoundError: Деталь с ID 'UNKNOWN' не найдена.
```

Удаление отсутствующей детали вызывает ту же предметную ошибку:

```python
catalog.remove("UNKNOWN")
```

Фраза для защиты: «KeyError словаря перехватывается и заменяется ItemNotFoundError».

**CorruptedFileError — повреждённый JSON.**

```python
bad_file = folder / "broken.json"
bad_file.write_text("{broken", encoding="utf-8")
load_catalog(catalog, bad_file)
```

`write_text` может вывести число записанных символов. При последующей загрузке
получим ошибку, потому что содержимое файла не является корректным JSON:

```text
src.errors.CorruptedFileError: Файл не является корректным UTF-8 JSON.
```

После ошибки покажите, что исходная деталь сохранилась:

```python
print(len(catalog))                 # 1
print(catalog.get("ENG-001").name)   # Лопатка турбины
```

Фраза для защиты: «Файл прочитан, но его содержимое повреждено. Каталог не изменился».

**CatalogFileError — невозможно прочитать файл.**

```python
load_catalog(catalog, folder / "missing.json")
```

Такого файла нет. Последняя строка сообщения содержит `src.errors.CatalogFileError`
и текст «Не удалось прочитать каталог». Полный путь зависит от временной папки.

Фраза для защиты: «Ошибка доступа к файлу оборачивается в CatalogFileError».

**FrozenInstanceError — изменение замороженной детали.**

```python
part.year = 2020
```

```text
dataclasses.FrozenInstanceError: cannot assign to field 'year'
```

Проверка сохранности старого значения:

```python
print(part.year)  # 2024
```

Фраза для защиты: «frozen=True запрещает обычное изменение полей созданного объекта».
Это готовая ошибка `dataclasses`, она не наследуется от нашего `CatalogError`.

**CatalogError — общий родитель предметных ошибок.** Отдельного сценария,
который вызывает непосредственно этот класс, в программе нет. Его используют,
чтобы одним обработчиком поймать любую из наших предметных ошибок:

```python
from src.errors import CatalogError

try:
    catalog.get("UNKNOWN")
except CatalogError as error:
    print(type(error).__name__, error)

```

При ручном построчном вводе после последней строки нажмите Enter на пустой строке,
чтобы Python выполнил блок `try/except`.

### Шаг 4. Вернуться в обычный терминал

```python
temporary.cleanup()
exit()
```

После выхода вместо `>>>` снова появится `%` или `$`. Теперь можно запускать
команды `python -m pytest` и самостоятельные блоки `python - <<'PY' ... PY`
из следующего раздела.

<a id="defense-examples"></a>

## Примеры для защиты по каждому критерию

Ниже идут все девять критериев из ведомости. У каждого есть запускаемый пример,
ожидаемый результат и пояснение, что показать преподавателю.

Перед примерами перейдите в папку проекта и активируйте виртуальное окружение.
Для нашей копии проекта в `Downloads` выполните:

```bash
cd ~/Downloads/lab3
source .venv/bin/activate
```

`cd` открывает папку проекта, а `source` активирует установленное окружение Python.
Корень проекта — это папка с `README.md`, `src/` и `tests/`.
Если проект находится в другом месте, замените путь в команде `cd`.
Если папки `.venv` ещё нет, сначала выполните шаги из раздела [Установка](#установка).
Эти команды подготовки выполняются один раз в каждом новом окне терминала.
После этого запускайте приведённые ниже примеры в том же окне.

Блоки `python - <<'PY' ... PY` целиком вставляются в терминал macOS/Linux.
Каждый блок самостоятельный: переменные из предыдущего блока ему не нужны.
Демонстрации читают `examples/catalog.json`, а файлы для проверки загрузки
создают во временной папке. Исходный пример JSON не изменяется.

### 1. dataclass и инварианты сущности — 12 баллов

**Что доказываем:** деталь является `dataclass`, содержит все шесть полей,
отклоняет пустое название и неправильный год при создании. Поля готовой
детали нельзя обычным присваиванием изменить на некорректные.

```bash
python - <<'PY'
from dataclasses import FrozenInstanceError, asdict, is_dataclass, replace
from src.errors import InvalidPartError
from src.part import AviationPart

part = AviationPart(
    item_id="0017", name="Лопатка турбины", category="Двигатель",
    year=2024, manufacturer="Учебный завод", aircraft_model="Самолёт А",
)
print("dataclass:", is_dataclass(part))
print("Поля:", ", ".join(asdict(part)))
print("Строковый ID с ведущими нулями:", repr(part.item_id))
for changes in ({"name": " "}, {"year": 1800}, {"year": "2024"}):
    try:
        replace(part, **changes)
    except InvalidPartError as error:
        print(type(error).__name__)
try:
    part.item_id = "OTHER"
except FrozenInstanceError as error:
    print(type(error).__name__)
PY
```

Ожидаемый вывод:

```text
dataclass: True
Поля: item_id, name, category, year, manufacturer, aircraft_model
Строковый ID с ведущими нулями: '0017'
InvalidPartError
InvalidPartError
InvalidPartError
FrozenInstanceError
```

**Где в коде:** [AviationPart и __post_init__](src/part.py),
[границы года и перечень полей](src/constants.py).
`replace` создаёт новый экземпляр и повторно запускает проверки конструктора.

### 2. Добавление, получение, удаление — 16 баллов

**Что доказываем:** `add` добавляет объект, `get` возвращает именно его;
повторный ID запрещён, а после удаления ID больше не существует.
Получение и удаление отсутствующей детали вызывают предметную ошибку.

```bash
python - <<'PY'
from src.catalog import Catalog
from src.errors import DuplicateIdError, ItemNotFoundError
from src.storage import load_catalog

source = Catalog()
load_catalog(source, "examples/catalog.json")
part = source.get("ENG-001")
catalog = Catalog()
catalog.add(part)
print("После add:", len(catalog))
print("get вернул тот же объект:", catalog.get("ENG-001") is part)
try:
    catalog.add(part)
except DuplicateIdError as error:
    print(type(error).__name__)
catalog.remove("ENG-001")
print("После remove:", len(catalog))
for operation in (catalog.get, catalog.remove):
    try:
        operation("ENG-001")
    except ItemNotFoundError as error:
        print(type(error).__name__)
PY
```

Ожидаемый вывод:

```text
После add: 1
get вернул тот же объект: True
DuplicateIdError
После remove: 0
ItemNotFoundError
ItemNotFoundError
```

**Где в коде:** [Catalog.add, get и remove](src/catalog.py).

### 3. Поиск по категории и имени — 10 баллов

**Что доказываем:** категория ищется точно, название — по подстроке без учёта
регистра. Поиск без совпадений возвращает пустой результат. Результат поиска
не позволяет удалить элементы из внутренней коллекции каталога.

```bash
python - <<'PY'
from src.catalog import Catalog
from src.storage import load_catalog

catalog = Catalog()
load_catalog(catalog, "examples/catalog.json")
print("Категория:", [p.item_id for p in catalog.find_by_category("Двигатель")])
result = catalog.find_by_name("ТУРБИНЫ")
print("Название:", [p.item_id for p in result])
print("Нет совпадений:", catalog.find_by_name("несуществующее название"))
print("Результат — tuple:", isinstance(result, tuple))
separate_list = list(result)
separate_list.clear()
print("После очистки отдельного списка:", len(catalog))
print("Деталь осталась:", "ENG-001" in catalog)
PY
```

Ожидаемый вывод:

```text
Категория: ['ENG-001']
Название: ['ENG-001']
Нет совпадений: ()
Результат — tuple: True
После очистки отдельного списка: 2
Деталь осталась: True
```

**Где в коде:** [find_by_category и find_by_name](src/catalog.py).
За нечувствительность к регистру отвечает `casefold()`.

### 4. Протоколы len, iter, contains — 8 баллов

**Что доказываем:** каталог работает с `len`, `for`/`iter` и `in`.
Порядок — порядок добавления, а не сортировка ID. Два перебора совпадают;
удалённая и заново добавленная деталь переходит в конец.

```bash
python - <<'PY'
from src.catalog import Catalog
from src.storage import load_catalog

catalog = Catalog()
load_catalog(catalog, "examples/catalog.json")
print("len:", len(catalog))
print("Есть ID:", "ENG-001" in catalog)
print("Нет ID:", "UNKNOWN" in catalog)
first = [part.item_id for part in iter(catalog)]
second = [part.item_id for part in catalog]
print("Первый перебор:", first)
print("Второй перебор:", second)
print("Порядок совпадает:", first == second)
part = catalog.get("ENG-001")
catalog.remove("ENG-001")
catalog.add(part)
print("После повторного добавления:", [p.item_id for p in catalog])
PY
```

Ожидаемый вывод:

```text
len: 2
Есть ID: True
Нет ID: False
Первый перебор: ['ENG-001', 'GEAR-002']
Второй перебор: ['ENG-001', 'GEAR-002']
Порядок совпадает: True
После повторного добавления: ['GEAR-002', 'ENG-001']
```

**Где в коде:** [__len__, __iter__ и __contains__](src/catalog.py).

### 5. Словарный индекс и согласованность — 9 баллов

**Что доказываем:** детали действительно находятся в словаре по ID.
Удаление обновляет доступ по ID, длину и результаты поиска. В проекте один
словарь, поэтому отдельный список не может разойтись с индексом.

Здесь `_items` читается только для демонстрации внутреннего устройства на
защите. При обычной работе используется публичный API каталога.

```bash
python - <<'PY'
from src.catalog import Catalog
from src.errors import ItemNotFoundError
from src.storage import load_catalog

catalog = Catalog()
load_catalog(catalog, "examples/catalog.json")
print("Индекс — dict:", isinstance(catalog._items, dict))
print("Ключи индекса:", list(catalog._items))
print("get читает объект из словаря:", catalog.get("ENG-001") is catalog._items["ENG-001"])
catalog.remove("ENG-001")
print("ID присутствует:", "ENG-001" in catalog)
print("Размер:", len(catalog))
print("Поиск удалённой категории:", catalog.find_by_category("Двигатель"))
print("Поиск удалённого названия:", catalog.find_by_name("турбины"))
try:
    catalog.get("ENG-001")
except ItemNotFoundError as error:
    print(type(error).__name__)
PY
```

Ожидаемый вывод:

```text
Индекс — dict: True
Ключи индекса: ['ENG-001', 'GEAR-002']
get читает объект из словаря: True
ID присутствует: False
Размер: 1
Поиск удалённой категории: ()
Поиск удалённого названия: ()
ItemNotFoundError
```

**Что объяснить:** в [методе get](src/catalog.py) есть прямое обращение
`return self._items[item_id]`, а цикла по объектам нет. Отсюда O(1) в среднем
для поиска ID. Демонстрация поведения сама по себе не измеряет сложность:
сложность обосновывается устройством словаря и реализацией метода.

### 6. JSON save/load и версия формата — 15 баллов

**Что доказываем:** сохраняются версия, все поля и порядок деталей;
после загрузки каталог совпадает с исходным. Неизвестная версия отклоняется.

```bash
python - <<'PY'
import json
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from src.catalog import Catalog
from src.constants import FORMAT_VERSION
from src.errors import UnsupportedVersionError
from src.storage import load_catalog, save_catalog

catalog = Catalog()
load_catalog(catalog, "examples/catalog.json")
with TemporaryDirectory() as folder:
    path = Path(folder) / "round-trip.json"
    save_catalog(catalog, path)
    document = json.loads(path.read_text(encoding="utf-8"))
    print("format_version:", document["format_version"])
    print("Все поля записаны:", document["items"] == [asdict(p) for p in catalog])
    restored = Catalog()
    load_catalog(restored, path)
    print("Каталоги совпали:", list(restored) == list(catalog))
    print("Порядок:", [p.item_id for p in restored])
    document["format_version"] = FORMAT_VERSION + 1
    path.write_text(json.dumps(document), encoding="utf-8")
    try:
        load_catalog(restored, path)
    except UnsupportedVersionError as error:
        print(type(error).__name__)
    print("После ошибки версии каталог сохранён:", list(restored) == list(catalog))
PY
```

Ожидаемый вывод:

```text
format_version: 1
Все поля записаны: True
Каталоги совпали: True
Порядок: ['ENG-001', 'GEAR-002']
UnsupportedVersionError
После ошибки версии каталог сохранён: True
```

**Где в коде:** [save_catalog, parse_document и load_catalog](src/storage.py),
[FORMAT_VERSION](src/constants.py).

### 7. Иерархия исключений и атомарная загрузка — 10 баллов

**Что доказываем:** все предметные ошибки наследуются от `CatalogError`.
В документе первая новая деталь корректна, а **вторая повреждена**.
После неудачной загрузки старая деталь остаётся тем же объектом, первая новая
не добавляется. Отдельно демонстрируется ошибка синтаксиса JSON.

```bash
python - <<'PY'
import json
from dataclasses import asdict, replace
from pathlib import Path
from tempfile import TemporaryDirectory
from src.catalog import Catalog
from src.constants import FORMAT_VERSION
from src.errors import (
    CatalogError, CatalogFileError, CorruptedFileError, DuplicateIdError,
    InvalidPartError, ItemNotFoundError, UnsupportedVersionError,
)
from src.storage import load_catalog

errors = (
    InvalidPartError, DuplicateIdError, ItemNotFoundError,
    UnsupportedVersionError, CorruptedFileError, CatalogFileError,
)
print("Все ошибки — CatalogError:", all(issubclass(e, CatalogError) for e in errors))
source = Catalog()
load_catalog(source, "examples/catalog.json")
old = replace(source.get("ENG-001"), item_id="OLD")
catalog = Catalog([old])
before = list(catalog)
good = asdict(replace(old, item_id="NEW-1"))
bad = asdict(replace(old, item_id="NEW-2"))
bad["year"] = "не число"
with TemporaryDirectory() as folder:
    path = Path(folder) / "damaged.json"
    document = {"format_version": FORMAT_VERSION, "items": [good, bad]}
    path.write_text(json.dumps(document), encoding="utf-8")
    try:
        load_catalog(catalog, path)
    except CatalogError as error:
        print("Повреждена вторая запись:", type(error).__name__)
    print("Исходное состояние сохранено:", list(catalog) == before)
    print("Старый объект тот же:", catalog.get("OLD") is old)
    print("Первая новая деталь добавилась:", "NEW-1" in catalog)
    path.write_text("{broken", encoding="utf-8")
    try:
        load_catalog(catalog, path)
    except CatalogError as error:
        print("Неверный синтаксис JSON:", type(error).__name__)
    print("После синтаксической ошибки:", list(catalog) == before)
PY
```

Ожидаемый вывод:

```text
Все ошибки — CatalogError: True
Повреждена вторая запись: CorruptedFileError
Исходное состояние сохранено: True
Старый объект тот же: True
Первая новая деталь добавилась: False
Неверный синтаксис JSON: CorruptedFileError
После синтаксической ошибки: True
```

**Где в коде:** [иерархия ошибок](src/errors.py), [загрузчик](src/storage.py)
и [replace_all](src/catalog.py). Сначала проверяются новые данные и строится
временный каталог, затем одной операцией заменяется `self._items`.
Если раньше возникло исключение, до замены выполнение не доходит.

### 8. Тестирование — 15 баллов

**Что показываем:** тесты действительно выполняются и отдельно покрывают
каждую группу из критериев. Команды можно запускать независимо:

```bash
python -m pytest -v tests/test_part.py
python -m pytest -v tests/test_catalog.py
python -m pytest -v tests/test_storage.py
python -m pytest -v tests/test_main.py
```

- [test_part.py](tests/test_part.py): инварианты сущности, включая неверные
  типы, пустые строки и границы года — группа на 3 балла.
- [test_catalog.py](tests/test_catalog.py): операции и ошибки — группа на
  4 балла; поиск и протоколы — группа на 3 балла.
- [test_storage.py](tests/test_storage.py): JSON round trip и версии — группа
  на 3 балла; атомарность загрузки — группа на 2 балла.
- [test_main.py](tests/test_main.py): дополнительно проверяет сценарии CLI.

Чтобы быстро показать именно повреждение второй записи:

```bash
python -m pytest -v tests/test_storage.py -k test_bad_second_record_is_atomic
```

Ожидается **18 passed**: шесть полей по три неверных значения.
Полный запуск:

```bash
python -m pytest -q
```

Ожидается **101 passed**; длительность и оформление строки зависят от среды.
Это число пройденных тестов, а не процент покрытия кода и не оценка за работу.

#### Измерение покрытия кода

`pytest-cov` включён в зависимости разработки. Для измерения покрытия строк
и ветвей, а также создания отчёта выполните:

```bash
python -m pytest --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml -q
```

Измеренный результат на Python 3.14.8, 101 тест:

- **Строки: 99,44%** — выполнено 179 из 180 исполняемых строк.
- **Ветви: 95,83%** — проверено 46 из 48 переходов.
- **Общий показатель coverage.py: 98,68%** — 225 из 228 строк и переходов.
- Модель детали (`part.py`), каталог (`catalog.py`), хранение (`storage.py`),
  константы и исключения: **100% строк и ветвей**.
- Консольный интерфейс (`main.py`): **96,74% общего покрытия**.

В CLI не выполнена строка вызова `main()` при запуске файла как главного
модуля: тесты вызывают `main` напрямую. Также не проверен выход из диспетчера
для неизвестной команды: обычный CLI отклоняет такую команду раньше, в argparse.
Они остаются в расчёте покрытия и не исключаются настройками.

Подробный HTML-отчёт создаётся в `htmlcov/index.html`, машинный XML-отчёт —
в `coverage.xml`. Колонка `Missing` в терминале показывает непроверенные строки
и переходы. Эти генерируемые файлы исключены из Git. В `pyproject.toml`
включён `branch = true`, поэтому измеряются и ветви, а не только строки.
Высокий процент покрытия означает выполнение кода тестами, но сам по себе
не доказывает отсутствие ошибок.

### 9. README и защита — 5 баллов

**Что показываем:** по README можно установить и запустить проект, найти
контракт методов и воспроизвести каждый критерий. Для демонстрации готового
приложения выполните:

```bash
python -m src.main --file examples/catalog.json list
```

Ожидаемый вывод:

```text
ENG-001 | Лопатка турбины | Двигатель | 2024 | Учебный завод | Учебный самолёт А
GEAR-002 | Стойка шасси | Шасси | 2023 | Учебный завод | Учебный самолёт Б
```

Подготовьте объяснения для трёх заданий на защите:

1. **Добавить проверяемое поле.** Порядок изменений описан в
   [DEFENSE.md](DEFENSE.md#как-добавить-новое-проверяемое-поле): модель,
   константы, CLI, JSON, примеры и тесты.
2. **Объяснить сложность.** `get` использует ключ словаря — O(1) в среднем;
   `find_by_name` просматривает все детали — O(n) при ограниченной длине строк.
3. **Добавить тест частично повреждённого документа.** Пункт 7 демонстрирует
   сценарий, а `test_bad_second_record_is_atomic` показывает его автоматическую
   проверку. Можно расширить её новым ошибочным значением или ограничением поля.

Пункты «Вычет за долг» и «Итого» в ведомости заполняет преподаватель;
они не являются отдельными функциями программы.

## Структура проекта

```text
lab3/
├── src/
│   ├── __init__.py
│   ├── main.py          # Точка входа и консольные команды
│   ├── part.py          # Неизменяемый dataclass AviationPart
│   ├── catalog.py       # Каталог и словарный индекс по ID
│   ├── storage.py       # JSON save/load и проверка структуры документа
│   ├── errors.py        # Предметные исключения
│   └── constants.py     # Версия формата, границы года и другие константы
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Общие фикстуры
│   ├── test_part.py     # Инварианты и неизменяемость детали
│   ├── test_catalog.py  # Операции, поиск и протоколы коллекции
│   ├── test_storage.py  # JSON, версии и атомарность загрузки
│   └── test_main.py     # Пользовательские сценарии CLI
├── examples/catalog.json
├── pyproject.toml
├── uv.lock
├── requirements.txt
├── .pre-commit-config.yaml
├── .gitignore
├── report.pdf
├── DEFENSE.md
└── README.md
```

## Установка

Нужен Python 3.12 или новее. Выполняйте команды из папки `lab3`.

Установка через uv:

```bash
uv sync --locked
source .venv/bin/activate
```

У приложения нет внешних зависимостей во время выполнения. Инструменты
разработки находятся в группе `dev`; версии зафиксированы в `uv.lock`.

## Запуск

```bash
python -m src.main --help
python -m src.main add --help
```

Добавление детали:

```bash
python -m src.main add \
  --id ENG-001 \
  --name "Лопатка турбины" \
  --category "Двигатель" \
  --year 2024 \
  --manufacturer "Учебный завод" \
  --aircraft-model "Учебный самолёт А"
```

Просмотр и поиск:

```bash
python -m src.main list
python -m src.main get ENG-001
python -m src.main find-category "Двигатель"
python -m src.main find-name "ТУРБИНЫ"
python -m src.main count
python -m src.main remove ENG-001
```

По умолчанию используется `catalog.json` в текущей рабочей папке.
Ключ `--file` задаётся перед командой:

```bash
python -m src.main --file examples/catalog.json list
```

Если файл отсутствует, CLI начинает с пустого каталога. После успешного
добавления или удаления файл сохраняется. Команды чтения файл не изменяют.
При предметной ошибке выводится сообщение в stderr и возвращается код 2.
Демонстрационные детали в `examples` вымышлены.

## Предметная модель и инварианты

`AviationPart` - `@dataclass(frozen=True)` со следующими полями:

- `item_id: str` - непустой строковый ID; допускаются буквы, цифры и дефисы.
  Ведущие нули сохраняются. Уникальность проверяет каталог.
- `name: str` - название детали.
- `category: str` - категория.
- `year: int` - год выпуска в принятом учебном диапазоне 1903..9999.
  Значения `bool`, строки и дробные числа не принимаются.
- `manufacturer: str` - производитель, первое поле варианта.
- `aircraft_model: str` - совместимая модель самолёта, второе поле варианта.

Все текстовые поля обязаны быть непустыми строками. Внешние пробелы
удаляются при создании. Проверки выполняются в `__post_init__`.
Неизменяемость препятствует смене ID после добавления в каталог и нарушению
инвариантов через результат `get` или поиска.

## Контракт каталога

Каталог содержит один приватный словарь `_items: dict[str, AviationPart]`.
Отдельный список и дополнительный индекс по категории не поддерживаются.

- `add(item) -> None`: проверяет тип, запрещает повторный ID.
- `get(item_id) -> AviationPart`: возвращает объект по ключу словаря.
- `remove(item_id) -> None`: удаляет запись по ключу.
- `find_by_category(category) -> tuple[AviationPart, ...]`: точное совпадение
  категории с учётом регистра; внешние пробелы запроса удаляются.
- `find_by_name(query) -> tuple[AviationPart, ...]`: поиск подстроки после
  `casefold()`, без учёта регистра; пустой запрос возвращает все детали.
- `len(catalog)`, `iter(catalog)`, `item_id in catalog`: стандартные протоколы.
- `replace_all(items) -> None`: сначала проверяет новую коллекцию целиком,
  затем заменяет словарь. Используется загрузчиком JSON.

**Порядок:** добавление, поиск и итерация сохраняют порядок вставки в словарь.
Два последовательных перебора неизменённого каталога дают один результат.
Удаление и повторное добавление помещают деталь в конец. Во время перебора
не следует менять состав каталога.

Поиск возвращает отдельный неизменяемый кортеж с неизменяемыми деталями.
Полученный результат не даёт изменить внутреннюю коллекцию.

**Сложность:** `add`, `get`, `remove`, `contains` - O(1) в среднем;
`len` - O(1); полный перебор - O(n). Поиск категории - O(n) при ограниченной
длине строк. Поиск названия линейно просматривает n деталей; точная стоимость
также зависит от длин названий и подстроки. Хранение каталога - O(n).

## JSON и атомарность загрузки

```json
{
  "format_version": 1,
  "items": [
    {
      "item_id": "ENG-001",
      "name": "Лопатка турбины",
      "category": "Двигатель",
      "year": 2024,
      "manufacturer": "Учебный завод",
      "aircraft_model": "Учебный самолёт А"
    }
  ]
}
```

`save_catalog(catalog, path)` сохраняет все поля в UTF-8. `load_catalog(catalog,
path)` **заменяет** содержимое существующего каталога, а не дополняет его.

Загрузка проходит в три этапа: прочитать JSON; проверить корневую структуру,
версию и все детали; построить временный каталог и заменить исходный словарь.
До последнего этапа исходный каталог не изменяется. Ошибка даже в последней
записи, неверный тип или дубликат ID сохраняют прежние детали и их порядок.
Загрузка пустого `items` успешно очищает каталог.

Набор полей документа и каждой записи проверяется точно. Версия обязана быть
целым числом; `true` и `"1"` не заменяют число `1`. Миграции не реализованы.
Атомарность относится к загрузке в память; файловая запись выполняется обычным
способом и не гарантирует сохранность старого файла при сбое диска или питания.

## Исключения

Все ошибки наследуются от `CatalogError`:

- `InvalidPartError` - неверная сущность.
- `DuplicateIdError` - повторный ID при добавлении.
- `ItemNotFoundError` - отсутствующий ID при получении или удалении.
- `UnsupportedVersionError` - неизвестная целочисленная версия формата.
- `CorruptedFileError` - синтаксис, кодировка, структура или данные JSON неверны;
  сюда же относится дубликат ID в загружаемом документе.
- `CatalogFileError` - ошибка файловой системы при чтении или записи.

## Проверки

```bash
python -m pytest -q
python -m pytest --cov=src --cov-report=term-missing --cov-report=html -q
ruff check .
mypy src tests
pre-commit validate-config
```

Тесты покрывают допустимые и ошибочные поля, оба края диапазона года,
неизменяемость, основные операции, дубликаты и отсутствующие ID, Unicode-поиск,
порядок вставки, независимость результатов поиска, JSON round trip, пустой
каталог, версии, повреждённую вторую запись и отсутствие частичного изменения.
Отдельно проверяются пользовательские команды и сохранность файла при ошибке.

После создания Git-репозитория можно установить проверки перед коммитом:

```bash
pre-commit install
pre-commit run --all-files
```

Первый запуск pre-commit требует доступа к сети для загрузки окружений хуков.
Подготовка к вопросам преподавателя находится в `DEFENSE.md`.

## Использованные ориентиры

- [Шаблон оформления](https://github.com/Untronix0nly/python-labs-skeleton).
- [Пример одногруппника](https://github.com/timofeykazakov2008-blip/lab3):
  разделение модели, каталога, хранения, CLI и тестов; неизменяемая сущность
  и загрузка через временный каталог.
- Задание «Лабораторная работа 3. Каталог объектов» и критерии «Оценивание ЛР3».
