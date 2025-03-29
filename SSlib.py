import hashlib
import re
from dataclasses import dataclass
from typing import List

@dataclass
class Player:
    def __post_init__(self):
        name_mapping = {"Grawr":"Dobrogost", "Skurvysyn":"Dobrogost"}
        if self.name in name_mapping:
            self.name = name_mapping[self.name]

    def __str__(self):
        return self.name
    name:str
    faction:str
    team:str
@dataclass
class GameMetadata:
    players:List[Player]
    @property
    def all_player_names(self):
        return [p.name for p in self.players]

    played_on_start:int
    played_on_end:int
    mod:str
    map:str
    content_hash = ''
    @staticmethod
    def from_file(path,content):
        return GameMetadata._parse(content)
    @property
    def game_length(self):
        return self.played_on_end-self.played_on_start
    @staticmethod
    def _parse(content):
        res = GameMetadata([],0, 0, '', '')
        res.mod = re.search(r'{mods \"(.*?)\"}', content).group(1)
        players = re.findall(r'{type player}\s+{.*?}\s+{name (.*?)}\s+{team (.*?)}\s+{army (.*?)}', content)
        for player in players:
            name, team, army = player
            res.players.append(Player(name,army,team))
        res.map = re.search(r'{map \"(.*?)\"}', content).group(1)
        res.played_on_start = int(re.search(r'{gameStartTime \"(.*?)\"}', content).group(1), 16)
        res.played_on_end = int(re.search(r'{gameEndTime \"(.*?)\"}', content).group(1), 16)
        hash_object = hashlib.sha256()
        hash_object.update(content.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        res.content_hash = hash_hex
        return res

