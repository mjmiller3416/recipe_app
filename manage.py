#!/usr/bin/env python3
"""
Management script for MealGenie.
"""
import subprocess
import sys
from pathlib import Path

try:
    import typer
except ImportError:
    print("Error: typer is not installed. Please run: pip install typer", file=sys.stderr)
    sys.exit(1)

app = typer.Typer(help="Management script for MealGenie.")
db_app = typer.Typer(help="Database management commands.")
app.add_typer(db_app, name="db")

@db_app.command("migrate")
def migrate():
    """
    Apply database migrations using Alembic.
    """
    here = Path(__file__).parent.resolve()
    alembic_ini = here / "alembic.ini"
    if not alembic_ini.exists():
        typer.echo(f"Could not find alembic.ini at {alembic_ini}", err=True)
        raise typer.Exit(code=1)
    cmd = ["alembic", "upgrade", "head", "--config", str(alembic_ini)]
    typer.echo(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error running alembic: {e}", err=True)
        raise typer.Exit(code=e.returncode)

if __name__ == "__main__":
    app()