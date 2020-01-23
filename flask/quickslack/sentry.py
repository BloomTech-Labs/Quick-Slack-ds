import sentry_sdk
from decouple import config

def integrate_sentry(func):
	sentry_sdk.init(
		dsn="https://8da7ef327cab437dbeef65a125a66286@sentry.io/1886929", #config('SENTRY_DNS'),
		integrations=[func()]
	)