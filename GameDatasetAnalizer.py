from collections import defaultdict
from datetime import datetime
from typing import List
from Game import *
import copy

class GameDatasetAnalizer:
    def __init__(self, games:List[Game]):
        self._games = self.__sort_games(copy.deepcopy(games))
        self.games = copy.deepcopy(self._games)
    def set_range(self, min, max):
        self.games = self._games[min:max]
    def set_range_to_last_game_only(self):
        self.games = [self._games[-1]]
    def __sort_games(self, games:List[Game]):
        return sorted(games, key=lambda x: x.metadata.played_on_end)
    @property
    def all_players(self):
        players = set()
        for game in self.games:
            for name in game.metadata.all_player_names:
                players.add(name)
        return players
    def get_playtimes(self):
        return [( datetime.fromtimestamp(game.metadata.played_on_end), game.metadata.game_length) for game in self.games]
    def get_games_count_by_player(self):
        counts = defaultdict(lambda: 0)
        for game in self.games:
            for player in game.metadata.players:
                counts[player.name] += 1
        return counts
    def get_games_count_by_faction(self):
        counts = defaultdict(lambda: 0)
        for game in self.games:
            for player in game.metadata.players:
                counts[player.faction] += 1
        return counts

    def get_kills_of_units(self):
        for game in self.games:
            game.game_data.report_for_unit()

    from collections import defaultdict

    def get_units_report(self):
        combined_report = defaultdict(lambda: {'vehicles': 0, 'support': 0, 'infantry': 0, 'other': 0, 'suicide':0})

        for game in self.games:
            singular_report = game.game_data.get_units_report()

            for key, report in singular_report.items():
                for unit_type, count in report.items():
                    combined_report[key][unit_type] += count

        return combined_report

    def get_raw_log(self):
        log = []
        for game in self.games:
            log += [entry.raw_data for entry in game.game_data.kill_log]
        return log
    def generic_combiner(self, default, x):
        def combined():
            results = defaultdict(lambda: default)
            for game in self.games:
                single = x(game)
                for unit, amount in single.items():
                    results[unit] += amount
            return results
        return combined

    def get_units_deads(self):
        return self.generic_combiner(0, lambda game: game.game_data.get_units_deads())()

    def who_killed_unit(self, name):
        return self.generic_combiner(0, lambda game: game.game_data.who_killed_unit(name))()

    def what_unit_killed(self, name):
        return self.generic_combiner(0, lambda game: game.game_data.what_unit_killed(name))()

    def who_lost_unit(self, name):
        return self.generic_combiner(0, lambda game: game.game_data.who_lost_unit(name))()

    def vehicles_dead_by_players(self):
        return self.generic_combiner(0, lambda game: game.game_data.vehicles_deads_by_players())()

    def generic_sorted(self, collection):
        return sorted(collection.items(), key=lambda item: item[1], reverse=True)
    def vehicle_types_dead_by_player(self,name):
        return self.generic_combiner(0, lambda game: game.game_data.vehicle_types_dead_by_player(name))()
    def vehicle_types_killed_by_player(self,name):
        return self.generic_combiner(0, lambda game: game.game_data.vehicle_types_killed_by_player(name))()
    def print_generic_collection(self, collection, extra_end=None):
        for i, entry in enumerate(collection):
            print(f"{i + 1}. {entry[0]} - {entry[1]} {extra_end(entry) if extra_end is not None else ''}")
    def player_dead_vehicles_per_game_avg(self,name):
        res = self.vehicle_types_dead_by_player(name)
        games_amout = len(self.get_games_with_player(name))
        for key in res:
            res[key] = res[key]/games_amout
        return res
    def player_killed_vehicles_per_game_avg(self,name):
        res = self.vehicle_types_killed_by_player(name)
        games_amout = len(self.get_games_with_player(name))
        for key in res:
            res[key] = res[key]/games_amout
        return res
    def get_games_with_player(self,name):
        return [game for game in self.games if name in [g.name for g in game.metadata.players]]
    def lost_vehicles_per_game(self):
        res = {}
        for player in self.all_players:
            res[player] = sum(self.player_dead_vehicles_per_game_avg(player).values())
        return res
    def killed_vehicles_per_game(self):
        res = {}
        for player in self.all_players:
            res[player] = sum(self.player_killed_vehicles_per_game_avg(player).values())
        return res
    def combine_two_results(self, this, other):
        this2 = copy.deepcopy(this)
        for other_key, other_value in other.items():
            this2[other_key]+=other_value
        return this2
    def players_per_game_report(self):
        res=defaultdict(lambda: 0)
        for game in self.games:
            count = len(game.metadata.players)
            value = {6: "3v3", 4:"2v2", 2:"1v1", 8:"4v4"}[count]
            res[value]+=1
        return res