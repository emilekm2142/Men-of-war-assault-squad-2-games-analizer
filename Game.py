from QMLib import GameData
from ReplayZipReader import get_replay_content
from SSlib import GameMetadata


class Game:
    def __init__(self, path):
        qm,ss = get_replay_content(path)
        self.path=path
        self.game_data:GameData = GameData.from_file(path, qm)
        self.metadata:GameMetadata = GameMetadata.from_file(path, ss)
