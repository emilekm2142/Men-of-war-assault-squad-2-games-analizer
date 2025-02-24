import sys

from Game import Game
from QMLib import *
from SSlib import *
from ReplayZipReader import get_replay_content, get_all_replays_paths
from GameDatasetAnalizer import GameDatasetAnalizer


# cheron_game = Game("replays/replay5_SS.zip")
#
# # input()
# sys.exit(0)
MOD = "w3bst3rs"
replays = get_all_replays_paths()
print(replays)
games = []
def does_game_exist_in_the_db(games,game):
    if not any(existing.metadata.content_hash == game.metadata.content_hash for existing in games):
        if not any(existing.metadata.played_on_start == game.metadata.played_on_start for existing in games) and not any(existing.metadata.played_on_end == game.metadata.played_on_end for existing in games):
            return False
    return True
for replay_path in replays:
    g = Game(replay_path)
    if MOD not in g.metadata.mod:
        continue
    if not does_game_exist_in_the_db(games, g):
        games.append(g)
    else:
        print(f"{replay_path} already read. Ignoring duplicate file...")

analizer = GameDatasetAnalizer(games)
#analizer.set_range_to_last_game_only()


print(analizer.get_playtimes())
print(analizer.get_games_count_by_player())
print(analizer.get_games_count_by_faction())
report = analizer.get_units_report()
deads_report = analizer.get_units_deads()
sorted_report_vehicles = sorted(report.items(), key=lambda item: item[1]['vehicles'], reverse=True)
sorted_report_infantry = sorted(report.items(), key=lambda item: item[1]['infantry'], reverse=True)
sorted_deads = sorted(deads_report.items(), key=lambda item: item[1], reverse=True)

for i,entry in enumerate(sorted_report_vehicles):
    print(f"{i}. {entry[0]} - {entry[1]['vehicles']}")
print("-------INFANTRY KILLS------------")
j=0
for i,entry in enumerate(sorted_report_infantry):
    if is_infantry(entry[0]): continue
    j+=1
    print(f"{j}. {entry[0]} - {entry[1]['infantry']} ({entry[1]['suicide']} suicide chargers)")

print("-------DEADS---------")
for i,entry in enumerate(sorted_deads):
    print(f"{i+1}. {entry[0]} - {entry[1]}")

print("-------DEADS VEHICLES---------")
j=0
for i,entry in enumerate(sorted_deads):
    if not is_vehicle(entry[0]): continue
    j+=1
    print(f"{j}. {entry[0]} - {entry[1]}")



print("---CO ZABIJAŁO SUICIDE---")
what_killed_suicide = analizer.generic_sorted(analizer.who_killed_unit("Suicide charger"))
analizer.print_generic_collection(what_killed_suicide)

print("---CO ZABIJAŁO ASSAULT SMG---")
what_killed_assault = analizer.generic_sorted(analizer.who_killed_unit("assault SMG infantry"))
analizer.print_generic_collection(what_killed_assault)

print("----MG42 LAFETTE - KILLS ---")
mg42_kills = analizer.generic_sorted(analizer.what_unit_killed("MG42 Lafette"))
analizer.print_generic_collection(mg42_kills)

print("----SMG-100 & SMG-100-44 - KILLS---")
assault_kills = analizer.generic_sorted(analizer.combine_two_results(analizer.what_unit_killed("Type 100 SMG"), analizer.what_unit_killed("Type 100-44 SMG")))
analizer.print_generic_collection(assault_kills)

print("----SUICIDE PISTOLS - KILLS---")
pistol_kills = analizer.generic_sorted(analizer.what_unit_killed("Type 14 Nambu"))
analizer.print_generic_collection(pistol_kills)

suicide_deads_by_players = analizer.generic_sorted(analizer.who_lost_unit("Suicide charger"))
print("--KTO STRACIŁ NAJWIĘCEJ SUICIDE--")
analizer.print_generic_collection(suicide_deads_by_players)

tank_crew_deads_by_players = analizer.generic_sorted(analizer.who_lost_unit("tank crew"))
print("--KTO STRACIŁ NAJWIĘCEJ TANK CREW--")
analizer.print_generic_collection(tank_crew_deads_by_players)

vehicles_deads_count = analizer.generic_sorted(analizer.vehicles_dead_by_players())
print("--KTO STRACIŁ NAJWIĘCEJ POJAZDÓW--")
analizer.print_generic_collection(vehicles_deads_count)

print("--Jakie pojazdy tracił CHERON--")
vehicles_emile = analizer.generic_sorted(analizer.vehicle_types_dead_by_player("Cheron"))
analizer.print_generic_collection(vehicles_emile)


print("---Games with Cheron---")
print(analizer.get_games_with_player("Cheron")[0].path)

print("----Martwe pojazdy na grę na gracza----")
analizer.print_generic_collection(analizer.generic_sorted(analizer.lost_vehicles_per_game()))

print("----Zabite pojazdy na grę na gracza----")
analizer.print_generic_collection(analizer.generic_sorted(analizer.killed_vehicles_per_game()))

print("----Liczba gier---")
analizer.print_generic_collection(analizer.generic_sorted(analizer.players_per_game_report()))

print("---Długość gier---")
playtimes = [int(t[1]/60) for t in analizer.get_playtimes()]
print(f"Avg. :{sum(playtimes)/len(playtimes)}")
for playtime in playtimes:
    print(int(playtime))

for entry in analizer.get_raw_log():
    if entry[2] == "Cheron" and (is_vehicle(entry[3])):
        print(entry)


print("---Co zrobilo hago?---")
hago_kills = analizer.generic_sorted(analizer.what_unit_killed("Ha-Go"))
analizer.print_generic_collection(hago_kills)
