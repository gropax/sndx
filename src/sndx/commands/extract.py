import typer
import sndx
import asyncio


def register(app: typer.Typer):
    @app.command("extract")
    def extract_cmd(
        email: str = typer.Option(..., "--email", "-e", help="Email address"),
        pwd: str = typer.Option(..., "--password", "-p", help="Password"),
        instances: int = typer.Option(..., "--browsers", "-b", help="Number of browser instances")
    ):
        print("TODO: extract command")
        print(f"email: {email}")
        print(f"pwd: {pwd}")
        print(f"instances: {instances}")

        asyncio.run(extract_cmd_async(email, pwd, instances))


    async def extract_cmd_async(email, pwd, instances):
        sinks = []
        for i in range(instances):
            sinks.append(sndx.Sink().__enter__())

        scrappers = []
        for i in range(instances):
            profile = f"sndx-profile-{i}"
            scrapper = sndx.RecordingScrapper(profile, sinks[i], email, pwd, headless=True)    
            scrappers.append(scrapper)
            await scrapper.__aenter__()

        print("Sleeping for 10s.")
        await asyncio.sleep(10)

        for scrapper in scrappers:
            await scrapper.__aexit__(None, None, None)

        for sink in sinks:
            await sink.__exit__(None, None, None)



    async def start_scrapper(i):
        profile = f"sndx-profile-{i}"
        sink = sndx.Sink().__enter__()
        scrapper = sndx.RecordingScrapper(profile, sink, headless=True)    
        await scrapper.__aenter__()

