from pathlib import Path
import math

skills = [
    ("Python", 8),
    ("JavaScript", 8),
    ("TypeScript", 7),
    ("React", 7),
    ("HTML/CSS", 8),
    ("AI/ML", 6),
    ("Supabase/SQL", 7),
    ("Git/GitHub", 8),
]

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
    return cx + r * math.cos(angle), cy + r * math.sin(angle)

def polygon_points(value):
    return " ".join(
        f"{point(i, value)[0]:.1f},{point(i, value)[1]:.1f}"
        for i in range(count)
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" rx="16" fill="#0d1117"/>

<text x="32" y="42" fill="#f0f6fc" font-family="Arial" font-size="22" font-weight="700">Tech Stack Radar</text>
<text x="32" y="67" fill="#8b949e" font-family="Arial" font-size="13">Self-rated skill levels · 10 point scale</text>
'''

# Radar grid
for level in range(2, 11, 2):
    svg += f'<polygon points="{polygon_points(level)}" fill="none" stroke="#30363d" stroke-width="1"/>'

# Axes and labels
for i, (name, value) in enumerate(skills):
    x, y = point(i, 10)

    svg += f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#30363d" stroke-width="1"/>'

    label_x, label_y = point(i, 11.8)

    anchor = "middle"
    if label_x < cx - 30:
        anchor = "end"
    elif label_x > cx + 30:
        anchor = "start"

    svg += f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="{anchor}" fill="#f0f6fc" font-family="Arial" font-size="13">{name}</text>'

# Skill area
skill_points = " ".join(
    f"{point(i, value)[0]:.1f},{point(i, value)[1]:.1f}"
    for i, (_, value) in enumerate(skills)
)

svg += f'''
<polygon points="{skill_points}" fill="#238636" fill-opacity="0.28" stroke="#39d353" stroke-width="2"/>
'''

for i, (_, value) in enumerate(skills):
    x, y = point(i, value)
    svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#39d353"/>'

svg += '</svg>'

Path("assets/radar.svg").write_text(svg)
print("Generated assets/radar.svg")
