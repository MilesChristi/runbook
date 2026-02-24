#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
OUT_FILE = DOCS_ROOT / "overrides" / "partials" / "announce.html"

MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")  # support [[...]] si besoin


def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{p.stderr}")
    return p.stdout


def exists_doc(rel: str) -> bool:
    return rel.startswith("docs/") and rel.endswith(".md") and (REPO_ROOT / rel).exists()


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


def normalize_link_to_doc_path(link: str, index_file: Path) -> str | None:
    link = link.strip()

    # Obsidian [[path|label]]
    if "|" in link:
        link = link.split("|", 1)[0].strip()

    link = link.split("#", 1)[0].strip()
    if not link or link.startswith(("http://", "https://", "mailto:")):
        return None

    if link.startswith("/runbook/"):
        link = link.removeprefix("/runbook/")

    base_dir = index_file.parent
    target = (base_dir / link).resolve()

    if target.is_dir():
        target = target / "index.md"

    if not str(target).endswith(".md"):
        target = target / "index.md"

    try:
        rel = target.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return None

    if not rel.startswith("docs/") or not rel.endswith(".md"):
        return None
    return rel


def collect_referenced_docs_from_all_indexes() -> set[str]:
    referenced: set[str] = set()
    for idx in DOCS_ROOT.rglob("index.md"):
        text = idx.read_text(encoding="utf-8", errors="ignore")

        for m in MD_LINK_RE.finditer(text):
            doc = normalize_link_to_doc_path(m.group(1), idx)
            if doc and exists_doc(doc):
                referenced.add(doc)

        for m in WIKI_LINK_RE.finditer(text):
            doc = normalize_link_to_doc_path(m.group(1), idx)
            if doc and exists_doc(doc):
                referenced.add(doc)

    return referenced


def collect_added_modified_lookback(days: int) -> tuple[list[str], list[str]]:
    """
    Retourne (added, modified) sur N jours, en excluant les fichiers supprimés (D).
    """
    out = run([
        "git", "log",
        f"--since={days} days ago",
        "--name-status",
        "--pretty=format:",
        "--", "docs"
    ])

    added: set[str] = set()
    modified: set[str] = set()

    for line in out.splitlines():
        line = line.strip()
        if not line or "\t" not in line:
            continue
        status, path = line.split("\t", 1)
        path = path.strip()

        if not (path.startswith("docs/") and path.endswith(".md")):
            continue

        # si supprimé : on l'enlève des listes éventuelles et on ignore
        if status == "D":
            added.discard(path)
            modified.discard(path)
            continue

        # garde uniquement si le fichier existe encore
        if not exists_doc(path):
            continue

        if status == "A":
            added.add(path)
        elif status == "M":
            modified.add(path)

    # évite doublons
    modified = {f for f in modified if f not in added}
    return sorted(added), sorted(modified)


def render_marquee(added: list[str], modified: list[str], max_items_each: int = 6) -> str:
    # Pas de doublon added vs modified
    added_set = set(added)
    modified = [f for f in modified if f not in added_set]

    items_html: list[str] = []

    for f in added[:max_items_each]:
        items_html.append(
            f'<span class="mc-announce__item">✅ <a href="{md_to_url(f)}">{title_from_file(f)}</a></span>'
        )
    for f in modified[:max_items_each]:
        items_html.append(
            f'<span class="mc-announce__item">🔁 <a href="{md_to_url(f)}">{title_from_file(f)}</a></span>'
        )

    if not items_html:
        return ""

    sep = '<span class="mc-announce__sep">•</span>'
    track = f" {sep} ".join(items_html)
    today = datetime.now().strftime("%d/%m/%Y")

    # ✅ 2 tracks identiques, mais le contenu n'est écrit qu'une seule fois par track
    return f"""<div class="md-banner mc-announce" role="status" aria-label="Nouveautés">
  <div class="mc-announce__inner">
    <span class="mc-announce__label">NOUVEAUTÉS</span>

    <div class="mc-announce__marquee" aria-hidden="true">
      <div class="mc-announce__track mc-announce__track--a">
        {track}
      </div>
      <div class="mc-announce__track mc-announce__track--b">
        {track}
      </div>
    </div>

    <div class="mc-announce__static">
      📌 Nouveautés ({today}) — {items_html[0]}
    </div>
  </div>
</div>
"""

def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    days = int(os.getenv("ANNOUNCE_LOOKBACK_DAYS", "14"))

    referenced = collect_referenced_docs_from_all_indexes()
    added, modified = collect_added_modified_lookback(days)

    # ✅ filtre index + existence déjà assurée
    added_f = [f for f in added if f in referenced]
    modified_f = [f for f in modified if f in referenced]

    OUT_FILE.write_text(render_marquee(added_f, modified_f), encoding="utf-8")


if __name__ == "__main__":
    main()