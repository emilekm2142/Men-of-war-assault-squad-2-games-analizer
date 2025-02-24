import hashlib
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import List

def get_modified_date(file_path):
    # Get the last modified time
    modified_time = os.path.getmtime(file_path)

    # Convert the timestamp to a readable format
    return modified_time

def calculate_md5(file_path):
    # Create an MD5 hash object
    md5_hash = hashlib.md5()

    # Open the file in binary mode
    with open(file_path, "rb") as file:
        # Read the file in chunks of 4096 bytes
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)

    # Return the hexadecimal MD5 hash
    return md5_hash.hexdigest()
def is_suicide_charger(name:str):
    return "charger" in name.lower()
def is_vehicle(name):
    vehicle_partial_names = ["Mk.",'Puma' 'Jagdpanzer', 'T-',
                             "KV-", "IS-", "Chi-", "Tiger", "PzKpfw", "Ausf",
                             "M5A1", "Ha-", "Chi-", "Ke-", "SdKfz", "Car", "GAZ", "Sd.Kfz"
                             "Sherman", "Archer", "Churchill", "Lee", "Ho-", "Stug",
                             "Stuh", "Universal", "Wasp",
                             ]
    excluded = ["Lee-Enfield", "AT", "tank commander"]
    for partial in vehicle_partial_names:
        if partial in name:
            for partial_negative in excluded:
                if partial_negative in name:
                    return False
            return True
    return False
def is_support(name):
    support_partial_names = ['ammunition', 'crate', "PaK", "ZIS-", "7.5cm", "cm", "Lafette", "mm", "SG-", "Opel", "Isuzu", "Truck"]
    excluded = ["tank commander"]
    for partial in support_partial_names:
        if partial.lower() in name.lower():
            for partial_negative in excluded:
                if partial_negative.lower() in name.lower():
                    return False
            return True
    return False
def is_infantry(name):
    return not is_support(name) and not is_vehicle(name) and  "crew" not in name

@dataclass
class KillLogEntry:
    raw_data:List[str]
    @property
    def killing_player(self):
        return self.raw_data[0]
    @property
    def victim_player(self):
        return self.raw_data[2]
    @property
    def killer(self):
        return self.raw_data[1]
    @property
    def victim(self):
        return self.raw_data[3]
    def is_killer_vehicle(self):
        return is_vehicle(self.raw_data[1])
    def is_killer_infantry(self):
        return is_infantry(self.raw_data[1])
    def is_killer_support(self):
        return is_support(self.raw_data[1])
    def is_victim_vehicle(self):
        return is_vehicle(self.raw_data[3])
    def is_victim_support(self):
        return is_support(self.raw_data[3])
    def is_victim_infantry(self):
        return is_infantry(self.raw_data[3])
    def is_victim_suicide_charger(self):
        return is_suicide_charger(self.raw_data[3])
