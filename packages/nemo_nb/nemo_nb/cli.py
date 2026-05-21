#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""CLI for nemo-nb converter.

This module provides the main entry point for the nemo-nb console command.

Markdown File Types:
--------------------
There are TWO types of Markdown files in the nemo-nb ecosystem:

1. **MD (notebook format)**:
   - A source markdown file that represents a notebook
   - Can be converted to/from .ipynb 1:1
   - Uses simple markdown with code fences for cells
   - Default filename when converting from .ipynb: `.md`
   - Example: notebook.md

2. **MD (Sphinx docs format)**:
   - A generated markdown file processed for Sphinx rendering
   - Created from notebooks with marker commands processed
   - Includes MyST directives (tab-sets, dropdowns, etc.)
   - Default filename when converting from .ipynb: `.sphinx.md`
   - Example: notebook.sphinx.md

Conversion Path:
----------------
MD (notebook) ? .ipynb ? MD (Sphinx docs) ? HTML (via Sphinx)

The CLI supports all conversions:
- MD (notebook) ? .ipynb (bidirectional, 1:1 conversion)
- .ipynb ? MD (notebook) (bidirectional, default)
- MD (notebook) OR .ipynb ? MD (Sphinx docs) (for local testing/preview)
"""

import json
import tempfile
import traceback
from pathlib import Path
from typing import Annotated, Optional

import typer

from nemo_nb.converter import NotebookConverter, NotebookToMarkdownConverter
from nemo_nb.md_to_notebook import MarkdownToNotebookConverter
from nemo_nb.sphinx import should_process_markdown, should_process_notebook
from nemo_nb.structures import Cell
from nemo_nb.sugar import PassOptions, SugarPipeline

# Create main app
app = typer.Typer(
    help="Convert between Jupyter notebooks and Markdown files",
    no_args_is_help=True,
    add_completion=False,
)


@app.command(name="md-to-nb")
def md_to_nb(
    input_file: Annotated[Path, typer.Argument(help="Input Markdown file (notebook format)")],
    output: Annotated[
        Optional[Path], typer.Argument(help="Output notebook file (optional, defaults to INPUT.ipynb)")
    ] = None,
    overwrite: Annotated[bool, typer.Option("--overwrite", help="Overwrite existing output files")] = False,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Show what would be converted without writing files")
    ] = False,
):
    """Convert Markdown (notebook format) to Jupyter Notebook.

    Examples:
      nemo-nb md-to-nb notebook.md              # Creates notebook.ipynb
      nemo-nb md-to-nb input.md output.ipynb    # Explicit output path

    Note: This converts MD (notebook format) to .ipynb. The markdown file should
    contain code fences and optional output cell markers.
    """
    if not input_file.exists():
        typer.echo(f"Error: Input file does not exist: {input_file}", err=True)
        raise typer.Exit(1)

    if input_file.suffix != ".md":
        typer.echo("Error: Expected .md file for md-to-nb conversion", err=True)
        raise typer.Exit(1)

    # Determine output path
    output_path = output if output else input_file.with_suffix(".ipynb")

    # Check if output exists
    if output_path.exists():
        if should_process_markdown(input_file) or should_process_notebook(output_path):
            typer.echo(
                f"Error: Conflict detected. Both {input_file} and {output_path} exist and at least one is marked for processing.",
                err=True,
            )
            raise typer.Exit(1)

        if not overwrite:
            typer.echo(f"Error: Output file exists: {output_path}", err=True)
            typer.echo("Use --overwrite to overwrite existing files", err=True)
            raise typer.Exit(1)

    try:
        converter = MarkdownToNotebookConverter()
        notebook = converter.convert(input_file)

        if dry_run:
            typer.echo(f"Would convert: {input_file} -> {output_path}")
            return

        converter.write_notebook(notebook, output_path)
        typer.echo(f"Converted: {input_file} -> {output_path}")

    except Exception as e:
        typer.echo(f"Error converting {input_file}: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(1)


@app.command(name="nb-to-md")
def nb_to_md(
    input_file: Annotated[Path, typer.Argument(help="Input notebook file")],
    output: Annotated[
        Optional[Path], typer.Argument(help="Output markdown file (optional, defaults to INPUT.md)")
    ] = None,
    overwrite: Annotated[bool, typer.Option("--overwrite", help="Overwrite existing output files")] = False,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Show what would be converted without writing files")
    ] = False,
):
    """Convert Jupyter Notebook to Markdown (notebook format).

    Examples:
      nemo-nb nb-to-md notebook.ipynb                # Creates notebook.md
      nemo-nb nb-to-md notebook.ipynb output.md      # Explicit output path
      nemo-nb nb-to-md notebook.ipynb --overwrite    # Overwrite existing file

    Note: This creates MD (notebook format) - a simple 1:1 conversion that can be
    converted back to .ipynb with 'md-to-nb'. For Sphinx docs format, use 'to-sphinx-md'.
    """
    if not input_file.exists():
        typer.echo(f"Error: Input file does not exist: {input_file}", err=True)
        raise typer.Exit(1)

    if input_file.suffix != ".ipynb":
        typer.echo("Error: Expected .ipynb file for nb-to-md conversion", err=True)
        raise typer.Exit(1)

    # Determine output path
    output_path = output if output else input_file.with_suffix(".md")

    # Check if output exists
    if output_path.exists():
        if should_process_notebook(input_file) or should_process_markdown(output_path):
            typer.echo(
                f"Error: Conflict detected. Both {input_file} and {output_path} exist and at least one is marked for processing.",
                err=True,
            )
            raise typer.Exit(1)

        if not overwrite:
            typer.echo(f"Error: Output file exists: {output_path}", err=True)
            typer.echo("Use --overwrite to overwrite existing files", err=True)
            raise typer.Exit(1)

    try:
        if dry_run:
            typer.echo(f"Would convert: {input_file} -> {output_path} (notebook format)")
            return

        # Convert to MD (notebook format) using fence format
        converter = NotebookToMarkdownConverter()
        md_content = converter.convert(input_file)
        output_path.write_text(md_content, encoding="utf-8")
        typer.echo(f"Converted: {input_file} -> {output_path} (notebook format)")

    except Exception as e:
        typer.echo(f"Error converting {input_file}: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(1)


@app.command(name="to-sphinx-md")
def to_sphinx_md(
    input_file: Annotated[Path, typer.Argument(help="Input file (.ipynb or .md in notebook format)")],
    output: Annotated[
        Optional[Path], typer.Argument(help="Output markdown file (optional, defaults to INPUT.sphinx.md)")
    ] = None,
    overwrite: Annotated[bool, typer.Option("--overwrite", help="Overwrite existing output files")] = False,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Show what would be converted without writing files")
    ] = False,
):
    """Convert notebook or markdown to Sphinx docs format.

    Examples:
      # From .ipynb
      nemo-nb to-sphinx-md notebook.ipynb            # Creates notebook.sphinx.md

      # From MD (notebook format)
      nemo-nb to-sphinx-md notebook.md         # Creates notebook.sphinx.md

      # Explicit output path
      nemo-nb to-sphinx-md notebook.ipynb output.md  # Creates output.md

    Note: This processes marker commands and generates MyST directives for Sphinx.
    Use this for local testing and preview of documentation rendering.
    """
    if not input_file.exists():
        typer.echo(f"Error: Input file does not exist: {input_file}", err=True)
        raise typer.Exit(1)

    # Determine output path
    output_path = output if output else input_file.with_suffix(".sphinx.md")

    # Check if output exists
    if output_path.exists() and not overwrite:
        typer.echo(f"Error: Output file exists: {output_path}", err=True)
        typer.echo("Use --overwrite to overwrite existing files", err=True)
        raise typer.Exit(1)

    try:
        # Convert either .md or .ipynb to Sphinx MD format
        if input_file.suffix == ".ipynb":
            # Direct conversion from .ipynb to Sphinx MD
            if dry_run:
                typer.echo(f"Would convert: {input_file} -> {output_path} (Sphinx docs format)")
                return

            converter = NotebookConverter()
            md_content = converter.convert(input_file)
            output_path.write_text(md_content, encoding="utf-8")
            typer.echo(f"Converted: {input_file} -> {output_path} (Sphinx docs format)")

        elif input_file.suffix == ".md":
            # Two-step conversion: MD (notebook) -> .ipynb -> MD (Sphinx docs)
            if dry_run:
                typer.echo(f"Would convert: {input_file} -> {output_path} (Sphinx docs format, via .ipynb)")
                return

            # Step 1: Convert MD to notebook (in memory)
            with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as tmp:
                tmp_notebook_path = Path(tmp.name)

            try:
                md_converter = MarkdownToNotebookConverter()
                notebook = md_converter.convert(input_file)
                md_converter.write_notebook(notebook, tmp_notebook_path)

                # Step 2: Convert notebook to Sphinx MD
                sphinx_converter = NotebookConverter()
                md_content = sphinx_converter.convert(tmp_notebook_path)
                output_path.write_text(md_content, encoding="utf-8")
                typer.echo(f"Converted: {input_file} -> {output_path} (Sphinx docs format)")
            finally:
                # Clean up temp file
                if tmp_notebook_path.exists():
                    tmp_notebook_path.unlink()
        else:
            typer.echo("Error: Expected .md or .ipynb file for to-sphinx-md conversion", err=True)
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"Error converting {input_file}: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(1)


@app.command(name="add-sugar")
def add_sugar(
    input_file: Annotated[Path, typer.Argument(help="Input file (.ipynb or .md)")],
    output: Annotated[
        Optional[Path], typer.Argument(help="Output file (optional, defaults to overwrite input)")
    ] = None,
    check: Annotated[
        bool, typer.Option("--check", help="Check if adding sugar would change the file without modifying it")
    ] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show which passes are being applied")] = False,
):
    """Apply syntax sugar markers to a notebook using compiler-style passes.

    The add-sugar command runs a pipeline of passes that detect and transform
    notebook cells. Each pass handles a specific pattern:

    - TabSetPass: Detects ::::{tab-set} and adds multi-cell-indent markers
    - TabItemPass: Detects :::{tab-item} and wraps code cells
    - DropdownPass: Detects :::{dropdown} and wraps code cells
    - LabelInsertPass: Detects MyST labels and adds insert markers

    The file must contain the @nemo-nb: process marker to have sugar added.

    For .ipynb files:
      - Validates the process marker exists
      - Converts to .md format before processing (normalizes representation)
      - Applies sugar passes
      - Converts back to .ipynb

    For .md files:
      - Validates the process marker exists
      - Converts to notebook cells
      - Applies sugar passes
      - Writes back to .md format

    Examples:
      nemo-nb add-sugar notebook.ipynb              # Updates notebook.ipynb in-place
      nemo-nb add-sugar tutorial.md                 # Updates tutorial.md in-place
      nemo-nb add-sugar input.ipynb output.ipynb    # Writes to output.ipynb
      nemo-nb add-sugar notebook.ipynb --check      # Checks if changes are needed
      nemo-nb add-sugar notebook.ipynb --verbose    # Show pass execution
    """
    if not input_file.exists():
        typer.echo(f"Error: Input file does not exist: {input_file}", err=True)
        raise typer.Exit(1)

    suffix = input_file.suffix.lower()
    if suffix not in [".ipynb", ".md"]:
        typer.echo("Error: Expected .ipynb or .md file for add-sugar command", err=True)
        raise typer.Exit(1)

    # Validate process marker exists
    if suffix == ".ipynb":
        if not should_process_notebook(input_file):
            typer.echo(
                f"Error: {input_file} does not contain the @nemo-nb: process marker.\n"
                "Add '# @nemo-nb: process' to a code cell or '<!-- @nemo-nb: process -->' to a markdown cell.",
                err=True,
            )
            raise typer.Exit(1)
    else:  # .md
        if not should_process_markdown(input_file):
            typer.echo(
                f"Error: {input_file} does not contain the @nemo-nb: process marker.\n"
                "Add '<!-- @nemo-nb: process -->' anywhere in the document or set 'nemo_nb.process: true' in frontmatter.",
                err=True,
            )
            raise typer.Exit(1)

    output_path = output if output else input_file

    try:
        if suffix == ".ipynb":
            _add_sugar_ipynb(input_file, output_path, check, verbose)
        else:
            _add_sugar_md(input_file, output_path, check, verbose)

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"Error adding sugar to {input_file}: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(1)


def _add_sugar_ipynb(input_file: Path, output_path: Path, check: bool, verbose: bool) -> None:
    """Add sugar to an .ipynb file by converting through .md format.

    Flow: .ipynb -> .md -> cells -> sugared cells -> .ipynb
    """
    if verbose:
        typer.echo(f"Converting {input_file} to markdown format...")

    # Step 1: Convert .ipynb to .md (normalizes representation)
    nb_to_md_converter = NotebookToMarkdownConverter()
    md_content = nb_to_md_converter.convert(input_file)

    # Step 2: Write to temp .md file and convert to notebook cells
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp_md:
        tmp_md.write(md_content)
        tmp_md_path = Path(tmp_md.name)

    try:
        # Step 3: Convert .md to notebook (gives us Cell objects)
        md_to_nb_converter = MarkdownToNotebookConverter()
        notebook_dict = md_to_nb_converter.convert(tmp_md_path)

        # Load original notebook to preserve metadata
        original_content = input_file.read_text(encoding="utf-8")
        original_notebook = json.loads(original_content)

        # Step 4: Apply sugar passes
        cells = [Cell.from_dict(c) for c in notebook_dict.get("cells", [])]
        options = PassOptions(verbose=verbose)
        pipeline = SugarPipeline()

        if verbose:
            typer.echo(f"Running {len(pipeline.passes)} passes:")
            for p in pipeline.passes:
                typer.echo(f"  - {p.name}")

        sugared_cells = pipeline.run(cells, options)
        new_cells = [c.to_dict() for c in sugared_cells]

        # Check mode
        if check:
            old_cells_json = json.dumps(original_notebook.get("cells", []), sort_keys=True)
            new_cells_json = json.dumps(new_cells, sort_keys=True)

            if old_cells_json != new_cells_json:
                typer.echo(f"Add-sugar would modify {input_file}")
                raise typer.Exit(1)
            else:
                typer.echo(f"No changes needed for {input_file}")
                return

        # Step 5: Write back to .ipynb (preserve original metadata)
        original_notebook["cells"] = new_cells
        output_path.write_text(json.dumps(original_notebook, indent=1), encoding="utf-8")
        typer.echo(
            f"\U0001f36c\u001b[38;2;255;0;0mS\u001b[38;2;255;127;0mt\u001b[38;2;255;255;0my\u001b[38;2;0;255;0ml\u001b[38;2;0;0;255mi\u001b[38;2;75;0;130mz\u001b[38;2;148;0;211me\u001b[38;2;255;0;0md\u001b[0m\U0001f36c: {input_file} -> {output_path}"
        )

    finally:
        if tmp_md_path.exists():
            tmp_md_path.unlink()


def _add_sugar_md(input_file: Path, output_path: Path, check: bool, verbose: bool) -> None:
    """Add sugar to an .md file directly.

    Flow: .md -> cells -> sugared cells -> .ipynb -> .md
    """
    if verbose:
        typer.echo(f"Converting {input_file} to notebook cells...")

    # Step 1: Convert .md to notebook cells
    md_to_nb_converter = MarkdownToNotebookConverter()
    notebook_dict = md_to_nb_converter.convert(input_file)

    # Step 2: Apply sugar passes
    cells = [Cell.from_dict(c) for c in notebook_dict.get("cells", [])]
    options = PassOptions(verbose=verbose)
    pipeline = SugarPipeline()

    if verbose:
        typer.echo(f"Running {len(pipeline.passes)} passes:")
        for p in pipeline.passes:
            typer.echo(f"  - {p.name}")

    sugared_cells = pipeline.run(cells, options)
    new_cells = [c.to_dict() for c in sugared_cells]

    # Step 3: Write to temp .ipynb and convert back to .md
    notebook_dict["cells"] = new_cells

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False, encoding="utf-8") as tmp_nb:
        json.dump(notebook_dict, tmp_nb, indent=1)
        tmp_nb_path = Path(tmp_nb.name)

    try:
        # Convert back to .md
        nb_to_md_converter = NotebookToMarkdownConverter()
        new_md_content = nb_to_md_converter.convert(tmp_nb_path)

        # Check mode
        if check:
            original_content = input_file.read_text(encoding="utf-8")
            if original_content != new_md_content:
                typer.echo(f"Add-sugar would modify {input_file}")
                raise typer.Exit(1)
            else:
                typer.echo(f"No changes needed for {input_file}")
                return

        # Write output
        output_path.write_text(new_md_content, encoding="utf-8")
        typer.echo(
            f"\U0001f36c\u001b[38;2;255;0;0mS\u001b[38;2;255;127;0mt\u001b[38;2;255;255;0my\u001b[38;2;0;255;0ml\u001b[38;2;0;0;255mi\u001b[38;2;75;0;130mz\u001b[38;2;148;0;211me\u001b[38;2;255;0;0md\u001b[0m\U0001f36c: {input_file} -> {output_path}"
        )

    finally:
        if tmp_nb_path.exists():
            tmp_nb_path.unlink()


def main():
    """Main CLI entry point for nemo-nb command."""
    app()


if __name__ == "__main__":
    main()
