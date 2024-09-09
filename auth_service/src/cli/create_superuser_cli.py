import asyncio
import sys

import typer

sys.path.append("..")

from utils.superuser import create_superuser

app = typer.Typer()


@app.command()
def superuser(login: str, password: str, first_name: str, last_name: str):
    asyncio.run(create_superuser(login, password, first_name, last_name))
    typer.echo("Superuser created successfully.")


if __name__ == "__main__":
    app()
