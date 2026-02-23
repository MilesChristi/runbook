#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = REPO_ROOT / "docs" / "overrides" / "partials" / "announce.html"

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{p.stderr}")
    return p.stdout.strip()


def is_doc(path: str) -> bool:
    # uniquement les docs markdown
    return path.startswith("docs/") and path.endswith(".md")


def md_to_url(md_path: str) -> str:
    # docs/installations/fog-installation.md -> /runbook/installations/fog-installation/
    # docs/index.md -> /runbook/
    rel = md_path.removeprefix("docs/").removesuffix(".md")
    if rel == "index":
        return "/runbook/"
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


def changed_docs_from_push() -> list[str]:
    """
    GitHub Actions : on passe BEFORE_SHA et AFTER_SHA depuis le workflow
    (github.event.before et github.sha).
    """
    before = os.getenv("BEFORE_SHA")
    after = os.getenv("AFTER_SHA") or os.getenv("GITHUB_SHA")

    if before and after and before != "0000000000000000000000000000000000000000":
        diff = run(["git", "diff", "--name-only", f"{before}..{after}"])
        files = [f.strip() for f in diff.splitlines() if f.strip()]
        return sorted({f for f in files if is_doc(f)})

    # Fallback local/si env absente : dernier commit
    diff = run(["git", "diff", "--name-only", "HEAD~1..HEAD"])
    files = [f.strip() for f in diff.splitlines() if f.strip()]
    return sorted({f for f in files if is_doc(f)})


def render(changed: list[str]) -> str:
    if not changed:
        return ""

    # max 6 liens, sinon c'est illisible
    changed = changed[:6]
    items = "\n".join(
        f'<li><a href="{md_to_url(f)}">{title_from_file(f)}</a></li>' for f in changed
    )

    today = datetime.now().strftime("%d/%m/%Y")

    return f"""<div class="md-banner mc-announce" role="status" aria-label="Maintenance">
  <div class="mc-announce__inner">
    <strong>⚠️ Maintenance</strong> : certaines procédures ont été mises à jour <span class="mc-announce__date">({today})</span>.
    <details class="mc-announce__details">
      <summary>Voir les changements</summary>
      <ul>
        {items}
      </ul>
    </details>
  </div>
</div>
"""


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    changed = changed_docs_from_push()
    OUT_FILE.write_text(render(changed), encoding="utf-8")


if __name__ == "__main__":
    main()