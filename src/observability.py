from contextlib import contextmanager
from src.config import settings


def init_sentry() -> None:
    if settings.sentry_dsn:
        import sentry_sdk
        sentry_sdk.init(dsn=settings.sentry_dsn)


@contextmanager
def span(name: str):
    if not settings.sentry_dsn:
        yield
        return
    import sentry_sdk
    with sentry_sdk.start_span(op="pipeline", name=name):
        yield
