#!/usr/bin/env python3
"""
Build the static website plus an auto-generated progress section for
`wp-phase-contrast-maps/`.

The generated site keeps the hand-authored root pages intact and adds a
mirrored subtree at `wp-phase-contrast-maps/` with:
  - markdown converted to HTML
  - raw files copied through for download
  - directory indexes for logbook, numerics, and plots
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Iterable
from urllib.parse import urlsplit, urlunsplit

import markdown


ROOT = Path(__file__).resolve().parents[1]
WP_ROOT = ROOT / "wp-phase-contrast-maps"
STATIC_DIRS = ("js", "data", "scripts", "schemas")
STATIC_FILE_SUFFIXES = {".html", ".css", ".md"}
SKIP_DIR_NAMES = {".git", ".github", "__pycache__"}


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_root_site(output_dir: Path) -> None:
    for item in ROOT.iterdir():
        if item.name in SKIP_DIR_NAMES:
            continue
        if item == output_dir or output_dir in item.parents:
            continue
        if item.is_file() and item.suffix in STATIC_FILE_SUFFIXES:
            shutil.copy2(item, output_dir / item.name)
        elif item.is_dir() and item.name in STATIC_DIRS:
            shutil.copytree(
                item,
                output_dir / item.name,
                ignore=shutil.ignore_patterns(*SKIP_DIR_NAMES),
            )


def copy_wp_assets(output_dir: Path) -> None:
    dest_root = output_dir / WP_ROOT.name
    for src in WP_ROOT.rglob("*"):
        if any(part in SKIP_DIR_NAMES for part in src.parts):
            continue
        rel = src.relative_to(WP_ROOT)
        dest = dest_root / rel
        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def md_destination(source_md: Path, output_dir: Path) -> Path:
    rel = source_md.relative_to(WP_ROOT)
    if rel.name.lower() == "readme.md":
        return output_dir / WP_ROOT.name / rel.parent / "index.html"
    return output_dir / WP_ROOT.name / rel.with_suffix(".html")


def first_heading(markdown_text: str, fallback: str) -> str:
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return fallback


def first_paragraph(markdown_text: str) -> str:
    blocks = re.split(r"\n\s*\n", markdown_text.strip())
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if lines[0].startswith("#"):
            continue
        joined = " ".join(lines)
        joined = re.sub(r"`([^`]+)`", r"\1", joined)
        joined = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", joined)
        joined = joined.replace("**", "").replace("*", "")
        return joined
    return ""


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{num_bytes} B"


def rel_href(from_page: Path, to_page: Path) -> str:
    return os.path.relpath(to_page, start=from_page.parent).replace(os.sep, "/")


def rel_to_root_asset(from_page: Path, relative_to_root: str, output_dir: Path) -> str:
    return rel_href(from_page, output_dir / relative_to_root)


def rewrite_markdown_links(markdown_text: str, source_md: Path) -> str:
    pattern = re.compile(r"(!?\[[^\]]*\]\()([^)]+)(\))")

    def replace(match: re.Match[str]) -> str:
        prefix, target, suffix = match.groups()
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or parsed.path.startswith("/") or parsed.path == "":
            return match.group(0)
        path = PurePosixPath(parsed.path)
        resolved = (source_md.parent / Path(path.as_posix())).resolve()
        if path.suffix.lower() == ".md" and resolved.is_relative_to(WP_ROOT.resolve()):
            if path.name.lower() == "readme.md":
                path = path.with_name("index.html")
            else:
                path = path.with_suffix(".html")
            target = urlunsplit(("", "", path.as_posix(), parsed.query, parsed.fragment))
            return f"{prefix}{target}{suffix}"
        return match.group(0)

    return pattern.sub(replace, markdown_text)


def normalize_markdown(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    normalized: list[str] = []
    for line in lines:
        if (
            normalized
            and normalized[-1].strip()
            and re.match(r"^>\s*[\d(+-]", line)
        ):
            normalized[-1] = normalized[-1].rstrip() + " " + re.sub(r"^>\s*", "> ", line.strip())
        else:
            normalized.append(line)
    return "\n".join(normalized)


def markdown_to_html(markdown_text: str) -> str:
    renderer = markdown.Markdown(
        extensions=[
            "extra",
            "admonition",
            "toc",
            "sane_lists",
        ],
        output_format="html5",
    )
    return renderer.convert(markdown_text)


def nav_markup(current_page: Path, output_dir: Path, current_key: str) -> str:
    items = [
        ("overview", "Overview", output_dir / "index.html"),
        ("dossier", "Dossier", output_dir / "dossier.html"),
        ("framework", "Framework", output_dir / "framework.html"),
        ("tutorial", "Tutorial", output_dir / "tutorial.html"),
        ("numerics", "Numerics", output_dir / "numerics.html"),
        ("simulate", "Simulate", output_dir / "simulate.html"),
        ("code", "Code", output_dir / "code.html"),
        ("reference", "Reference", output_dir / "reference.html"),
        ("start", "Start", output_dir / "getting-started.html"),
        ("progress", "Progress", output_dir / WP_ROOT.name / "index.html"),
    ]
    links = []
    for key, label, target in items:
        aria = ' aria-current="page"' if key == current_key else ""
        href = rel_href(current_page, target)
        links.append(f'    <a href="{href}"{aria}>{html.escape(label)}</a>')
    return "<nav>\n" + "\n".join(links) + "\n  </nav>"


def breadcrumbs_markup(current_page: Path, output_dir: Path) -> str:
    progress_root = output_dir / WP_ROOT.name / "index.html"
    rel = current_page.relative_to(output_dir / WP_ROOT.name)
    crumbs = [f'<a href="{rel_href(current_page, progress_root)}">WP-E Progress</a>']

    if rel.parent != Path("."):
        accum = output_dir / WP_ROOT.name
        for part in rel.parent.parts:
            accum = accum / part
            crumbs.append(
                f'<a href="{rel_href(current_page, accum / "index.html")}">{html.escape(part.title())}</a>'
            )

    if current_page.name != "index.html":
        crumbs.append(html.escape(current_page.stem.replace("-", " ")))

    return f'<p class="crumbs">{" / ".join(crumbs)}</p>'


def page_shell(
    *,
    title: str,
    subtitle: str,
    current_page: Path,
    output_dir: Path,
    body_html: str,
    source_file: Path | None = None,
) -> str:
    style_href = rel_to_root_asset(current_page, "style.css", output_dir)
    source_note = ""
    if source_file is not None:
        source_href = rel_href(current_page, output_dir / WP_ROOT.name / source_file.relative_to(WP_ROOT))
        source_note = (
            '<div class="meta-block">'
            f'<p><strong>Source:</strong> <a href="{source_href}">{html.escape(source_file.relative_to(ROOT).as_posix())}</a></p>'
            f"<p><strong>Built:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>"
            "</div>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — WP-E Progress</title>
<link rel="stylesheet" href="{style_href}">
</head>
<body>
<div class="page-wrap">

<header>
  <div class="site-id"><a href="https://github.com/threehouse-plus-ec/open-research-platform">Rocket Science</a> · Open Research Platform · Breakwater Layer</div>
  <h1>{html.escape(title)}</h1>
  <p class="subtitle">{html.escape(subtitle)}</p>
{nav_markup(current_page, output_dir, "progress")}
</header>

{breadcrumbs_markup(current_page, output_dir)}
{source_note}

<div class="prose">
{body_html}
</div>

<footer>
  <p>Dossier v0.8 · WP-E progress mirror · generated from <code>{html.escape(WP_ROOT.name)}</code></p>
</footer>

</div>
</body>
</html>
"""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def convert_markdown_files(output_dir: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for source_md in sorted(WP_ROOT.rglob("*.md")):
        raw = source_md.read_text(encoding="utf-8")
        normalized = normalize_markdown(raw)
        rewritten = rewrite_markdown_links(normalized, source_md)
        rendered = markdown_to_html(rewritten)
        dest = md_destination(source_md, output_dir)
        title = first_heading(raw, source_md.stem)
        subtitle = source_md.parent.relative_to(WP_ROOT).as_posix() or "Work package overview"
        page = page_shell(
            title=title,
            subtitle=subtitle,
            current_page=dest,
            output_dir=output_dir,
            body_html=rendered,
            source_file=source_md,
        )
        write_text(dest, page)
        records.append(
            {
                "source": source_md,
                "dest": dest,
                "title": title,
                "summary": first_paragraph(raw),
            }
        )
    return records


def listing_table(current_page: Path, output_dir: Path, files: Iterable[Path]) -> str:
    rows = []
    for file_path in files:
        rel_link = rel_href(current_page, output_dir / WP_ROOT.name / file_path.relative_to(WP_ROOT))
        rows.append(
            "<tr>"
            f"<td><a href=\"{rel_link}\">{html.escape(file_path.name)}</a></td>"
            f"<td>{html.escape(file_path.suffix or 'dir')}</td>"
            f"<td>{human_size(file_path.stat().st_size)}</td>"
            f"<td>{datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</td>"
            "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="4">No files found.</td></tr>')
    return (
        '<table class="compact-table file-table">'
        "<thead><tr><th>File</th><th>Type</th><th>Size</th><th>Modified</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def generate_root_index(output_dir: Path, markdown_records: list[dict[str, object]]) -> None:
    current_page = output_dir / WP_ROOT.name / "index.html"
    logbook_records = [
        record for record in markdown_records if Path(record["source"]).parent.name == "logbook"
    ]
    latest_logs = sorted(logbook_records, key=lambda record: Path(record["source"]).name, reverse=True)[:4]
    plots = sorted((WP_ROOT / "plots").glob("*.png"))
    numerics = sorted((WP_ROOT / "numerics").iterdir())

    cards = [
        (
            "Logbook",
            "Converted research notes and run records.",
            output_dir / WP_ROOT.name / "logbook" / "index.html",
        ),
        (
            "Plots",
            "Rendered figures copied straight from the work package.",
            output_dir / WP_ROOT.name / "plots" / "index.html",
        ),
        (
            "Numerics",
            "Download-only HDF5 datasets and local driver scripts.",
            output_dir / WP_ROOT.name / "numerics" / "index.html",
        ),
    ]

    card_html = "".join(
        f'<a href="{rel_href(current_page, target)}" class="card-link">'
        '<div class="wp-card progress-card">'
        f'<p class="wp-title">{html.escape(title)}</p>'
        f'<p>{html.escape(summary)}</p>'
        "</div></a>"
        for title, summary, target in cards
    )

    latest_html = "".join(
        f'<li><a href="{rel_href(current_page, record["dest"])}">{html.escape(str(record["title"]))}</a>'
        + (
            f'<span class="list-note"> — {html.escape(str(record["summary"]))}</span>'
            if record["summary"]
            else ""
        )
        + "</li>"
        for record in latest_logs
    )

    readme_record = next(
        record for record in markdown_records if Path(record["source"]).relative_to(WP_ROOT).as_posix() == "README.md"
    )
    readme_html = markdown_to_html(
        rewrite_markdown_links(
            normalize_markdown(Path(readme_record["source"]).read_text(encoding="utf-8")),
            Path(readme_record["source"]),
        )
    )

    body_html = f"""
<div class="callout">
  <div class="cl">Generated Section</div>
  <p>This area mirrors the repository folder <code>{html.escape(WP_ROOT.name)}</code>. Markdown is rendered to HTML during the GitHub Pages build, plots are copied through, and numerics files remain download-only.</p>
</div>

<div class="progress-grid">
{card_html}
</div>

<h2>Latest Logbook Entries</h2>
<ul class="link-list">
{latest_html}
</ul>

<h2>Current Snapshot</h2>
<div class="meta-row">
  <div class="meta-item"><span class="meta-key">Logbook files</span><span>{len(logbook_records)}</span></div>
  <div class="meta-item"><span class="meta-key">Plot files</span><span>{len(plots)}</span></div>
  <div class="meta-item"><span class="meta-key">Numerics files</span><span>{len(numerics)}</span></div>
</div>

<hr>

{readme_html}
"""

    page = page_shell(
        title="WP-E Progress",
        subtitle="Forward map and observability work package mirror",
        current_page=current_page,
        output_dir=output_dir,
        body_html=body_html,
        source_file=WP_ROOT / "README.md",
    )
    write_text(current_page, page)


def generate_logbook_index(output_dir: Path, markdown_records: list[dict[str, object]]) -> None:
    current_page = output_dir / WP_ROOT.name / "logbook" / "index.html"
    logbook_records = sorted(
        (
            record
            for record in markdown_records
            if Path(record["source"]).parent.name == "logbook"
        ),
        key=lambda record: Path(record["source"]).name,
        reverse=True,
    )
    body_html = [
        "<p>This logbook index is generated from the markdown files in <code>wp-phase-contrast-maps/logbook/</code>.</p>",
        '<div class="progress-grid">',
    ]
    for record in logbook_records:
        body_html.append(
            f'<a href="{rel_href(current_page, record["dest"])}" class="card-link">'
            '<div class="wp-card progress-card">'
            f'<p class="wp-title">{html.escape(str(record["title"]))}</p>'
            f'<p>{html.escape(Path(record["source"]).name)}</p>'
            + (
                f'<p class="card-note">{html.escape(str(record["summary"]))}</p>'
                if record["summary"]
                else ""
            )
            + "</div></a>"
        )
    body_html.append("</div>")
    page = page_shell(
        title="WP-E Logbook",
        subtitle="Converted markdown entries",
        current_page=current_page,
        output_dir=output_dir,
        body_html="\n".join(body_html),
    )
    write_text(current_page, page)


def generate_numerics_index(output_dir: Path) -> None:
    current_page = output_dir / WP_ROOT.name / "numerics" / "index.html"
    numerics_dir = WP_ROOT / "numerics"
    h5_files = sorted(numerics_dir.glob("*.h5"))
    script_files = sorted(numerics_dir.glob("*.py"))

    body_html = f"""
<div class="callout">
  <div class="cl">Download Only</div>
  <p>The numerics section currently exposes datasets and helper scripts as direct downloads. No browser-side HDF5 rendering is performed in this version of the site.</p>
</div>

<h2>Datasets</h2>
{listing_table(current_page, output_dir, h5_files)}

<h2>Scripts</h2>
{listing_table(current_page, output_dir, script_files)}
"""
    page = page_shell(
        title="WP-E Numerics",
        subtitle="Datasets and drivers",
        current_page=current_page,
        output_dir=output_dir,
        body_html=body_html,
    )
    write_text(current_page, page)


def prettify_stem(name: str) -> str:
    return name.replace("_", " ").replace("-", " ")


def generate_plots_index(output_dir: Path) -> None:
    current_page = output_dir / WP_ROOT.name / "plots" / "index.html"
    plot_files = sorted((WP_ROOT / "plots").glob("*.png"))
    cards = []
    for plot in plot_files:
        href = rel_href(current_page, output_dir / WP_ROOT.name / plot.relative_to(WP_ROOT))
        cards.append(
            '<div class="gallery-card">'
            f'<a href="{href}"><img src="{href}" alt="{html.escape(prettify_stem(plot.stem))}"></a>'
            f'<p class="wp-title">{html.escape(prettify_stem(plot.stem).title())}</p>'
            f'<p class="card-note"><a href="{href}">{html.escape(plot.name)}</a></p>'
            "</div>"
        )

    body_html = """
<p>Plots are copied directly from the repository folder and shown here as a lightweight gallery.</p>
<div class="gallery-grid">
""" + "".join(cards) + """
</div>
"""
    page = page_shell(
        title="WP-E Plots",
        subtitle="Copied figure outputs",
        current_page=current_page,
        output_dir=output_dir,
        body_html=body_html,
    )
    write_text(current_page, page)


def build(output_dir: Path) -> None:
    ensure_clean_dir(output_dir)
    copy_root_site(output_dir)
    copy_wp_assets(output_dir)
    markdown_records = convert_markdown_files(output_dir)
    generate_root_index(output_dir, markdown_records)
    generate_logbook_index(output_dir, markdown_records)
    generate_numerics_index(output_dir)
    generate_plots_index(output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build static site with WP-E progress mirror.")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "_site"),
        help="Directory to write the generated site into.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build(Path(args.output_dir).resolve())


if __name__ == "__main__":
    main()
