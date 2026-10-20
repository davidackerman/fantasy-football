#!/usr/bin/env python3
"""Score NFL players week by week with the Hill Family League's rules.

Pulls public weekly stats from nflverse (github.com/nflverse/nflverse-data),
so it needs no login. Requires pandas:  pip install pandas

Examples:
  python tools/league_points.py "Pat Freiermuth" "Devin Lloyd" "Evan McPherson"
  python tools/league_points.py --defense NE MIN
  python tools/league_points.py --season 2026 "Jaylin Noel" --csv noel.csv
"""
import argparse, sys
import numpy as np, pandas as pd

BASE = "https://github.com/nflverse/nflverse-data/releases/download"

def offense_idp(r):
    ret = r.punt_return_yards + r.kickoff_return_yards
    off = (r.passing_yards / 25 + 4 * r.passing_tds - r.passing_interceptions
           + r.rushing_yards / 10 + 6 * r.rushing_tds
           + 0.5 * r.receptions + r.receiving_yards / 10 + 6 * r.receiving_tds
           + ret / 20 + 6 * r.special_teams_tds
           + 2 * (r.passing_2pt_conversions + r.rushing_2pt_conversions + r.receiving_2pt_conversions)
           - 2 * (r.rushing_fumbles_lost + r.receiving_fumbles_lost + r.sack_fumbles_lost)
           + 6 * r.fumble_recovery_tds)
    idp = (r.def_tackles_solo + 0.5 * r.def_tackle_assists + 2.5 * r.def_sacks
           + 3 * r.def_interceptions + 3 * r.def_fumbles_forced + 3 * r.fumble_recovery_opp
           + 6 * r.def_tds + 4 * r.def_safeties + r.def_pass_defended + r.def_tackles_for_loss
           + 4 * (r.def_punt_blocks + r.def_pat_blocks + r.def_fg_blocks)
           + (r.def_interception_yards + r.fumble_recovery_yards_opp) / 20)
    return off + idp

def kicker(r):
    return (3 * (r.fg_made_0_19 + r.fg_made_20_29 + r.fg_made_30_39) + 4 * r.fg_made_40_49
            + 5 * (r.fg_made_50_59 + r.fg_made_60_)
            - (r.fg_missed_0_19 + r.fg_missed_20_29 + r.fg_missed_30_39)
            + r.pat_made - r.pat_missed)

def pa_tier(pa):
    return 10 if pa == 0 else 7 if pa <= 6 else 4 if pa <= 13 else 1 if pa <= 20 else 0 if pa <= 27 else -1 if pa <= 34 else -4

def summarize(label, weeks, pts):
    p = np.array(pts, dtype=float)
    exbest = (p.sum() - p.max()) / (len(p) - 1) if len(p) > 1 else float("nan")
    line = " ".join(f"W{w}:{v:.1f}" for w, v in zip(weeks, p))
    print(f"{label:<26} GP {len(p):>2}  PPG {p.mean():5.1f}  median {np.median(p):5.1f}  excl. best {exbest:5.1f}   {line}")
    return [{"name": label, "week": int(w), "points": round(float(v), 2)} for w, v in zip(weeks, p)]

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("players", nargs="*", help="player display names, e.g. \"Pat Freiermuth\"")
    ap.add_argument("--defense", nargs="*", default=[], help="team abbreviations for team defenses, e.g. NE MIN (an estimate)")
    ap.add_argument("--season", type=int, default=2026)
    ap.add_argument("--csv", help="also write week-by-week points to this CSV file")
    a = ap.parse_args()
    if not a.players and not a.defense:
        ap.print_help(); sys.exit(1)
    rows = []
    if a.players:
        d = pd.read_csv(f"{BASE}/stats_player/stats_player_week_{a.season}.csv", low_memory=False).fillna(0)
        d = d[d.season_type == "REG"].copy()
        for n in a.players:
            x = d[d.player_display_name.str.lower() == n.lower()].sort_values("week")
            if x.empty:
                hits = d[d.player_display_name.str.contains(n.split()[-1], case=False, na=False)].player_display_name.unique()[:5]
                print(f"{n}: not found. Close matches: {', '.join(hits) or 'none'}"); continue
            f = kicker if (x.position == "K").all() else offense_idp
            rows += summarize(n, x.week, x.apply(f, axis=1))
    if a.defense:
        t = pd.read_csv(f"{BASE}/stats_team/stats_team_week_{a.season}.csv", low_memory=False).fillna(0)
        t = t[t.season_type == "REG"].copy()
        t["offpts"] = (6 * (t.passing_tds + t.rushing_tds) + 3 * t.fg_made + t.pat_made
                       + 2 * (t.passing_2pt_conversions + t.rushing_2pt_conversions + t.receiving_2pt_conversions))
        opp = t[["week", "team", "offpts"]].rename(columns={"team": "opponent_team", "offpts": "pa"})
        t = t.merge(opp, on=["week", "opponent_team"], how="left")
        for tm in a.defense:
            x = t[t.team == tm.upper()].sort_values("week")
            if x.empty:
                print(f"{tm}: no team found"); continue
            pts = (x.def_sacks + 2 * x.def_interceptions + 2 * x.fumble_recovery_opp
                   + 6 * (x.def_tds + x.special_teams_tds + x.fumble_recovery_tds) + 4 * x.def_safeties
                   + 2 * (x.def_punt_blocks + x.def_fg_blocks + x.def_pat_blocks) + x.pa.apply(pa_tier))
            rows += summarize(f"{tm.upper()} DEF (estimate)", x.week, pts)
    if a.csv and rows:
        pd.DataFrame(rows).to_csv(a.csv, index=False); print(f"Wrote {a.csv}")

if __name__ == "__main__":
    main()
