import pandas as pd
import numpy as np

def g(x):
  return 1/np.sqrt(1+3*x**2/np.pi**2)

def prob(s1, r1, s2, r2):
  A = g(np.sqrt(r1**2 + r2**2)) * (s1-s2)
  return 1/(1+np.exp(-A))

def main() -> int:
  config = pd.read_json("./config.json")
  year = int(config.season.year)

  df = pd.read_csv(f"./teams_{year}_rankings.csv")
  sched = pd.read_csv(f"./games{year}.csv")
  sched = sched.sort_values('start_date', ascending=True,)
  sched = sched[sched.home_points.isna()]
  sched = sched[(sched.home_level == 'fbs') & (sched.away_level == 'fbs')]
  sched = sched[sched.week == sched.week.min()].reset_index(drop=True)
  sched = sched[['home_team', 'away_team',]]
  sched['home_prob'] = np.nan

  for i in range(len(sched)):
    home,away = sched.loc[i, ['home_team', 'away_team']]
    s1 = df.loc[df.school == home, 'rating'].values[0]
    r1 = df.loc[df.school == home, 'rd'].values[0]
    s2 = df.loc[df.school == away, 'rating'].values[0]
    r2 = df.loc[df.school == away, 'rd'].values[0]
    home_prob = prob(s1, r1, s2, r2)
    sched.loc[i, 'home_prob'] = home_prob

  sched = sched[(sched.home_prob > 0.6) | (sched.home_prob < 0.4)]
  print(sched)

  return 0

if __name__ == '__main__':
  raise SystemExit(main())
