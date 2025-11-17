import typer

def register(app: typer.Typer):
    @app.command("scaffold")
    def scaffold_cmd():
        print("TODO: scaffold command")

