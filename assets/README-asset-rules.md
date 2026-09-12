# README asset behavior

- `project-1.svg` through `project-6.svg` are visual card assets. The clickable links are in `README.md`, not inside the images.
- `scripts/cards.py` reads public GitHub repository data and refreshes the six project cards and their README links.
- `.github/workflows/cards.yml` runs the generator daily and when the generator/workflow changes.
- `learning-3d.svg` and `whoami-3d.svg` are intentionally static visual assets. They are not links and do not claim to be live data.
- The LeetCode card in `README.md` is an external dynamic card and is wrapped in a real link to the user's LeetCode profile.
