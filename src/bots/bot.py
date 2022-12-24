import copy
from ..utils import config
from ..utils.logger import logger
import random
import numpy as np

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


default_state_dict = {
    'its_per_sec': 1.0,
    'sec_per_tick': 10,
}

move_map = [
    "rotateCW",
    "rotateCCW",
    "rotate180",
    "shiftLeft",
    "shiftRight",
    "softDrop",
    "hardDrop",
    "swapHold"
]

can_undo = [True, True, True, True, True, True, False, False]

class State:
        
    def __init__(self, board, hold=None, cur=None):
        self.board = board
        self.hold = hold
        self.cur = cur


import cProfile
import io
import pstats
def profile(func):
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = pstats.SortKey.CUMULATIVE # TIME
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return wrapper# Profile foo

class HeuristicBot(Bot):
    # bot with lookahead depth 1

    def __init__(self):
        super().__init__()

    def score(self, state : State):
        m = state.board
        sm = 0
        for j in range(10):
            for i in range(20):
                if m[i+2][j] != 0:
                    if (i+2, j) not in state.cur:
                        sm += (20 - i)**2
                        break

        return -sm
            
    # @profile
    def tree_search(self, gamestate):
        state = gamestate.m
        # tree search over the game matrix instead
        vis_state_space = dict()
        parent_state_space = dict()
        # action_space = list(config.key2action.keys())[:-3] # no zone key, reset, pause
        action_space = move_map
        cand_position = []
        positions = [state]

        mb = state.matrix.tobytes()
        vis_state_space[mb] = False
        
        while positions != []:
            s = positions[0]
            positions = positions[1:]

            # lots of optimization hacks here
            m = s.matrix
            mb = m.tobytes()
            res = s.copy()
            log = dict()
            for idx, action in enumerate(action_space):
                # swapHold must be the first action
                if idx == 7 and mb in parent_state_space:
                    continue
                # hack to reduce computation
                if idx in (5, 6) and mb in parent_state_space and parent_state_space[mb][1][-1] == 5:
                    continue
                # hack: no consecutive spin moves (even though some kicks cannot be replicated otherwise)
                if idx < 3 and mb in parent_state_space and parent_state_space[mb][1][-1] < 3:
                    continue
                # print(action)
                if idx > 0: # need to reset copy since it is different from m
                    if ("moved" not in log) and ("rotated" not in log): # no change
                        pass
                    # elif can_undo[idx-1] and "rotated" in log:
                    #     if s.mino_locations != res.prev_mino_locations:
                    #         print("RIP")
                        # print(s.mino_locations, res.prev_mino_locations)
                        # if res.mino_locations == res.prev_mino_locations:
                        #     print("REEEE")
                        # res = s.copy() # .undo()
                    else: # cannot undo last operation, so have to clone s again
                        res = s.copy()
                
                ops = action
                log = getattr(res, ops)()

                t = (idx == 6)
                if (n := res.matrix.tobytes()) not in vis_state_space:
                    parent_state_space[n] = (m, [idx])
                    vis_state_space[n] = True
                    if t:
                        cand_position.append(State(board=res.matrix, hold=None, cur=res.mino_locations))
                    else:
                        positions.append(res)

        opt = list(sorted(cand_position, key=lambda x: self.score(x)))[-1].board

        # backtrack to construct move sequence
        seq = []

        while (b := opt.tobytes()) in parent_state_space:
            p, s = parent_state_space[b]
            opt = p
            seq.extend(list(reversed(s)))

        actions = list(reversed(seq))
        controls = [Output(list(config.key2action.keys())[k], t) for k in actions for t in [gamestate.cls.KEYDOWN, gamestate.cls.KEYUP]]
        return controls

    def get_move(self, gamestate):
        return self.tree_search(gamestate)



BOTS = {
    "Bot": Bot,
    "RandomBot": RandomBot,
    "HeuristicBot": HeuristicBot
}