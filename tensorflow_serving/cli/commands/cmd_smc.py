import click, subprocess

@click.group()
def cli():
    """ Run saved_model_cli Commands """
    pass

@click.command()
def show_models():
    
    cmd = 'saved_model_cli show --dir models/resnet18/1'

    return subprocess.call(cmd, shell=True)

@click.command()
def tag_set():
    
    cmd = 'saved_model_cli show --dir models/resnet18/1/ --tag_set serve'

    return subprocess.call(cmd, shell=True)

@click.command()
def signature_def():
    
    cmd = 'saved_model_cli show --dir models/resnet18/1/ --tag_set serve --signature_def predict_images'

    return subprocess.call(cmd, shell=True)

@click.command()
@click.pass_context
def chain(ctx):

    ctx.invoke(show_models)
    ctx.invoke(tag_set)
    ctx.invoke(signature_def)

    return None

cli.add_command(show_models)
cli.add_command(tag_set)
cli.add_command(signature_def)
cli.add_command(chain)
