from pathlib import Path
import json
import os
import urllib.request
import html

USERNAME = "yashbajaj02"
TOKEN = os.getenv("METRICS_TOKEN") or os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError("METRICS_TOKEN or GITHUB_TOKEN is required")

PINNED_PROJECTS = [
    {
        "repo": "connect-yash",
        "title": "Connect",
        "fallback_description": "Modern developer portfolio and developer hub",
        "status": "In development",
    },
    {
        "repo": "Splity",
        "title": "Splity",
        "fallback_description": "Expense splitting and settlement platform",
        "status": "In development",
    },
    {
        "repo": "Filewise",
        "title": "Filewise",
        "fallback_description": "All-in-one file utility platform",
        "status": "In development",
    },
    {
        "repo": "pricewise",
        "title": "Pricewise",
        "fallback_description": "Web-based product price comparison application",
        "status": "In development",
    },
]

EXCLUDED_LIVE_REPOS = {
    "yashbajaj02",
    "connect-yash",
    "Splity",
    "Filewise",
    "pricewise",
}

def select_projects(repos):
    pinned = []

    for project in PINNED_PROJECTS:
        repo = repo_map.get(project["repo"])
        item = dict(project)

        if repo:
            item["live_repo"] = repo

        pinned.append(item)

    live = []
    for repo in repos:
        name = repo["name"]

        if name in EXCLUDED_LIVE_REPOS:
            continue

        if repo.get("isFork"):
            continue

        live.append({
            "repo": name,
            "title": name.replace("-", " "),
            "fallback_description": "GitHub project",
            "status": "Live project",
            "live_repo": repo,
        })

        if len(live) == 2:
            break

    return pinned + live



QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(
      first: 100
      ownerAffiliations: OWNER
      orderBy: {field: UPDATED_AT, direction: DESC}
    ) {
      nodes {
        name
        description
        url
        isPrivate
        stargazerCount
        forkCount
        isFork
        languages(first: 3, orderBy: {field: SIZE, direction: DESC}) {
          nodes {
            name
          }
        }
      }
    }
  }
}
"""

payload = json.dumps({
    "query": QUERY,
    "variables": {"login": USERNAME}
}).encode()

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": USERNAME,
    },
)

with urllib.request.urlopen(request) as response:
    data = json.load(response)

if "errors" in data:
    raise RuntimeError(data["errors"])

repos = data["data"]["user"]["repositories"]["nodes"]
repo_map = {repo["name"]: repo for repo in repos}

PROJECTS = select_projects(repos)

width = 900
card_width = 410
card_height = 190
gap = 20
columns = 2
rows = (len(PROJECTS) + 1) // 2

height = rows * card_height + (rows - 1) * gap

svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
width="{width}" height="{height}"
viewBox="0 0 {width} {height}">

<rect width="100%" height="100%" rx="16" fill="#0d1117"/>
'''

for i, project in enumerate(PROJECTS):

    col = i % columns
    row = i // columns

    x = col * (card_width + gap) + 20
    y = row * (card_height + gap) + 20

    repo_name = project["repo"]
    repo = repo_map.get(repo_name) if repo_name else None

    title = html.escape(project["title"])

    if repo:
        description = repo["description"] or project["fallback_description"]
        description = html.escape(description[:72])

        languages = [
            lang["name"]
            for lang in repo["languages"]["nodes"]
        ]

        language_text = " • ".join(languages[:3])
        language_text = html.escape(language_text or "Project")

        stars = repo["stargazerCount"]
        forks = repo["forkCount"]
        url = html.escape(repo["url"], quote=True)

        status = f"★ {stars}    Forks {forks}"
        link_text = "View repository →"

    else:
        description = html.escape(project["fallback_description"])

        language_text = "Python • AI/ML • Voice Analysis"
        status = "Coming soon"
        url = ""
        link_text = "Coming soon →"

    svg += f'''
<g>

<rect x="{x}" y="{y}"
width="{card_width}" height="{card_height}"
rx="14"
fill="#161b22"
stroke="#30363d"/>

<text x="{x + 22}" y="{y + 38}"
fill="#f0f6fc"
font-family="Arial"
font-size="20"
font-weight="700">
{title}
</text>

<text x="{x + 22}" y="{y + 70}"
fill="#8b949e"
font-family="Arial"
font-size="13">
{description}
</text>

<text x="{x + 22}" y="{y + 105}"
fill="#39d353"
font-family="Arial"
font-size="12">
{language_text}
</text>

<text x="{x + 22}" y="{y + 138}"
fill="#8b949e"
font-family="Arial"
font-size="12">
{status}
</text>
'''

    if url:
        svg += f'''
<a href="{url}">
<text x="{x + 22}" y="{y + 168}"
fill="#58a6ff"
font-family="Arial"
font-size="12"
font-weight="600">
{link_text}
</text>
</a>
'''
    else:
        svg += f'''
<text x="{x + 22}" y="{y + 168}"
fill="#8b949e"
font-family="Arial"
font-size="12"
font-weight="600">
{link_text}
</text>
'''

    svg += "</g>"

svg += "</svg>"

Path("assets/project-cards.svg").write_text(svg)

print("Generated assets/project-cards.svg")
print()
print("Projects:")
for project in PROJECTS:
    print(f"  {project['title']}")
