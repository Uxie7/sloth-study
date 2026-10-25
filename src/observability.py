from contextlib import contextmanager
import os
from src.config import settings


def init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN", settings.sentry_dsn)
    if dsn:
        import sentry_sdk
        sentry_sdk.init(dsn=dsn)


@contextmanager
def span(name: str):
    dsn = os.getenv("SENTRY_DSN", settings.sentry_dsn)
    if not dsn:
        yield
        return
    import sentry_sdk
    with sentry_sdk.start_span(op="pipeline", name=name):
        yield
