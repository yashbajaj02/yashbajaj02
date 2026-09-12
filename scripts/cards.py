from pathlib import Path
import html
import json
import os
import urllib.request

USERNAME = "yashbajaj02"
TOKEN = os.getenv("METRICS_TOKEN") or os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError("METRICS_TOKEN or GITHUB_TOKEN is required")

PINNED_PROJECTS = [
    {"repo": "connect-yash", "title": "Connect", "fallback": "Modern developer portfolio and developer hub"},
    {"repo": "Splity", "title": "Splity", "fallback": "Expense splitting and settlement platform"},
    {"repo": "Filewise", "title": "Filewise", "fallback": "All-in-one file utility platform"},
    {"repo": "pricewise", "title": "Pricewise", "fallback": "Web-based product price comparison application"},
]
EXCLUDED = {"yashbajaj02", "connect-yash", "Splity", "Filewise", "pricewise"}

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(first: 100, ownerAffiliations: OWNER, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        name description url isFork stargazerCount forkCount
        languages(first: 3, orderBy: {field: SIZE, direction: DESC}) { nodes { name } }
      }
    }
  }
}
"""

payload = json.dumps({"query": QUERY, "variables": {"login": USERNAME}}).encode()
request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": USERNAME},
)
with urllib.request.urlopen(request) as response:
    data = json.load(response)
if "errors" in data:
    raise RuntimeError(data["errors"])

repos = data["data"]["user"]["repositories"]["nodes"]
repo_map = {repo["name"]: repo for repo in repos}

projects = []
for item in PINNED_PROJECTS:
    repo = repo_map.get(item["repo"])
    if repo:
        projects.append((item["title"], repo))

for repo in repos:
    if repo["name"] in EXCLUDED or repo.get("isFork"):
        continue
    projects.append((repo["name"].replace("-", " "), repo))
    if len(projects) == 6:
        break

assets = Path("assets")
assets.mkdir(exist_ok=True)

for index, (title, repo) in enumerate(projects, start=1):
    description = (repo.get("description") or "GitHub project").strip()
    if len(description) > 46:
        description = description[:46].rsplit(" ", 1)[0] + "..."
    languages = " • ".join(lang["name"] for lang in repo["languages"]["nodes"][:3]) or "Project"
    title_e = html.escape(title)
    desc_e = html.escape(description)
    lang_e = html.escape(languages)
    stars = repo.get("stargazerCount", 0)
    forks = repo.get("forkCount", 0)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="270" height="150" viewBox="0 0 270 150" role="img" aria-label="{title_e} project card">
<defs><filter id="s"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-opacity=".35"/></filter></defs>
<rect x="4" y="7" width="262" height="138" rx="13" fill="#05070a" opacity=".8"/>
<rect x="2" y="2" width="262" height="138" rx="13" fill="#161b22" stroke="#30363d"/>
<rect x="2" y="2" width="262" height="4" rx="2" fill="#8b5cf6" opacity=".75"/>
<g filter="url(#s)">
<text x="18" y="32" fill="#f0f6fc" font-family="Arial,sans-serif" font-size="17" font-weight="700">{title_e}</text>
<text x="18" y="57" fill="#8b949e" font-family="Arial,sans-serif" font-size="10">{desc_e}</text>
<text x="18" y="84" fill="#39d353" font-family="Arial,sans-serif" font-size="9">{lang_e}</text>
<text x="18" y="108" fill="#8b949e" font-family="Arial,sans-serif" font-size="9">★ {stars}    Forks {forks}</text>
<text x="18" y="128" fill="#58a6ff" font-family="Arial,sans-serif" font-size="10" font-weight="600">Open repository →</text>
</g></svg>'''
    (assets / f"project-{index}.svg").write_text(svg, encoding="utf-8")

rows = []
for i in range(0, len(projects), 2):
    cells = []
    for index in range(i, min(i + 2, len(projects))):
        title, repo = projects[index]
        cells.append(
            f'<td align="center"><a href="{html.escape(repo["url"], quote=True)}"><img src="./assets/project-{index + 1}.svg" width="270" alt="{html.escape(title)}"></a></td>'
        )
    rows.append("<tr>" + "".join(cells) + "</tr>")

project_block = "<!-- PROJECTS:START -->\n<table>\n" + "\n".join(rows) + "\n</table>\n<!-- PROJECTS:END -->"

readme_path = Path("README.md")
readme = readme_path.read_text(encoding="utf-8")
start_marker = "<!-- PROJECTS:START -->"
end_marker = "<!-- PROJECTS:END -->"
if start_marker in readme and end_marker in readme:
    start = readme.index(start_marker)
    end = readme.index(end_marker) + len(end_marker)
    readme = readme[:start] + project_block + readme[end:]
else:
    section = "## ~/ selected work\n\n<div align=\"center\">\n\n" + project_block + "\n\n</div>"
    old = '## ~/ selected work\n\n<div align="center">\n<img src="./assets/project-cards.svg" width="560" alt="Selected Projects"/>\n</div>'
    if old not in readme:
        raise RuntimeError("Could not find the selected work section to replace")
    readme = readme.replace(old, section)
readme_path.write_text(readme, encoding="utf-8")

print("Generated clickable project cards and updated README links.")
for index, (title, repo) in enumerate(projects, start=1):
    print(f"{index}. {title} -> {repo['url']}")
