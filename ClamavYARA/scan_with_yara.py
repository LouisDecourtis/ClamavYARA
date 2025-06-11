#!/usr/bin/env python3
"""Scan a given file with all YARA rules present inside signature-base/yara directory.
Printed output will show matches in a colored table (Rich).
"""
import sys
import os
from pathlib import Path
import yara
import re
from rich.console import Console
from rich.table import Table

RULES_DIR = Path(__file__).resolve().parent / "signature-base" / "yara"

console = Console()

def load_rules(external_vars: dict):
    rule_files = list(RULES_DIR.rglob("*.yar")) + list(RULES_DIR.rglob("*.yara"))
    if not rule_files:
        console.print("[bold red]No YARA rule files found in directory[/bold red]", file=sys.stderr)
        sys.exit(2)
    sources = {}
    for idx, rf in enumerate(rule_files):
        try:
            sources[str(idx)] = rf.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:
            console.print(f"[yellow]Skipping rule {rf}: {exc}[/yellow]", file=sys.stderr)
    # Attempt to compile, automatically adding missing external variables if necessary
    while True:
        try:
            compiled = yara.compile(sources=sources, externals=external_vars)
            return compiled, len(sources)
        except yara.SyntaxError as exc:
            m = re.search(r"undefined identifier \"(\w+)\"", str(exc))
            if m:
                missing = m.group(1)
                # Provide empty string default for missing external variable
                if missing not in external_vars:
                    external_vars[missing] = ""
                    continue  # retry compile
            raise  # re-raise other syntax errors

def main():
    if len(sys.argv) < 2:
        console.print("[red]Usage: scan_with_yara.py <file>[/red]", file=sys.stderr)
        sys.exit(1)
    target = Path(sys.argv[1]).expanduser().resolve()
    if not target.exists():
        console.print(f"[red]File {target} does not exist[/red]", file=sys.stderr)
        sys.exit(1)

    # Prepare common external variables for rule sets that expect them
    external_vars = {
        "filepath": str(target),
        "filename": target.name,
        "extension": target.suffix.lstrip('.').lower(),
        "filetype": target.suffix.lstrip('.').lower(),
        "parentdir": target.parent.name,
        "grandparentdir": target.parent.parent.name if target.parent.parent != target.parent else "",
    }

    rules, rule_count = load_rules(external_vars)
    matches = rules.match(str(target))

    console.print(f"[blue]Scanned {rule_count} rules. Detections: {len(matches)}[/blue]")

    table = Table(title=f"YARA results for {target.name}")
    table.add_column("Rule", style="cyan")
    table.add_column("Tags")
    table.add_column("Meta")

    if matches:
        for m in matches:
            tags = ",".join(m.tags) if m.tags else "-"
            meta = ",".join(f"{k}={v}" for k, v in m.meta.items()) if m.meta else "-"
            table.add_row(m.rule, tags, meta)
        console.print(table)
        sys.exit(100)  # Non-zero to indicate detection
    else:
        console.print("[green]No YARA detections.[/green]")
        sys.exit(0)

if __name__ == "__main__":
    main()
