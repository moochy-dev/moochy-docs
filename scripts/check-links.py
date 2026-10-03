#!/usr/bin/env python3
"""Fails when a relative Markdown link points to a file that does not exist."""
import os
import re
import subprocess
import sys

root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip()
files = subprocess.run(["git", "-C", root, "ls-files", "*.md"], capture_output=True, text=True, check=True).stdout.split()
broken = []
for f in files:
    with open(os.path.join(root, f), encoding="utf-8") as fh:
        text = fh.read()
    text = re.sub(r"```.*?```", "", text, flags=re.S)  # code blocks
    text = re.sub(r"`[^`\n]*`", "", text)  # inline code (regexes look like links)
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        path = target.split("#")[0]
        if not path or re.match(r"[a-z]+:", target):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(root, os.path.dirname(f), path))):
            broken.append(f"{f}: {target}")
print("\n".join(broken) or f"{len(files)} files: every relative link resolves")
sys.exit(1 if broken else 0)
