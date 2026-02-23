import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = DOCS / "overrides" / "partials" / "announce.html"

MAX_ITEMS = 6

EXCLUDE = {
    "docs/index.md",
}
EXCLUDE_PREFIXES = (
    "docs/templates/",
    "docs/overrides/",
)

def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True, encoding="utf-8").strip()

def is_doc(path: str) -> bool:
    if not path.startswith("docs/") or not path.endswith(".md"):
        return False
    if path in EXCLUDE:
        return False
    if any(path.startswith(p) for p in EXCLUDE_PREFIXES):
        return False
    return True

def md_to_url(md_path: str) -> str:
    # mkdocs/material style: foo/bar.md -> foo/bar/
    rel = md_path.replace("docs/", "").replace(".md", "/")
    if rel == "index/":
        return "./"
    # dossier/index.md -> dossier/
    rel = rel.replace("/index/", "/")
    return "./" + rel

def title_from_file(md_path: str) -> str:
    p = ROOT / md_path
    if not p.exists():
        return md_path
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return p.stem

def main():
    # Liste des changements récents (derniers commits) : ajoute/modify/rename
    # Format : <date ISO>|<status>|<path>
    log = run([
        "git", "log", "-n", "30",
        "--name-status",
        "--date=short",
        "--pretty=format:%ad"
    ])

    items = []
    current_date = None

    for line in log.splitlines():
        line = line.strip()
        if not line:
            continue

        # date seule (ex: 2026-02-23)
        if len(line) == 10 and line[4] == "-" and line[7] == "-":
            current_date = line
            continue

        # status + path(s)
        parts = line.split("\t")
        if len(parts) >= 2 and current_date:
            status = parts[0]
            path = parts[-1]  # pour R100 old new -> prends new
            if status[0] in ("A", "M", "R") and is_doc(path):
                title = title_from_file(path)
                url = md_to_url(path)
                items.append((current_date, title, url))

    # dédupe par URL en gardant le plus récent
    seen = set()
    deduped = []
    for d, t, u in items:
        if u in seen:
            continue
        seen.add(u)
        deduped.append((d, t, u))
        if len(deduped) >= MAX_ITEMS:
            break

    if not deduped:
        html = "<div class='mc-announce'><div class='mc-announce__inner'><div class='mc-announce__label'>NOUVEAUTÉS</div><div class='mc-announce__static'>Aucune mise à jour récente.</div></div></div>"
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(html, encoding="utf-8")
        return

    def render_item(d, t, u):
        return f"<span class='mc-announce__item'>🆕 {d} — <a href='{u}'>{t}</a></span>"

    # dupliquer pour boucle fluide (marquee)
    line_items = []
    for d, t, u in deduped:
        line_items.append(render_item(d, t, u))
        line_items.append("<span class='mc-announce__sep'>•</span>")
    track = "\n".join(line_items + line_items)

    static = " • ".join([f"🆕 {d} — {t}" for d, t, _ in deduped])

    html = f"""<div class="mc-announce" role="status" aria-label="Nouveautés">
  <div class="mc-announce__inner">
    <div class="mc-announce__label">NOUVEAUTÉS</div>

    <div class="mc-announce__marquee" aria-hidden="true">
      <div class="mc-announce__track">
        {track}
      </div>
    </div>

    <div class="mc-announce__static" aria-label="Nouveautés (statique)">
      {static}
    </div>
  </div>
</div>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")

if __name__ == "__main__":
    main()