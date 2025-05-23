import os
from datetime import datetime, timedelta
from babel.dates import format_timedelta, format_date
from portprotonqt.config_utils import read_time_config
from portprotonqt.localization import _, get_system_locale
from portprotonqt.logger import get_logger

logger = get_logger(__name__)

def get_cache_file_path():
    """Возвращает путь к файлу кеша portproton_last_launch."""
    cache_home = os.getenv("XDG_CACHE_HOME", os.path.join(os.path.expanduser("~"), ".cache"))
    return os.path.join(cache_home, "PortProtonQT", "last_launch")

def save_last_launch(exe_name, launch_time):
    """
    Сохраняет время запуска для exe.
    Формат файла: <exe_name> <isoformatted_time>
    """
    file_path = get_cache_file_path()
    data = {}
    if os.path.exists(file_path):
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    data[parts[0]] = parts[1]
    data[exe_name] = launch_time.isoformat()
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        for key, iso_time in data.items():
            f.write(f"{key} {iso_time}\n")

def format_last_launch(launch_time):
    """
    Форматирует время запуска с использованием Babel.

    Для detail_level "detailed" возвращает относительный формат с добавлением "назад"
    (например, "2 мин. назад"). Если время меньше минуты – возвращает переведённую строку.
    Для "brief" – дату в формате "день месяц год" (например, "1 апреля 2023")
    на основе системной локали.
    """
    detail_level = read_time_config() or "detailed"
    system_locale = get_system_locale()
    if detail_level == "detailed":
        # Вычисляем delta как launch_time - datetime.now() чтобы получить отрицательное значение для прошедшего времени.
        delta = launch_time - datetime.now()
        if abs(delta.total_seconds()) < 60:
            return _("just now")
        return format_timedelta(delta, locale=system_locale, granularity='second', format='short', add_direction=True)
    else:
        return format_date(launch_time, format="d MMMM yyyy", locale=system_locale)

def get_last_launch(exe_name):
    """
    Читает время последнего запуска для заданного exe из файла кеша.
    Возвращает время запуска в нужном формате или перевод строки "Never".
    """
    file_path = get_cache_file_path()
    if not os.path.exists(file_path):
        return _("Never")
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2 and parts[0] == exe_name:
                iso_time = parts[1]
                launch_time = datetime.fromisoformat(iso_time)
                return format_last_launch(launch_time)
    return _("Never")

def parse_playtime_file(file_path):
    """
    Парсит файл с данными о времени игры.

    Формат строки в файле:
      <полный путь к exe> <хэш> <playtime_seconds> <platform> <build>

    Возвращает словарь вида:
      {
         '<exe_path>': playtime_seconds (int),
         ...
      }
    """
    playtime_data = {}
    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}")
        return playtime_data

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            exe_path = parts[0]
            seconds = int(parts[2])
            playtime_data[exe_path] = seconds
    return playtime_data

def format_playtime(seconds):
    """
    Конвертирует время в секундах в форматированную строку с использованием Babel.

    При "detailed" выводится полный разбор времени, без округления
    (например, "1 ч 1 мин 15 сек").

    При "brief":
      - если время менее часа, выводится точное время с секундами (например, "9 мин 28 сек"),
      - если больше часа – только часы (например, "3 ч").
    """
    detail_level = read_time_config() or "detailed"
    system_locale = get_system_locale()
    seconds = int(seconds)

    if detail_level == "detailed":
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, secs = divmod(rem, 60)
        parts = []
        if days > 0:
            parts.append(f"{days} " + _("d."))
        if hours > 0:
            parts.append(f"{hours} " + _("h."))
        if minutes > 0:
            parts.append(f"{minutes} " + _("min."))
        if secs > 0 or not parts:
            parts.append(f"{secs} " + _("sec."))
        return " ".join(parts)
    else:
        # Режим brief
        if seconds < 3600:
            minutes, secs = divmod(seconds, 60)
            parts = []
            if minutes > 0:
                parts.append(f"{minutes} " + _("min."))
            if secs > 0 or not parts:
                parts.append(f"{secs} " + _("sec."))
            return " ".join(parts)
        else:
            hours = seconds // 3600
            return format_timedelta(timedelta(hours=hours), locale=system_locale, granularity='hour', format='short')

def get_last_launch_timestamp(exe_name):
    """
    Возвращает метку времени последнего запуска (timestamp) для заданного exe.
    Если записи нет, возвращает 0.
    """
    file_path = get_cache_file_path()
    if not os.path.exists(file_path):
        return 0
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2 and parts[0] == exe_name:
                iso_time = parts[1]
                dt = datetime.fromisoformat(iso_time)
                return dt.timestamp()
    return 0
