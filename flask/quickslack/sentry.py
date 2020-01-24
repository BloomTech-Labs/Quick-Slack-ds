import sentry_sdk
from decouple import config


def integrate_sentry(func):
    sentry_sdk.init(
        dsn=config('SENTRY_DSN'),
        integrations=[func()]
    )
