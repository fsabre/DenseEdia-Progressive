import datetime

DEFAULT_FILE_NAME = "db.db"


def now() -> datetime.datetime:
    return datetime.datetime.now().replace(microsecond=0)
