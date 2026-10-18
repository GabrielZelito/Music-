#!/usr/bin/env python3
import json
import os
import urllib.request

USERNAME = os.getenv("GITHUB_USERNAME", "GabrielZelito")
TOKEN = os.getenv("GITHUB_TOKEN", "")
START, END = "<!-- PROJECTS:START -->", "<!-- PROJECTS:END -->"

headers = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "profile-readme-project-updater",
    "X-GitHub-Api-Version": "2022-11-28",
}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

req = urllib.request.Request(
    f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=pushed&direction=desc&type=owner",
    headers=headers,
)
with urllib.request.urlopen(req, timeout=30) as response:
    repos = json.load(response)

repos = [r for r in repos if not r.get("private") and not r.get("fork")
         and r.get("name", "").lower() != USERNAME.lower()]
repos.sort(key=lambda r: r.get("pushed_at") or r.get("updated_at") or "", reverse=True)

def cell(value):
    return str(value or "").replace("|", r"\\|").replace("\\n", " ").strip()

lines = [
    "_Automatically refreshed by GitHub Actions. Showing your most recently updated public projects._",
    "",
    "| Project | Description | Language | Stars | Last updated |",
    "|---|---|---:|---:|---|",
]
for r in repos[:8]:
    name = cell(r.get("name"))
    desc = cell(r.get("description")) or "No description added yet."
    if len(desc) > 100:
        desc = desc[:97] + "..."
    lang = cell(r.get("language")) or "—"
    updated = (r.get("pushed_at") or r.get("updated_at") or "")[:10] or "—"
    lines.append(f"| [{name}]({r.get('html_url')}) | {desc} | {lang} | ⭐ {r.get('stargazers_count', 0)} | {updated} |")

if not repos:
    lines.append("| _No public project repositories found yet_ | — | — | — | — |")

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()
if START not in content or END not in content:
    raise SystemExit("Could not find PROJECTS markers in README.md")
before, rest = content.split(START, 1)
_, after = rest.split(END, 1)
new_content = before + START + "\n" + "\n".join(lines) + "\n" + END + after
if new_content != content:
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("README project table updated.")
else:
    print("README project table is already up to date.")
