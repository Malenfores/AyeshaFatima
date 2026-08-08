import json
import os


class ScoreManager:

    FILE_NAME = "highscore.json"

    def __init__(self):

        self.score = 0
        self.combo = 1
        self.chain = 0

        self.high_score = self.load_high_score()

    # =====================================
    # LOAD HIGH SCORE
    # =====================================

    def load_high_score(self):

        if not os.path.exists(self.FILE_NAME):

            with open(self.FILE_NAME, "w") as file:
                json.dump({"high_score": 0}, file, indent=4)

            return 0

        try:

            with open(self.FILE_NAME, "r") as file:

                data = json.load(file)

                return data.get("high_score", 0)

        except:

            return 0

    # =====================================
    # SAVE HIGH SCORE
    # =====================================

    def save_high_score(self):

        try:

            with open(self.FILE_NAME, "w") as file:

                json.dump(

                    {
                        "high_score": self.high_score
                    },

                    file,

                    indent=4

                )

        except:

            pass

    # =====================================
    # UPDATE HIGH SCORE
    # =====================================

    def update_high_score(self):

        if self.score > self.high_score:

            self.high_score = self.score

            self.save_high_score()

    # =====================================
    # ADD SCORE
    # =====================================

    def add_score(self, group_size, multiplier=1.0):

        base_points = group_size * 10

        combo_bonus = (self.combo - 1) * 5

        chain_bonus = self.chain * 10

        total = int(

            (base_points + combo_bonus + chain_bonus)

            * multiplier

        )

        self.score += total

        self.combo += 1

        self.chain += 1

        self.update_high_score()

        return total

    # =====================================
    # BONUS
    # =====================================

    def add_bonus(self, bonus):

        self.score += bonus

        self.update_high_score()

    # =====================================
    # RESET COMBO
    # =====================================

    def reset_combo(self):

        self.combo = 1

        self.chain = 0

    # =====================================
    # RESET GAME
    # =====================================

    def reset_game(self):

        self.update_high_score()

        self.score = 0

        self.combo = 1

        self.chain = 0

    # =====================================
    # GETTERS
    # =====================================

    def get_score(self):

        return self.score

    def get_high_score(self):

        return self.high_score

    def get_combo(self):

        return self.combo

    def get_chain(self):

        return self.chain