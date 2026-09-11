import os
import json
import urllib.request
from pathlib import Path

TOKEN = os.environ.get("METRICS_TOKEN") or os.environ.get("GITHUB_TOKEN")

if not TOKEN:
    raise SystemExit("Missing GitHub token")

query = '''
query {
  user(login: "yashbajaj02") {
    repositories(first: 100, ownerAffiliations: OWNER) {
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node {
              name
              color
            }
          }
        }
      }
    }
  }
}
'''

data = json.dumps({"query": query}).encode()

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=data,
    headers={
        "Authorization": "bearer " + TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "yashbajaj02"
    }
)

with urllib.request.urlopen(req) as response:
    result = json.load(response)

if "errors" in result:
    raise SystemExit(json.dumps(result["errors"], indent=2))

languages = {}

for repo in result["data"]["user"]["repositories"]["nodes"]:
    for edge in repo["languages"]["edges"]:
        name = edge["node"]["name"]
        size = edge["size"]
        color = edge["node"].get("color") or "#888888"

        if name not in languages:
            languages[name] = {"size": 0, "color": color}

        languages[name]["size"] += size

total = sum(x["size"] for x in languages.values())

top = sorted(
    languages.items(),
    key=lambda x: x[1]["size"],
    reverse=True
)[:8]

svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="360">
<rect width="100%" height="100%" rx="14" fill="#0d1117"/>
<text x="32" y="42" fill="#f0f6fc" font-family="Arial" font-size="22" font-weight="700">Most Used Languages</text>
<text x="32" y="67" fill="#8b949e" font-family="Arial" font-size="13">Across my GitHub repositories</text>
'''

y = 105

for name, info in top:
    percentage = info["size"] / total * 100 if total else 0
    bar_width = min(580, max(4, percentage * 5.8))
    color = info["color"]

    svg += f'''
<circle cx="38" cy="{y-5}" r="6" fill="{color}"/>
<text x="54" y="{y}" fill="#f0f6fc" font-family="Arial" font-size="14">{name}</text>
<text x="650" y="{y}" text-anchor="end" fill="#8b949e" font-family="Arial" font-size="13">{percentage:.1f}%</text>
<rect x="54" y="{y+10}" width="580" height="7" rx="3.5" fill="#21262d"/>
<rect x="54" y="{y+10}" width="{bar_width:.1f}" height="7" rx="3.5" fill="{color}"/>
'''
    y += 34

svg += "</svg>"

Path("assets/languages-custom.svg").write_text(svg)

print("Generated assets/languages-custom.svg")
