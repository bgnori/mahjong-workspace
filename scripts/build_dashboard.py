#!/usr/bin/env python3

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_FILES = ("index.html", "dashboard.js", "repositories.json")
SHARED_FILES = ("metrics.js", "metrics.css")


def build(site: Path, ci_assets: Path) -> None:
    site.mkdir(parents=True, exist_ok=True)
    dashboard = site / "dashboard"
    dashboard.mkdir()
    shutil.copy2(ROOT / "web" / "index.html", site / "index.html")
    for name in DASHBOARD_FILES:
        shutil.copy2(ROOT / "web" / "dashboard" / name, dashboard / name)
    for name in SHARED_FILES:
        shutil.copy2(ci_assets / name, dashboard / name)
    (site / ".nojekyll").touch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble the workspace Pages dashboard.")
    parser.add_argument("site", type=Path)
    parser.add_argument("--ci-assets", type=Path, required=True)
    args = parser.parse_args()
    build(args.site, args.ci_assets)
