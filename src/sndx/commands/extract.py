import typer

def register(app: typer.Typer):
    @app.command("extract")
    def extract_cmd():
        print("TODO: extract command")

