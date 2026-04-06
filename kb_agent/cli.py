"""CLI entry point for the knowledge base agent."""

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from . import core

console = Console()


@click.group()
def cli():
    """LLM-powered personal knowledge base agent."""
    pass


@cli.command()
@click.argument("path")
def ingest(path):
    """Ingest a file or URL into raw/."""
    dest = core.ingest(path)
    console.print(f"[green]Ingested:[/green] {dest}")


@cli.command()
@click.option("--force", is_flag=True, help="Recompile existing articles")
def compile(force):
    """Compile raw documents into wiki articles."""
    console.print("[bold]Compiling raw docs → wiki articles...[/bold]")
    created = core.compile_all(force=force)
    if created:
        for slug in created:
            console.print(f"  [green]+ {slug}.md[/green]")
        console.print(f"\n[bold]{len(created)}[/bold] articles created. Index rebuilt.")
    else:
        console.print("[dim]Nothing new to compile.[/dim]")


@cli.command()
@click.argument("question")
@click.option("--save", is_flag=True, help="Integrate answer into the wiki")
def query(question, save):
    """Ask a question against the wiki."""
    console.print(f"[bold]Researching:[/bold] {question}\n")
    result = core.query(question, save=save)
    console.print(Markdown(result["answer"]))
    if result["save_info"]:
        info = result["save_info"]
        if info["action"] == "update":
            console.print(f"\n[green]Updated existing article:[/green] {info['slug']}.md")
        else:
            console.print(f"\n[green]Created new article:[/green] {info['slug']}.md")


@cli.command()
def lint():
    """Run health checks on the wiki."""
    console.print("[bold]Running wiki health checks...[/bold]\n")
    findings = core.lint_wiki()

    if findings["structural"]:
        console.print(Panel("\n".join(findings["structural"]), title="Structural Issues", border_style="yellow"))
    else:
        console.print("[green]No structural issues found.[/green]\n")

    if findings["llm"]:
        console.print(Panel(Markdown(findings["llm"]), title="LLM Analysis", border_style="blue"))


@cli.command()
def fix():
    """Auto-fix wiki issues found by lint."""
    console.print("[bold]Running lint + auto-fix...[/bold]\n")
    fixed = core.fix_wiki()
    if fixed:
        for slug, issues in fixed.items():
            console.print(f"  [green]Fixed {slug}.md[/green]")
            for issue in issues:
                console.print(f"    - {issue}")
        console.print(f"\n[bold]{len(fixed)}[/bold] articles fixed. Index rebuilt.")
    else:
        console.print("[dim]No issues to fix.[/dim]")


@cli.command()
def index():
    """Rebuild the wiki INDEX.md."""
    console.print("[bold]Rebuilding index...[/bold]")
    core.rebuild_index()
    console.print("[green]INDEX.md updated.[/green]")


@cli.command()
@click.argument("query")
def search(query):
    """Search wiki articles by keyword."""
    results = core.search_wiki(query)
    if not results:
        console.print("[dim]No results found.[/dim]")
        return
    for slug, score in results:
        console.print(f"  [cyan]{slug}.md[/cyan]  (score: {score})")
