import copy
from collections import defaultdict
from ChessBoard import Chessgame
from Player_Base import *
from ChessPieces import *
from multiprocessing import Queue,Pool
from queue import Queue


class vars:
    player = 'White'
    depth = 3

def child_process(node,player=vars.player):
    abspawn = AlphaBeta(player)
    return abspawn.call_multiprocess(node,maxing=False)


class ChessNode(Chessgame):

    def __init__(self,depth,board,value=None,parent=None):
        self.parent = parent
        self.depth = depth
        self.value = value
        self.board = board
        self.index = 0
        self.children = None
        #self.get_current_state(board)

    def __ge__(self, other):
        return self.value >= other
    def __le__(self, other):
        return self.value <= other
    def __lt__(self, other):
        return self.value < other
    def __gt__(self, other):
        return self.value > other

    def __call__(self):
        return self.board
    def __iter__(self):
        return next(self)
    def items(self):
         return self.board.items()
    def __getitem__(self, key):
        return self.board[key]
    def __setitem__(self, key, value):
        self.board[key] = value

    def __next__(self):
        subs = (value for _, value in self.board.items())
        while True:
            try:
                yield next(subs)
            except StopIteration:
                break


class AlphaBeta(ChessTurnABC,Chessgame):

    type = 'alpha-beta'
    opponent = {'Black': 'White', 'White': 'Black'}
    def __init__(self,player):
        super(ChessTurnABC).__init__()
        self.player = player


    def call_multiprocess(self,node,maxing):
        depth = node.depth - 1
        self.root_node = node
        self.alphabeta(self.root_node, depth, maxing, -100000, 100000)
        optimal_node = max([child for child in self.root_node.children if child.value is not None])
        return optimal_node.parent


    def __call__(self,root,depth=3,maxing=True):

        self.root_node = ChessNode(depth,root)
        self.alphabeta(self.root_node,depth,maxing,-100000,100000)
        self._current_state_raw = max([child for child in self.root_node.children if child.value is not None]).board
        return self._current_state_raw

    def child_node_finder(self, node, depth,is_maxing):

        self.current_working_node = node
        child_nodes = []
        moves = defaultdict(list)
        if is_maxing:
            current_player = self.player
        else:
            current_player=self.opponent[self.player]
        for piece in self.current_working_node:
            piece.getpos(self.current_working_node)
            if piece.owner == current_player:
                piece.move_range(self.current_working_node)
                [moves[piece].append(x) for x in [*piece.avalible_moves.keys()]]

        for piece, moves in moves.items():
            self.current_piece = piece
            for move in moves:
                workingboard = copy.copy(self.current_working_node.board)
                workingboard[piece.position],workingboard[move] = Dummy(),piece
                child_nodes.append(ChessNode(depth,workingboard,parent=node))
        return tuple(child_nodes)

    def node_evaluation_heuristic(self, node):
        value = 0
        for piece in node:
            if piece.owner == self.player:
                value += piece.value
                if piece.move_range(node) != []:
                    value += len([*piece.avalible_moves.keys()])*0.1
            if piece.owner == self.opponent[self.player]:
                value -= piece.value
                if piece.move_range(node) != []:
                    value -= len([*piece.avalible_moves.keys()])*0.1
        return value

    def alphabeta(self, node, depth, maxing_player, alpha, beta):


        if depth == 0:
            value = self.node_evaluation_heuristic(node)
            node.value = value
            return value

        if maxing_player:
            value = -100000
            subnodes = self.child_node_finder(node,depth,maxing_player)
            node.children = subnodes
            for nodes in subnodes:
                val = self.alphabeta(nodes, depth - 1, False, alpha, beta)
                try:
                    value = max(value,val)
                except TypeError:
                    value = max(value, val[0])
                alpha = max(alpha, value)
                node.value = value
                if alpha >= beta:
                    break
                else:
                    continue
            return value
        else:
            value = 100000
            subnodes = self.child_node_finder(node, depth,maxing_player)
            node.children = subnodes
            for nodes in subnodes:
                val = self.alphabeta(nodes, depth - 1, True, alpha, beta)
                value = min(value, val)
                beta = min(beta, value)
                node.value = value
                if alpha >= beta:
                    break
                else: continue
            return value





class MultiprocessAB(AlphaBeta):

    def __init__(self, player, root,depth=3):
        super().__init__(player)

        self.root_node = ChessNode(depth,root)
        self.mp_childs = self.child_node_finder(self.root_node,depth-1,True)
        self.root_node.children = tuple(self.mp_childs)


    def __call__(self):

        with Pool(5) as p:
            data = p.map(child_process, self.mp_childs)
        self._current_state_raw=max(data)


if __name__ == '__main__':
    import time

    t = Chessgame()
    initial = time.time()
    for i in range(5,6):
        t0  = time.time()
        a = MultiprocessAB('Black',t._current_state_raw,depth=i)
        yepis = a()
        yepis.get_current_state(yepis.board)
        elapsed = time.time() - t0
        total = time.time()-initial
        print(f'depth: {i} run-time: {elapsed} total time : {total}')