from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer
from rich import print

from pdf_grepper.da import run_da
from pdf_grepper.meaning import run_meaning
from pdf_grepper.pipeline import run_pipeline
from pdf_grepper.validate import load_graph, validate_with_pyshacl

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


@app.command("da")
def da_command(
	input_path: str = typer.Argument(..., help="Input: a parsed pg Turtle (.ttl) (preferred) or a PDF to parse first."),
	out: str = typer.Option("da.ttl", "--out", "-o", help="Output DA Turtle path."),
	shacl: str = typer.Option("shacl/da.shacl.ttl", "--shacl", help="SHACL shapes Turtle path for DA validation."),
	offline: bool = typer.Option(True, "--offline/--online", help="When parsing PDFs, disable all network calls."),
	base_uri: str = typer.Option("http://example.org/pdf-grepper/", "--base-uri", help="Base URI for RDF resources (PDF parse only)."),
) -> None:
	"""
	Post-parse Dimensional Analysis (Layer B).

	Produces `da:*` resources grounded in `pg:TextSpan` evidence and validates against SHACL.
	"""
	in_path = Path(input_path)
	pg_ttl_path = in_path
	if in_path.suffix.lower() != ".ttl":
		# Parse first to pg TTL (do not change parse semantics; just reuse pipeline)
		pg_ttl_path = Path(out).with_suffix(".pg.ttl")
		print(f"[bold]pdf-grepper[/bold] parse -> pg ttl={pg_ttl_path}")
		run_pipeline(
			input_paths=[str(in_path)],
			ttl_out=str(pg_ttl_path),
			json_out=None,
			ocr_mode="auto",
			use_cloud=[],
			enrich_web=False,
			offline=offline,
			base_uri=base_uri,
		)

	print(f"[bold]pdf-grepper[/bold] da input={pg_ttl_path} out={out}")
	da_graph = run_da(str(pg_ttl_path), out_ttl=out)
	shapes = load_graph(shacl)
	res = validate_with_pyshacl(da_graph, shapes)
	if not res.conforms:
		print("[red]DA SHACL validation failed[/red]")
		print(res.report_text)
		raise typer.Exit(code=2)
	print(f"[green]Wrote DA Turtle to {out} (SHACL ok)[/green]")


@app.command("meaning")
def meaning_command(
	input_ttl: str = typer.Argument(..., help="Input: a parsed pg Turtle (.ttl)."),
	da: Optional[str] = typer.Option(None, "--da", help="Optional DA Turtle path to include as context/evidence."),
	out: str = typer.Option("meaning.ttl", "--out", "-o", help="Output Meaning Turtle path."),
	shacl: str = typer.Option("shacl/meaning.shacl.ttl", "--shacl", help="SHACL shapes Turtle path for Meaning validation."),
) -> None:
	"""
	Meaning extraction (Layer C).

	Produces conservative `m:Claim` and `m:Procedure/m:Step` resources with mandatory evidence spans and confidence,
	then validates against SHACL.
	"""
	print(f"[bold]pdf-grepper[/bold] meaning input={input_ttl} da={da or ''} out={out}")
	m_graph = run_meaning(input_ttl, da_ttl=da, out_ttl=out)
	shapes = load_graph(shacl)
	res = validate_with_pyshacl(m_graph, shapes)
	if not res.conforms:
		print("[red]Meaning SHACL validation failed[/red]")
		print(res.report_text)
		raise typer.Exit(code=2)
	print(f"[green]Wrote Meaning Turtle to {out} (SHACL ok)[/green]")


if __name__ == "__main__":
	app()


