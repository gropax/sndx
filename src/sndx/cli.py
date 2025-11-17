import typer
from sndx.commands.scaffold import register as register_scaffold
from sndx.commands.extract import register as register_extract

app = typer.Typer(help="SndX audio extraction tools.")

register_scaffold(app)
register_extract(app)

def main():
    app()
