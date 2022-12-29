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

good_clears = [
    "MINI T-SPIN SINGLE",
    "B2B MINI T-SPIN SINGLE",
    "MINI T-SPIN DOUBLE",
    "B2B MINI T-SPIN DOUBLE",
    "QUADRUPLE",
    "T-SPIN SINGLE",
    "B2B T-SPIN SINGLE",
    "B2B QUADRUPLE",
    "T-SPIN DOUBLE",
    "T-SPIN TRIPLE",
    "B2B T-SPIN DOUBLE",
    "B2B T-SPIN TRIPLE",
    "PERFECT CLEAR",
]

tetromino_orientations = [
    #I
    np.array([[1,1,1,1]],dtype=int),
    np.array([[1],
              [1],
              [1],
              [1]],dtype=int),
    #T
    np.array([[0,1,0],
              [1,1,1]],dtype=int),
    np.array([[1,0],
              [1,1],
              [1,0]],dtype=int),
    np.array([[1,1,1],
              [0,1,0]],dtype=int),
    np.array([[0,1],
              [1,1],
              [0,1]],dtype=int),
    #S
    np.array([[0,1,1],
              [1,1,0]],dtype=int),
    np.array([[1,0],
              [1,1],
              [0,1]],dtype=int),
    #Z
    np.array([[1,1,0],
              [0,1,1]],dtype=int),
    np.array([[0,1],
              [1,1],
              [1,0]],dtype=int),
    #L
    np.array([[0,0,1],
              [1,1,1]],dtype=int),
    np.array([[1,0],
              [1,0],
              [1,1]],dtype=int),
    np.array([[1,1,1],
              [1,0,0]],dtype=int),
    np.array([[1,1],
              [0,1],
              [0,1]],dtype=int),
    #J
    np.array([[1,0,0],
              [1,1,1]],dtype=int),
    np.array([[1,1],
              [1,0],
              [1,0]],dtype=int),
    np.array([[1,1,1],
              [0,0,1]],dtype=int),
    np.array([[0,1],
              [0,1],
              [1,1]],dtype=int),
    #O
    np.array([[1,1],
              [1,1]],dtype=int),
]

# 0 = empty or filled (no weighting), -1 = must be empty (negative score if filled), 1 = must be filled (positive score if filled)
# 2 = extra weight if filled
# right-overhang and left-overhang separately for now

ro_tsd_mask = np.array([
    [ 0,-1,-1, 2, 0],
    [ 1,-1,-1,-1, 1],
    [ 1, 1,-1, 1, 1],
], dtype = int)

lo_tsd_mask = np.array([
    [ 0, 2,-1,-1, 0],
    [ 1,-1,-1,-1, 1],
    [ 1, 1,-1, 1, 1],
], dtype = int)

mask_list = [ro_tsd_mask, lo_tsd_mask]

