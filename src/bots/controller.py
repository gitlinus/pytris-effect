from . import bot as tetris_bots
import threading
import time

# goal is to separate interface from logic
class BotController:

    """
    Args:
        bot: type of bot used for generating moves
        gamestate: GameState object to bind to
        pps: the fixed pps the bot plays at
    """
    def __init__(self, bot="Bot", gamestate=None, pps=0.5):
        assert(bot in tetris_bots.BOTS)
        self.bot = tetris_bots.BOTS[bot]()
        self.gamestate = gamestate
        self.pps = pps
        self.done = False

        self.queue = []
        self.lock = threading.Lock()

    def bind(self, gamestate):
        # bind to gamestate and reset internal state
        self.gamestate = gamestate
        self.done = False

    def move(self):
        # places a piece
        while not self.done:
            try:
                moves = self.bot.get_move(self.gamestate)
                with self.lock:
                    self.queue.extend(moves)
            except:
                self.done = True

            time.sleep(1.0 / self.pps)

    def start(self):
        threading.Timer(1.0 / self.pps, self.move).start()

    def end(self):
        self.done = True

if __name__ == '__main__':
    ctrl = BotController(pps=3.0)
    ctrl.start()

    def kill_test():
        ctrl.end()

    threading.Timer(10.0, kill_test).start()
