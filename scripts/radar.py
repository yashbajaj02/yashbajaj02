from pathlib import Path
import json
import math
import os
import urllib.request

USERNAME = "yashbajaj02"
TOKEN = os.getenv("METRICS_TOKEN") or os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError("METRICS_TOKEN or GITHUB_TOKEN is required")

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(
      first: 100
      ownerAffiliations: OWNER
      privacy: PUBLIC
    ) {
      nodes {
        name
        languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node {
              name
            }
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

repositories = data["data"]["user"]["repositories"]["nodes"]

# Aggregate actual language usage across all public repositories.
language_bytes = {}

for repo in repositories:
    for edge in repo["languages"]["edges"]:
        language = edge["node"]["name"]
        size = edge["size"]
        language_bytes[language] = language_bytes.get(language, 0) + size

# Combine related GitHub languages into useful technology categories.
categories = {
    "Python": ["Python"],
    "JavaScript": ["JavaScript"],
    "TypeScript": ["TypeScript"],
    "HTML/CSS": ["HTML", "CSS"],
    "SQL": ["PLpgSQL", "SQL"],
    "Jupyter": ["Jupyter Notebook"],
    "Shell": ["Shell"],
}

category_values = {}

for category, languages in categories.items():
    category_values[category] = sum(
        language_bytes.get(language, 0)
        for language in languages
    )

# Calculate relative scores from actual repository language usage.
non_zero = [v for v in category_values.values() if v > 0]

if not non_zero:
    raise RuntimeError("No GitHub language data found")

max_value = max(non_zero)

skills = []

for category, value in category_values.items():
    if value <= 0:
        continue

    # Scale usage to a 1–10 radar score.
    score = 1 + 9 * math.sqrt(value / max_value)
    score = round(min(10, score), 1)

    skills.append((category, score))

# Always keep a useful radar shape.
skills = skills[:8]

width = 720
height = 520
cx = 360
cy = 270
radius = 180

count = len(skills)
angle_step = 2 * math.pi / count


def point(index, value):
    angle = -math.pi / 2 + index * angle_step
    r = radius * value / 10
    return (
        cx + r * math.cos(angle),
        cy + r * math.sin(angle),
    )


def polygon_points(value):
    return " ".join(
        f"{point(i, value)[0]:.1f},{point(i, value)[1]:.1f}"
        for i in range(count)
    )


svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
width="{width}" height="{height}"
viewBox="0 0 {width} {height}">

<rect width="100%" height="100%" rx="16" fill="#0d1117"/>

<text x="32" y="42"
fill="#f0f6fc"
font-family="Arial"
font-size="22"
font-weight="700">
GitHub Tech Radar
</text>

<text x="32" y="67"
fill="#8b949e"
font-family="Arial"
font-size="13">
Based on actual GitHub repository language usage
</text>
'''

# Radar grid
for level in range(2, 11, 2):
    svg += (
        f'<polygon points="{polygon_points(level)}" '
        f'fill="none" stroke="#30363d" stroke-width="1"/>'
    )

# Axes and labels
for i, (name, value) in enumerate(skills):

    x, y = point(i, 10)

    svg += (
        f'<line x1="{cx}" y1="{cy}" '
        f'x2="{x:.1f}" y2="{y:.1f}" '
        f'stroke="#30363d" stroke-width="1"/>'
    )

    label_x, label_y = point(i, 11.8)

    anchor = "middle"

    if label_x < cx - 30:
        anchor = "end"
    elif label_x > cx + 30:
        anchor = "start"

    svg += (
        f'<text x="{label_x:.1f}" y="{label_y:.1f}" '
        f'text-anchor="{anchor}" '
        f'fill="#f0f6fc" '
        f'font-family="Arial" font-size="13">'
        f'{name}</text>'
    )

# Actual data polygon
skill_points = " ".join(
    f"{point(i, value)[0]:.1f},{point(i, value)[1]:.1f}"
    for i, (_, value) in enumerate(skills)
)

svg += f'''
<polygon
points="{skill_points}"
fill="#238636"
fill-opacity="0.28"
stroke="#39d353"
stroke-width="2"/>
'''

# Data points
for i, (_, value) in enumerate(skills):
    x, y = point(i, value)

    svg += (
        f'<circle cx="{x:.1f}" cy="{y:.1f}" '
        f'r="4" fill="#39d353"/>'
    )

svg += '</svg>'

Path("assets/radar.svg").write_text(svg)

print("Generated assets/radar.svg")
print()
print("Live GitHub language data:")
for name, score in skills:
    print(f"  {name}: {score}/10")
