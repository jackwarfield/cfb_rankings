import os.path

import cfbd
import numpy as np
import pandas as pd
from cfbd.rest import ApiException


def build_teams_table(
    ApiClient: cfbd.api_client.ApiClient,
    year: int,
) -> pd.DataFrame:
    teams_instance = cfbd.TeamsApi(ApiClient)
    try:
        teams_res = teams_instance.get_fbs_teams(
            year=year,
        )
    except ApiException as e:
        print('Exception when calling TeamsApi->get_teams: %s\n' % e)
        raise SystemExit(1)

    res_len = []
    school = []
    school_id = []
    div = []
    level = []
    conference = []
    rating = []
    rd = np.full(res_len, 600.0)
    volatility = np.full(res_len, 0.06)
    for i, row in enumerate(teams_res):
        school += [row.school]
        school_id += [row.id]
        div += [row.division]
        # level += [row.classification]
        level += ['fbs']
        conference += [row.conference]
        rating += [1500]
        # if row.classification == 'fbs':
        #    rating += [1500]
        # elif row.classification == 'fcs':
        #    rating += [700]
        # else:
        #    rating += [200]
    data = {
        'school': school,
        'id': school_id,
        'conference': conference,
        'division': div,
        'level': level,
        'rating': rating,
        'rd': rd,
        'volatility': volatility,
    }
    teams = pd.DataFrame(data=data)
    teams.to_csv(
        './teams.csv',
        index=False,
    )
    return teams


def build_games_table(
    ApiClient: cfbd.api_client.ApiClient,
    year: int,
) -> pd.DataFrame:
    games_instance = cfbd.GamesApi(ApiClient)
    try:
        games_res = games_instance.get_games(
            year,
            season_type='regular',
        )
    except ApiException as e:
        print('Exception when calling GamesApi->get_games: %s\n' % e)
        raise SystemExit(1)
    try:
        games_res += games_instance.get_games(
            year,
            season_type='postseason',
        )
    except ApiException as e:
        print('Exception when calling GamesApi->get_games: %s\n' % e)
        raise SystemExit(1)

    id = []
    season = []
    week = []
    season_type = []
    start_date = []
    neutral_site = []
    conference_game = []
    home_id = []
    home_team = []
    home_points = []
    away_id = []
    away_team = []
    away_points = []
    home_level = []
    away_level = []
    for i, row in enumerate(games_res):
        id += [row.id]
        season += [row.season]
        week += [row.week]
        season_type += [row.season_type]
        start_date += [row.start_date]
        neutral_site += [row.neutral_site]
        conference_game += [row.conference_game]
        home_id += [row.home_id]
        home_team += [row.home_team]
        home_points += [row.home_points]
        away_id += [row.away_id]
        away_team += [row.away_team]
        away_points += [row.away_points]
        home_level += [row.home_division]
        away_level += [row.away_division]

    data = {
        'id': id,
        'season': season,
        'week': week,
        'season_type': season_type,
        'start_date': start_date,
        'neutral_site': neutral_site,
        'conference_game': conference_game,
        'home_id': home_id,
        'home_team': home_team,
        'home_points': home_points,
        'away_id': away_id,
        'away_team': away_team,
        'away_points': away_points,
        'home_level': home_level,
        'away_level': away_level,
    }
    games = pd.DataFrame(data=data)

    games = games[
        (games.home_points.notna()) & (games.home_points != games.away_points)
    ]
    games = games.sort_values('start_date', ascending=True)
    games = games.reset_index(drop=True)

    games.to_csv(
        f'./games{year}.csv',
        index=False,
    )
    return games


def main():
    config = pd.read_json('config.json')
    configuration = cfbd.Configuration()
    configuration.api_key['Authorization'] = config.api.key
    configuration.api_key_prefix['Authorization'] = 'Bearer'
    year = int(config.season.year)

    build_teams_table(
        ApiClient=cfbd.ApiClient(configuration),
        year=year,
    )

    # if not os.path.exists(f"./games{year-2}.csv"):
    build_games_table(ApiClient=cfbd.ApiClient(configuration), year=year - 2)
    # if not os.path.exists(f"./games{year-1}.csv"):
    build_games_table(ApiClient=cfbd.ApiClient(configuration), year=year - 1)
    build_games_table(ApiClient=cfbd.ApiClient(configuration), year=year)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
