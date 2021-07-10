import datetime

DEFAULT_FILE_PATH = "db.yml"


def now() -> datetime.datetime:
    return datetime.datetime.now().replace(microsecond=0)
