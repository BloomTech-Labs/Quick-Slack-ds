import click

from quickslack.app import create_app
from quickslack.extensions import db

app = create_app()
db.app = app

@click.group()
def cli():
    """ Run Database related tasks. """
    pass

@click.command()
def init():

    db.drop_all()
    db.create_all()

    print('db init success...')

    return None

@click.command()
@click.pass_context
def reset(ctx):

    ctx.invoke(init)

    return None

cli.add_command(init)
cli.add_command(reset)