@dataclass
class GameData:
    kill_log:List[KillLogEntry]
    hash:str
    def vehicle_types_killed_by_player(self, name):
        result = defaultdict(lambda: 0)
        for entry in self.kill_log:
            if entry.killing_player == name and entry.is_victim_vehicle():
                result[entry.victim] += 1
        return result
    def vehicle_types_dead_by_player(self, name):
        result = defaultdict(lambda: 0)
        for entry in self.kill_log:
            if entry.victim_player == name and entry.is_victim_vehicle():
                result[entry.victim] += 1
        return result
    def vehicles_deads_by_players(self):
        result = defaultdict(lambda: 0)
        for entry in self.kill_log:
            if entry.is_victim_vehicle():
                result[entry.victim_player] += 1
        return result
    def who_lost_unit(self, name):
        result = defaultdict(lambda: 0)
        for entry in self.kill_log:
            if entry.victim == name:
                result[entry.victim_player] += 1
        return result
    def what_unit_killed(self, name):
        result = defaultdict(lambda: 0)
        for entry in self.kill_log:
            if entry.killer == name:
                result[entry.victim] += 1
        return result
    def who_killed_unit(self, name):
        result = defaultdict(lambda: 0)
        for entry in self.kill_log:
            if entry.victim == name:
                result[entry.killer] += 1
        return result
    def get_units_deads(self):
        results = defaultdict(lambda: 0)
        for entry in self.kill_log:
            results[entry.victim]+=1
        return results
    def report_for_unit(self,name):
        results = {'vehicles':0, 'support':0, "infantry":0, "other":0, "suicide":0}
        for entry in self.kill_log:
            if entry.killer == name:
                if entry.is_victim_vehicle(): results['vehicles']+=1
                if entry.is_victim_support(): results['support']+=1
                if entry.is_victim_infantry(): results['infantry']+=1
                if entry.is_victim_suicide_charger(): results['suicide']+=1
        return results


    def get_units_report(self):
        results = defaultdict(lambda: {'vehicles':0, 'support':0, "infantry":0, "other":0, "suicide":0})
        for entry in self.kill_log:
                if entry.is_victim_vehicle(): results[entry.killer]['vehicles']+=1
                if entry.is_victim_support(): results[entry.killer]['support']+=1
                if entry.is_victim_infantry(): results[entry.killer]['infantry']+=1
                if entry.is_victim_suicide_charger(): results[entry.killer]['suicide']+=1
        return results
    @staticmethod
    def from_file(zip_path, qm_content):
        all_unit_names_list = set()
        kill_log_extracted = []
        game_data = GameData([], calculate_md5(zip_path) )
        string_content = qm_content
        killlog_lines = re.findall(r'<f(.*?)>(.*?)interface/scene/controlbar/log', string_content)
        killlog_lines = [match[1] for match in killlog_lines if
                    'Flag captured' not in match[1] and 'Flag lost' not in match[1]]

        for log_item_raw in killlog_lines:
            log_item = log_item_raw.replace("e(shadow)", "").replace("<>", "")
            if len(log_item)>300:
                temp = log_item.split("<f(arial_hq")
                log_item = temp[1]
            log_item = re.sub(r">\\.*$", "", log_item) #remove > if its last character

            player1, killer, player2 = re.findall(r'<[a-z]\(.*?\)>(.+?)<[a-z]\(.*?\)>', log_item)
            killer = re.sub(r"<.*>", "", killer).replace("\\","") #usuwa wszystkie <> i content w nich
            all_unit_names_list.add(killer.strip())
            victim_raw = re.match(r'.*>([^>]*)$', log_item).group(1)
            # print(victim_raw)
            victim = re.sub(r"\\.*","", victim_raw)
            if victim=="":
                input()
            kill_log_extracted.append([player1.strip(), killer.strip(), player2.strip(), victim.strip()])
            # if 'Cheron' in log_item:
            #     print(log_item)
            #     print(kill_log_extracted[-1])
        #sanitazing victims
        victims_list = []
        def sanitize_victim_name(name):
            banned_chars = ["@"]
            if name[-1] in banned_chars:
                name = name[0:-1]
            #to jest jakieś dziwne - czasami dodaje na koniec extra char a czasami nie. I jak teraz poznać który jest prawdziwą nazwą?
            if name[-1].isupper() and not name[-2].isupper():
                return name[0:-1]
            if name[0:-1] in all_unit_names_list:
                return name[0:-1]
            return name

        for entry in kill_log_extracted:

            try:
                entry[3] = sanitize_victim_name(entry[3])
                victims_list.append(entry[3])
            except IndexError:
                print("ERROR! NAME TOO SHORT - "+str(entry))
        #second sanitizaion - in case a unit never kill anyone and we only have poluted name
        for entry in kill_log_extracted:
            if entry[3][0:-1] in victims_list:
                entry[3] = entry[3][0:-1]
        game_data.kill_log = [KillLogEntry(entry) for entry in kill_log_extracted]
        return game_data