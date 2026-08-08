import json
import os


class PlayerManager:

    def __init__(self):

        self.file = "players.json"

        if not os.path.exists(self.file):

            with open(self.file, "w") as f:
                json.dump({}, f, indent=4)

        self.load()


    def load(self):

        with open(self.file, "r") as f:
            self.players = json.load(f)


    def save(self):

        with open(self.file, "w") as f:
            json.dump(self.players, f, indent=4)


    def get_player(self, name):

        if name not in self.players:

            self.players[name] = {

                "high_score": 0,
                "games_played": 0,
                "games_won": 0,
                "games_lost": 0

            }

            self.save()

        return self.players[name]


    def update(self, name, score, win):

        player = self.get_player(name)

        player["games_played"] += 1

        if win:
            player["games_won"] += 1
        else:
            player["games_lost"] += 1

        if score > player["high_score"]:
            player["high_score"] = score

        self.save()