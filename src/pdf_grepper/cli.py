from __future__ import annotations

import json
import os
from typing import Optional

import typer
from rich import print

from pdf_grepper.pipeline import run_pipeline

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback()
def _main() -> None:
	"""pdf-grepper CLI."""
	return None


@app.command("parse")
def parse_command(
	inputs: list[str] = typer.Argument(..., help="Input files: PDF(s) and/or DOCX OCR variants."),
	out: str = typer.Option("model.ttl", "--out", "-o", help="Output Turtle path."),
	json_out: Optional[str] = typer.Option(None, "--json", help="Optional JSON mirror path."),
	ocr: str = typer.Option("auto", "--ocr", help="OCR mode: none|local|auto"),
	cloud: str = typer.Option("", "--cloud", help="Comma-list: openai,google,aws,azure"),
	enrich_web: bool = typer.Option(False, "--enrich-web", help="Enable web enrichment for domain inference."),
	offline: bool = typer.Option(False, "--offline", help="Disable all network calls."),
	base_uri: str = typer.Option("http://example.org/pdf-grepper/", "--base-uri", help="Base URI for RDF resources."),
) -> None:
	cloud_list = [c.strip() for c in cloud.split(",") if c.strip()]
	print(f"[bold]pdf-grepper[/bold] inputs={inputs} out={out}")
	model = run_pipeline(
		input_paths=inputs,
		ttl_out=out,
		json_out=json_out,
		ocr_mode=ocr,
		use_cloud=cloud_list,
		enrich_web=enrich_web,
		offline=offline,
		base_uri=base_uri,
	)
	print(f"[green]Wrote Turtle to {out}[/green]")
	if json_out:
		print(f"[green]Wrote JSON to {json_out}[/green]")


if __name__ == "__main__":
	app()


