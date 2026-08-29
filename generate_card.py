#!/usr/bin/env python3
"""Generate dark_mode.svg and light_mode.svg for the profile README.

Run locally:   python3 generate_card.py
Run in CI:     same, with GITHUB_TOKEN set as an env var (auto-provided by
               GitHub Actions) for higher API rate limits.
"""
import sys
import yaml
import requests

sys.path.insert(0, "lib")
from ascii_art import image_to_ascii
from gh_stats import fetch_stats
from render import build_info_lines, render_svg

CONFIG_PATH = "config.yml"
AVATAR_TMP = "_avatar_live.png"


def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def download_live_avatar(url: str, dest: str):
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    with open(dest, "wb") as f:
        f.write(r.content)


def main():
    cfg = load_config()
    handle = cfg["github_handle"]

    print(f"Fetching live GitHub stats for {handle}...")
    stats = fetch_stats(handle)

    avatar_path = cfg.get("avatar_path", "avatar.png")
    if avatar_path == "avatar.png" and stats.get("avatar_url"):
        # Always refresh from the live avatar unless the user pinned a custom file.
        try:
            download_live_avatar(stats["avatar_url"], AVATAR_TMP)
            avatar_path = AVATAR_TMP
        except Exception as e:
            print(f"Could not download live avatar ({e}), using local fallback.")

    ascii_lines = image_to_ascii(avatar_path, cfg.get("ascii_cols", 60))
    rows = build_info_lines(cfg, stats)

    for theme in ("dark", "light"):
        svg = render_svg(ascii_lines, rows, theme)
        out_path = f"{theme}_mode.svg"
        with open(out_path, "w") as f:
            f.write(svg)
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
