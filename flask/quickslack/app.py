from flask import Flask, jsonify, render_template
from celery import Celery
from decouple import config

from slack_user_client import SlackClient

from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from quickslack.routes.dashboard.views import dashboard
from quickslack.routes.api.slackevents import slackevents
from quickslack.sentry import integrate_sentry
from quickslack.extensions import (
	debug_toolbar,
	db
)

import logging, logging.config
logging.config.fileConfig('config/logging.conf')

CELERY_TASK_LIST = [
    'quickslack.tasks.example',
]

def create_celery_app(app=None):
    app = app or create_app()

    celery = Celery(
		app.import_name,
		broker=app.config['CELERY_BROKER_URL'],
		include=CELERY_TASK_LIST
	)

    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app(settings_override=None):
	integrate_sentry(FlaskIntegration)
	# sentry()

	app = Flask(__name__, instance_relative_config=True)
	app.config.from_object('config.flask')

	extensions(app)
	app.register_blueprint(dashboard)
	app.register_blueprint(slackevents)

	app.logger.info('Initializing Slack Client...')
	app.config['slack'] = SlackClient(
		config('SLACK_EMAIL'),
		config('SLACK_PASSWORD'),
		config('SLACK_WORKSPACE_URL')
	)
	app.logger.info('Logging into Slack...')
	app.config['slack'].login()

	@app.route('/')
	def index():
		render_kwargs = {'include_logs': True}
		try:
			with open('logs/flaskapp.log', 'r') as f:
				render_kwargs['log_file'] = f.readlines()
		except Exception as e:
			app.logger.info(str(e))
		app.logger.info('render_kwargs')

		return render_template('layouts/dashboard.html', **render_kwargs)

	@app.route('/debug_sentry')
	def trigger_error():
		division_by_zero = 1 / 0

	return app

# def sentry():
# 	integrate_sentry(CeleryIntegration)
# 	integrate_sentry(RedisIntegration)
# 	integrate_sentry(SqlalchemyIntegration)


def extensions(app):
	app.logger = logging.getLogger('root')

	debug_toolbar.init_app(app)
	db.init_app(app)

	app.logger.info('Extensions started...')
	return None
