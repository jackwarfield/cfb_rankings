"""
Game data from https://collegefootballdata.com
"""

import random
import subprocess as sp
from datetime import datetime
from datetime import timezone

import numpy as np
import pandas as pd

today = datetime.now(timezone.utc).strftime('%Y-%m-%d') + 'T00:00:00.000Z'
todayprint = datetime.now()
todayprint = todayprint.strftime('%m/%d/%Y %H:%M:%S')

config = pd.read_json('./config.json')
targyear = int(config.season.year)
print(f'season: {targyear}')

sched = pd.read_csv(f'games{targyear}.csv')
max_week = sched.week.max()
max_week = 16
sched = sched[
    (sched.home_points.notna()) & (sched.home_points != sched.away_points)
]
run_week = sched.week.max()
print(f'Week {run_week}')

df = pd.read_csv('teams.csv')
df['rating'] = df['rating'].astype(float)

sched = pd.read_csv(f'games{targyear-2}.csv')
sched = sched[
    (sched.home_points.notna()) & (sched.home_points != sched.away_points)
]
sched = sched.sort_values('start_date', ascending=True)
sched = sched.reset_index(drop=True)
s_ind = list(sched.index)
sched1 = sched.copy()
for i in range(max_week - run_week - 1):
    sched = pd.concat([sched, sched1]).reset_index(drop=True)
sched.to_csv('./sched1.csv', index=False)

sched = pd.read_csv(f'games{targyear-1}.csv')
sched = sched[
    (sched.home_points.notna()) & (sched.home_points != sched.away_points)
]
sched = sched.sort_values('start_date', ascending=True)
sched = sched.reset_index(drop=True)
sched2 = pd.read_csv(f'games{targyear}.csv')
sched2 = sched2[
    (sched2.home_points.notna()) & (sched2.home_points != sched2.away_points)
]
sched2 = sched2.sort_values('start_date', ascending=True).reset_index(
    drop=True
)
sched = (
    pd.concat([sched, sched2])
    .reset_index(drop=True)
    .sort_values(by='start_date')
    .reset_index(drop=True)
)
sched1 = sched.copy()
for i in range(21 + 10 * (max_week - run_week) - 1):
    sched = pd.concat([sched, sched1]).reset_index(drop=True)
sched.to_csv('./sched2.csv', index=False)

sched = pd.read_csv(f'games{targyear}.csv')
sched = sched[(sched.season == targyear)]
sched = sched[
    (sched.home_points.notna()) & (sched.home_points != sched.away_points)
]
sched = sched.sort_values('start_date', ascending=True)
sched = sched.reset_index(drop=True)
sched.to_csv(f'games{targyear}.csv', index=False)
sched1 = sched.copy()
for i in range(31 + 10 * run_week - 1):
    sched = pd.concat([sched, sched1]).reset_index(drop=True)
sched.to_csv('./sched3.csv', index=False)

sp.run('./cfb', shell=True)

df = pd.read_csv('./teams_2024_rankings.csv')
df = df[df.conference.notna()].reset_index(drop=True)
df['wins'] = (df['wins'] / (31 + 10 * run_week - 1)).astype(int)
df['losses'] = (df['losses'] / (31 + 10 * run_week - 1)).astype(int)

ranks = (
    df.sort_values('rating', ascending=False)
    .reset_index(drop=True)[
        ['school', 'conference', 'rating', 'wins', 'losses', 'rd']
    ]
    .values
)

print(
    '| {:<5} | {:<20} | {:<20} | {:<8} | {:<6} | {:<9} |'.format(
        'Rank', 'Team', 'Conference', 'Record', 'Rating', 'Deviation'
    )
)
print(
    '| {:<5} | {:<20} | {:<20} | {:<8} | {:<6} | {:<9} |'.format(
        '---:', '---:', '---:', '---:', '---:', '---:'
    )
)
for i in range(1, 25 + 1):
    t, c, r, w, l, rd = ranks[i - 1]
    rec = str(int(w)) + '-' + str(int(l))
    print(
        '| {:<5} | {:<20} | {:<20} | {:<8} | {:<6} | {:<9} |'.format(
            i, t, c, rec, int(r), int(rd)
        )
    )

with open('./README.md', 'w') as f:
    print(
        '| {:<5} | {:<20} | {:<20} | {:<8} | {:<6} | {:<9} |'.format(
            'Rank', 'Team', 'Conference', 'Record', 'Rating', 'Deviation'
        ),
        file=f,
    )
    print(
        '| {:<5} | {:<20} | {:<20} | {:<8} | {:<6} | {:<9} |'.format(
            '---:', '---:', '---:', '---:', '---:', '---:'
        ),
        file=f,
    )
    for i in range(1, 25 + 1):
        t, c, r, w, l, rd = ranks[i - 1]
        rec = str(int(w)) + '-' + str(int(l))
        print(
            '| {:<5} | {:<20} | {:<20} | {:<8} | {:<6} | {:<9} |'.format(
                i, t, c, rec, int(r), int(rd)
            ),
            file=f,
        )

    print('', file=f)
    print(f'Updated {todayprint}', file=f)


df.to_csv('teams_2024_rankings.csv', index=False)

sp.run('rm -f sched1.csv sched2.csv sched3.csv', shell=True)
