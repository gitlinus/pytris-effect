from ..utils import config
import random

# the real bot logic, called by controller to get the move

class Output:
    def __init__(self, key, type):
        self.key = key
        self.type = type
    

class Bot:

    def __init__(self):
        pass

    def get_move(self, gamestate):
        # for now, we assume planning is instantaneous
        # even though the gamestate is time-based, this should be sufficiently fast to not matter

        raise NotImplementedError()


class RandomBot(Bot):

    def __init__(self):
        super().__init__()

    def get_move(self, gamestate):
        action = random.choice(list(config.key2action.keys())[:-3])
        return [Output(action, gamestate.cls.KEYDOWN), Output(action, gamestate.cls.KEYUP)]


BOTS = {
    "Bot": Bot,
    "RandomBot": RandomBot
}