class State:
        
    def __init__(self, board, hold=None, cur=None, move_score=0, lines_cleared=0, clear_type=[], queue=[]):
        self.board = board
        self.hold = hold
        self.cur = cur
        self.move_score = move_score
        self.lines_cleared = lines_cleared
        self.clear_type = clear_type
        self.queue = queue


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

    def mask_score(self, state : State): # favour filling a mask
        m = state.board
        max_mask_score = 0
        for idx, mask in enumerate(mask_list):
            for j in range(10):
                for i in range(20):
                    cur_mask_score = 0
                    extra_weight = 0
                    if i+2+mask.shape[0]-1 < 22 and j+mask.shape[1]-1 < 10:
                        # "convolution"
                        valid = True
                        for mask_i in range(mask.shape[0]):
                            for mask_j in range(mask.shape[1]):
                                if (i+2+mask_i, j+mask_j) in state.cur:
                                    valid = False
                                    break
                                else:
                                    if(m[i+2+mask_i][j+mask_j] * mask[mask_i][mask_j] < 0):
                                        valid = False
                                        break
                                    elif(m[i+2+mask_i][j+mask_j] * mask[mask_i][mask_j] > 0):
                                        cur_mask_score += 1
                                        if(mask[mask_i][mask_j] == 2 and (m[i+2+mask_i][j+mask_j] != 6 or 'T' in state.queue)): # avoid using T for overhang unless it is in queue
                                            extra_weight += 10
                                    else:
                                        # can the remaining mask be filled such that we do not violate mask requirements
                                        # and none of the minos lie below the mask?
                                        # - above, left, or right of the mask is fine so long as the mino lies within the matrix
                                        if(mask[mask_i][mask_j] > 0):
                                            ans = False
                                            for to in tetromino_orientations:
                                                for to_i in range(to.shape[0]):
                                                    for to_j in range(to.shape[1]):
                                                        # determine if we can fit this tetromino if (mask_i, mask_j) is at (to_i, to_j)
                                                        if(to[to_i][to_j]==0):
                                                            continue
                                                        if(mask_i+(to.shape[0]-1-to_i) <= mask.shape[0]-1 and 0 <= j+mask_j-to_j and j+mask_j+(to.shape[1]-1-to_j) <= 9):
                                                            # to[to_i][to_j] is at (mask_i,mask_j), therefore top-left of to is at (i+2+mask_i-to_i,j+mask_j-to_j)
                                                            possible = True
                                                            for ii in range(to.shape[0]):
                                                                for jj in range(to.shape[1]):
                                                                    if(0 <= mask_i-to_i+ii and mask_i-to_i+ii<=mask.shape[0]-1 and
                                                                       0 <= mask_j-to_j+jj and mask_j-to_j+jj<=mask.shape[1]-1 ):
                                                                       #inside mask
                                                                        if(mask[mask_i-to_i+ii][mask_j-to_j+jj] + to[ii][jj] != mask[mask_i-to_i+ii][mask_j-to_j+jj]):
                                                                            if(mask[mask_i-to_i+ii][mask_j-to_j+jj] < 0):
                                                                                possible = False
                                                                                break
                                                                            elif(mask[mask_i-to_i+ii][mask_j-to_j+jj] > 0):
                                                                                if(m[i+2+mask_i-to_i+ii][j+mask_j-to_j+jj] != 0):
                                                                                    possible = False
                                                                                    break
                                                                    else:
                                                                        #oustside mask
                                                                        if(m[i+2+mask_i-to_i+ii][j+mask_j-to_j+jj] + to[ii][jj] != m[i+2+mask_i-to_i+ii][j+mask_j-to_j+jj]):
                                                                            if(m[i+2+mask_i-to_i+ii][j+mask_j-to_j+jj] != 0):
                                                                                possible = False
                                                                                break
                                                                if not possible:
                                                                    break
                                                            ans = ans or possible
                                                            if ans:
                                                                break
                                                        else:
                                                            continue
                                                    if ans:
                                                        break
                                                if ans:
                                                    break
                                            if not ans:
                                                valid = False
                                                break
                            if not valid:
                                cur_mask_score = 0
                                break
                        if valid and cur_mask_score > 0:
                            # print(f"mask {idx} at {i+2},{j} with current score {cur_mask_score}")
                            mask_match=(mask>0).sum()
                            if(cur_mask_score == mask_match):
                                # extend mask to the left and right
                                for ii in range(mask.shape[0]):
                                    if(j==0):
                                        cur_mask_score += mask[ii][0] if m[i+2+ii][j]==0 and mask[ii][0]>=1 else 2*mask[ii][0]
                                        mask_match += 2*mask[ii][0]
                                    else:
                                        for jj in range(j):
                                            cur_mask_score += mask[ii][0] if m[i+2+ii][jj]==0 and mask[ii][0]>=1 else 2*mask[ii][0]
                                            mask_match += 2*mask[ii][0]
                                    if(j+mask.shape[1]-1==9):
                                        cur_mask_score += mask[ii][mask.shape[1]-1] if m[i+2+ii][j+mask.shape[1]-1]==0 and mask[ii][mask.shape[1]-1]>=1 else 2*mask[ii][mask.shape[1]-1]
                                        mask_match += 2*mask[ii][mask.shape[1]-1]
                                    else:
                                        for jj in range(9 - (j+mask.shape[1]-1)):
                                            cur_mask_score += mask[ii][mask.shape[1]-1] if m[i+2+ii][j+mask.shape[1]-1+jj+1]==0 and mask[ii][mask.shape[1]-1]>=1 else 2*mask[ii][mask.shape[1]-1]
                                            mask_match += 2*mask[ii][mask.shape[1]-1]
                                # extend mask all the way up
                                for jj in range(mask.shape[1]):
                                    if(mask[0][jj] == -1): # if this cell is empty, make sure everything all the way up is empty
                                        for ii in range(20):
                                            if(ii+2 < i+2 and (ii+2,j+jj) not in state.cur):
                                                if(m[ii+2][j+jj] != 0):
                                                    cur_mask_score -= 2
                                # print(f"prefinal score of {cur_mask_score}")
                                # how close are we to full mask match
                                cur_mask_score = int(cur_mask_score**2 * cur_mask_score / mask_match + 1) + extra_weight**2
                            else:
                                if(cur_mask_score > mask_match):
                                    assert False, "WTF"
                                cur_mask_score = cur_mask_score**3
                            # print(f"final score of {cur_mask_score}")
                    max_mask_score = max(max_mask_score,cur_mask_score)
        return max_mask_score

    def jaggedness_score(self, state : State): # favour keeping stack flat and avoid making islands
        m = state.board
        sm = 0
        height_diff = 0
        prev_height = None
        for j in range(10):
            for i in range(20):
                if m[i+2][j] != 0:
                    if (i+2, j) not in state.cur:
                        if(j>0):
                            sm += 1 if m[i+2][j-1] == 0 else 0
                        if(j<9):
                            sm += 1 if m[i+2][j+1] == 0 else 0
                        if(i+2+1 < 22):
                            sm += 10 if m[i+2+1][j] == 0 else 0 # please don't cover holes
        for j in range(10):
            for i in range(20):
                if m[i+2][j] != 0:
                    if (i+2, j) not in state.cur:
                        if not prev_height:
                            prev_height = i+2
                            break
                        else:
                            height_diff += abs(i+2 - prev_height) if abs(i+2 - prev_height) > 1 else 0
                            prev_height = i+2
                            break
        sm += height_diff # penalize creating dependencies
        return -sm**2

    def clear_score(self, state : State): # favour higher clear scores
        if(state.lines_cleared == 0):
            return 0
        elif(any(x in state.clear_type for x in good_clears)):
            return state.move_score**2
        else:
            return -state.lines_cleared*200

    def height_score(self, state : State): # favour staying low
        m = state.board
        sm = 0
        for j in range(10):
            for i in range(20):
                if m[i+2][j] != 0:
                    if (i+2, j) not in state.cur:
                        sm += (20 - i)**2
                        break

        return -sm

    def score(self, state : State):
        return self.jaggedness_score(state) + self.clear_score(state) + self.height_score(state) + self.mask_score(state)
            
    @profile
    def tree_search(self, gamestate):
        state = gamestate.m.copy()
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
            for idx, action in enumerate(action_space):
                # hack to reduce computation
                if idx in (5, 6) and mb in parent_state_space and parent_state_space[mb][1][-1] == 5:
                    continue
                # hack: no consecutive spin moves (even though some kicks cannot be replicated otherwise)
                if idx < 3 and mb in parent_state_space and parent_state_space[mb][1][-1] < 3:
                    continue
                if idx > 0: # need to reset copy since it is different from m
                    res = s.copy()
                if idx == 5: # sdf infinity
                    for _ in range(20):
                        getattr(res, action)()
                else:
                    ops = action
                    getattr(res, ops)()

                t = (idx == 6)
                if (n := res.matrix.tobytes()) not in vis_state_space:
                    if idx == 5:
                        parent_state_space[n] = (m, [idx]*20)
                    else:
                        parent_state_space[n] = (m, [idx])
                    vis_state_space[n] = True
                    if t:
                        # import pdb; pdb.set_trace()
                        cand_position.append(State(board=res.matrix, hold=None, cur=res.mino_locations, move_score=res.prev_move_score, lines_cleared=res.prev_lines_cleared, clear_type=res.prev_clear_text, queue=res.tetrominos.queue[0:5]))
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