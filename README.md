# Fantasy football plans

Weekly waiver and lineup plans for the Hill Family League (HFL).

- `index.html` is the current week's plan. Open it in any browser; it needs no internet connection or login.
- `assets/logo.png` is the team logo shown in the page header.
- `2026/week-07.html` and later files are archived copies of past weeks.

## Put it online (GitHub Pages)

One-time setup, with git and the GitHub CLI (`gh auth login` first):

```bash
./setup.sh              # creates a public repo named fantasy-football
./setup.sh my-repo-name # or pick a different name
```

The site goes live at `https://<your-username>.github.io/fantasy-football/` within a minute or two.
If the script can't turn on Pages, go to the repo's **Settings → Pages**, choose
**Deploy from a branch**, pick `main` and `/`, and save.

Without the command line: create a public repo on github.com, upload these files,
and turn on Pages the same way.

The site is public to anyone with the link, and the plan names the team.

## Each week

```bash
./new-week.sh 8 ~/Downloads/new-plan.html
```

This makes the new plan the live page, saves a copy as `2026/week-08.html`, and pushes.
Change `SEASON` at the top of `new-week.sh` next year.

## Scoring tool

`tools/league_points.py` scores players week by week with this league's rules
(half-PPR, 1 point per 20 return yards, the league's IDP and kicker rates) using
public nflverse stats. It needs Python 3 and pandas (`pip install pandas`).

```bash
python3 tools/league_points.py "Pat Freiermuth" "Devin Lloyd" "Evan McPherson"
python3 tools/league_points.py --defense NE MIN
python3 tools/league_points.py "Jaylin Noel" --csv noel.csv
```

It prints games played, points per game, median game, average with the best game
removed, and each week's points. Defense scores are an estimate built from team
stats; they can differ slightly from Yahoo's.
