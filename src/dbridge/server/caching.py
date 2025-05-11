from datetime import datetime
from typing import Callable

from dbridge.config import EXPIRATION_SECONDS


def hash_arg(args: list[str | None]) -> str:
    return hashlib.sha256(
        "".join([a for a in args if a is not None]).encode()
    ).hexdigest()


def is_expired(dt: datetime):
    now = datetime.now()
    if (now - dt).total_seconds() > EXPIRATION_SECONDS:
        return True
    return False


def cache_value(v: Callable, args: list[str | None]):
    now = datetime.now()
    key = hash_arg(args)
    if not (value := cache.get(key)) or is_expired(value[1]):
        value = (v(), now)
        cache[key] = value
    return value[0]
