#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = REPO_ROOT / "docs" / "overrides" / "partials" / "announce.html"


def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{p.stderr}")
    return p.stdout


def is_doc(path: str) -> bool:
    return path.startswith("docs/") and path.endswith(".md")


def md_to_url(md_path: str) -> str:
    rel = md_path.removeprefix("docs/").removesuffix(".md")
    if rel == "index":
        return "/runbook/"
    if rel.endswith("/index"):
        rel = rel.removesuffix("/index")
    return f"/runbook/{rel}/"


def title_from_file(md_path: str) -> str:
    p = REPO_ROOT / md_path
    if not p.exists():
        return Path(md_path).stem.replace("-", " ").title()
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return Path(md_path).stem.replace("-", " ").title()


def collect_changes_lookback(days: int) -> tuple[list[str], list[str]]:
    """
    Retourne (added, modified) sur les N derniers jours.
    On parse `git log --name-status` et on garde les fichiers docs/*.md.
    """
    out = run([
        "git", "log",
        f"--since={days}.days",
        "--name-status",
        "--pretty=format:"
        , "--", "docs"
    ])

    added: list[str] = []
    modified: list[str] = []

    # git log --name-status produit des lignes:
    # A<TAB>docs/xxx.md
    # M<TAB>docs/yyy.md
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        # exemple: "A\tdocs/installations/fog-installation.md"
        if "\t" not in line:
            continue
        status, path = line.split("\t", 1)
        path = path.strip()
        if not is_doc(path):
            continue

        if status == "A" and path not in added:
            added.append(path)
        elif status == "M" and path not in modified:
            modified.append(path)

    # évite doublon (un fichier ajouté peut aussi être marqué M)
    modified = [f for f in modified if f not in set(added)]
    return added, modified


def render_section(title: str, files: list[str], max_items: int = 6) -> str:
    files = files[:max_items]
    items = "\n".join(
        f'<li><a href="{md_to_url(f)}">{title_from_file(f)}</a></li>' for f in files
    )
    return f"""
    <details class="mc-announce__details" open>
      <summary>{title} <span class="mc-badge">{len(files)}</span></summary>
      <ul>
        {items}
      </ul>
    </details>
    """.strip()


def render(added: list[str], modified: list[str]) -> str:
    if not added and not modified:
        return ""

    today = datetime.now().strftime("%d/%m/%Y")

    parts = []
    if added:
        parts.append(render_section("✅ Nouvelles procédures", added))
    if modified:
        parts.append(render_section("🔁 Procédures mises à jour", modified))

    sections_html = "\n".join(parts)

    return f"""<div class="md-banner mc-announce" role="status" aria-label="Nouveautés">
  <div class="mc-announce__inner">
    <strong>📌 Nouveautés</strong> <span class="mc-announce__date">({today})</span>
    {sections_html}
  </div>
</div>
"""


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # configurable via env, défaut 14 jours
    days = int(os.getenv("ANNOUNCE_LOOKBACK_DAYS", "14"))

    added, modified = collect_changes_lookback(days)
    OUT_FILE.write_text(render(added, modified), encoding="utf-8")


if __name__ == "__main__":
    main()