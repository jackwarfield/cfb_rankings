#include <rapidcsv.h>

#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "glicko2.h"

int find_index(std::vector<std::string> schools, std::string school);
void loop_schedule(std::string sched_fn, std::string teams_fnin,
                   std::string teams_fnout, int n_loops, bool reset_rd);

int main(int argc, char *argv[]) {
  // int max_week = 15;
  // int week = 7;

  // loop_schedule("sched1.csv", "teams.csv", "teams_2023_rankings.csv",
  //               max_week - week, true);
  // loop_schedule("sched2.csv", "teams_2023_rankings.csv",
  //               "teams_2023_rankings.csv", 21 + 10 * (max_week - week),
  //               true);
  // loop_schedule("sched3.csv", "teams_2023_rankings.csv",
  //               "teams_2023_rankings.csv", 31 + 10 * week, false);

  loop_schedule("sched1.csv", "teams.csv", "teams_2024_rankings.csv", 1, true);
  loop_schedule("sched2.csv", "teams_2024_rankings.csv",
                "teams_2024_rankings.csv", 1, true);
  loop_schedule("sched3.csv", "teams_2024_rankings.csv",
                "teams_2024_rankings.csv", 1, false);

  return 0;
}

int find_index(std::vector<std::string> schools, std::string school) {
  for (int i = 0; i < schools.size(); i++) {
    if (schools[i] == school) {
      return i;
    }
  }
  return -9999;
}

void loop_schedule(std::string sched_fn, std::string teams_fnin,
                   std::string teams_fnout, int n_loops, bool reset_rd) {
  // run loop through the schedule
  rapidcsv::Document teams(teams_fnin);
  std::vector<std::string> schools = teams.GetColumn<std::string>("school");
  std::vector<double> ratings = teams.GetColumn<double>("rating");
  std::vector<double> ids = teams.GetColumn<double>("id");
  std::vector<std::string> conferences =
      teams.GetColumn<std::string>("conference");
  std::vector<std::string> divisions = teams.GetColumn<std::string>("division");
  std::vector<std::string> levels = teams.GetColumn<std::string>("level");
  std::vector<double> rds = teams.GetColumn<double>("rd");
  std::vector<double> vols = teams.GetColumn<double>("volatility");
  std::vector<int> wins(schools.size(), 0);
  std::vector<int> losses(schools.size(), 0);
  if (reset_rd) {
    for (int i = 0; i < rds.size(); i++) {
      rds[i] = 600.0;
    }
  }

  rapidcsv::Document sched(sched_fn);
  std::vector<std::string> home_teams =
      sched.GetColumn<std::string>("home_team");
  std::vector<std::string> away_teams =
      sched.GetColumn<std::string>("away_team");
  std::vector<int> home_id = sched.GetColumn<int>("home_id");
  std::vector<int> away_id = sched.GetColumn<int>("away_id");
  std::vector<double> home_points = sched.GetColumn<double>("home_points");
  std::vector<double> away_points = sched.GetColumn<double>("away_points");
  std::vector<std::string> home_level =
      sched.GetColumn<std::string>("home_level");
  std::vector<std::string> away_level =
      sched.GetColumn<std::string>("away_level");

  std::string ht, at;
  int h_ind, a_ind;
  bool t1win;
  double r1, rd1, sig1, r2, rd2, sig2;
  std::vector<double> results(6, 0.0);
  for (int _ = 0; _ < n_loops; _++) {
    for (int j = 0; j < wins.size(); j++) {
      wins[j] = 0;
      losses[j] = 0;
    }
    for (int i = 0; i < home_teams.size(); i++) {
      ht = home_teams[i];
      at = away_teams[i];

      h_ind = find_index(schools, ht);
      if (h_ind < 0) {
        std::string level = home_level[i];
        double rating = 200.0;
        if (level == "fcs") {
          double rating = 700.0;
        }
        schools.push_back(ht);
        ratings.push_back(rating);
        ids.push_back(home_id[i]);
        conferences.push_back("");
        divisions.push_back("");
        levels.push_back(level);
        rds.push_back(600.0);
        vols.push_back(0.06);
        wins.push_back(0);
        losses.push_back(0);
        h_ind = schools.size() - 1;
      }

      a_ind = find_index(schools, at);
      if (a_ind < 0) {
        std::string level = away_level[i];
        double rating = 200.0;
        if (level == "fcs") {
          rating = 700.0;
        }
        schools.push_back(at);
        ratings.push_back(rating);
        ids.push_back(away_id[i]);
        conferences.push_back("");
        divisions.push_back("");
        levels.push_back(level);
        rds.push_back(600.0);
        vols.push_back(0.06);
        wins.push_back(0);
        losses.push_back(0);
        a_ind = schools.size() - 1;
      }

      if (home_points[i] > away_points[i]) {
        t1win = true;
        wins[h_ind] = wins[h_ind] + 1;
        losses[a_ind] = losses[a_ind] + 1;
      } else {
        t1win = false;
        losses[h_ind] = losses[h_ind] + 1;
        wins[a_ind] = wins[a_ind] + 1;
      }

      r1 = ratings[h_ind];
      rd1 = rds[h_ind];
      sig1 = vols[h_ind];
      r2 = ratings[a_ind];
      rd2 = rds[a_ind];
      sig2 = vols[a_ind];

      results = glicko2::update_ratings(r1, rd1, sig1, r2, rd2, sig2, t1win);

      ratings[h_ind] = results[0];
      rds[h_ind] = results[1];
      vols[h_ind] = results[2];
      ratings[a_ind] = results[3];
      rds[a_ind] = results[4];
      vols[a_ind] = results[5];
    }
  }

  std::ofstream outcsv;
  outcsv.open(teams_fnout);
  outcsv << "school,id,conference,division,level,rating,rd,volatility,wins,"
            "losses\n";
  for (int i = 0; i < schools.size(); i++) {
    outcsv << schools[i] << "," << ids[i] << "," << conferences[i] << ","
           << divisions[i] << "," << levels[i] << "," << ratings[i] << ","
           << rds[i] << "," << vols[i] << "," << wins[i] << "," << losses[i]
           << "\n";
  }
  outcsv.close();
}
