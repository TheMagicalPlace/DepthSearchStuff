
from Player_Base import *
import copy
import random as r
from abc import abstractclassmethod
from Visualization import *
from time import sleep
from ChessPieces import *
from colorama import Fore, Back, Style
import time

class Chessgame:
    Names = ['Rook', 'Knight', 'Bishop',
             'Queen', 'King', 'Pawn']
    opponent = {'Black': 'White', 'White': 'Black'}

    def __init__(self):

        self.board = []
        self.board_state = []
        self.current = []
        self._current_state_raw = {}
        self.is_in_check = False
        self.testvalue = None

        self._setup()
        self.king_check = {'Black': [], 'White': []}
        self.turn_count = 0
        self.testing_holdback = []

    def determine_checkmate(self,player):
        king_check = defaultdict(list)
        for k, v in self._current_state_raw.items():
            if v.owner == player:
                king_check[self.opponent[player]] += v.move_range(self._current_state_raw, True)
            if v.owner == self.opponent[player] and v.piece == 'Kng':
                king_pos, king = k, v
        try:
            king.move_range(self._current_state_raw)
        except UnboundLocalError:
            print((f'{self.opponent[player]} is in checkmate'))
            return -1
        else:
            king_move_range = list(king.avalible_moves.keys())
            king_move_range.append(king_pos)
            kmr = set(king_move_range)
            kcr = set(king_check[self.opponent[player]])
            if not kmr.issubset(kcr):
                print(kmr-kcr)
                if king_pos in kcr:
                    print(f'{self.opponent[player]} is in check')
                else:
                    print(f'{self.opponent[player]} is not in checkmate or check')
            else:
                print((f'{self.opponent[player]} is in checkmate'))
                return -1

    def _setup(self):
        '''
        This builds the intial chess board, calling constructors for all the chess pieces as well as a 'Dummy' piece to
        occupy empty spaces

        '''
        y = ["a", "b", "c", "d", "e", "f", "g", "h"]
        y.reverse() # sanity check this later
        for i in range(0, len(y)):
            self.board.append([y[i] + str(x) for x in range(1, 9)])
        back_row = lambda owner: [Rook(owner), Knight(owner), Bishop(owner),
                                  Queen(owner), King(owner), Bishop(owner), Knight(owner),
                                  Rook(owner)]

        for y in range(1, 9):
            self.board_state.append(back_row('Black')) if (y == 1) else \
            self.board_state.append([Pawn('Black') for i in range(1, 9)]) if (y == 2) else \
            self.board_state.append([Pawn('White') for i in range(1, 9)]) if (y == 7) else \
            self.board_state.append(back_row('White')) if (y == 8) else \
            self.board_state.append([Dummy() for x in range(1, 9)])

        tracker = {}
        for (a, b) in zip([xx for x in self.board for xx in x], [yy for y in self.board_state for yy in y]):
            tracker[a] = b
            if a in list(zip(*self.board))[-1]:
                self._current_state_raw.update(
                    tracker)  # the list of single dictionaries used for  tracking where everything is
                tracker = {}
            [v.getpos(self._current_state_raw) for k, v in self._current_state_raw.items()]
        self.get_current_state(self._current_state_raw)
        #self.Visual = BoardRepresentation(self._current_state_raw)

    def get_current_state(self, raw_state):

        k, v = [k for k, v in raw_state.items()], [v for k, v in raw_state.items()]
        self.current = []
        row = {}
        for i in range(0, len(k)):
            row[k[i]] = v[i]
            if len(row) == 8:
                self.current.append(row)
                row = {}

    def __call__(self, AI1:ChessTurnABC=None,AI2:ChessTurnABC=None):
        if AI1 is not None:
            white_ai=AI1('White',self._current_state_raw)
        if AI2 is not None:
            black_ai=AI2('Black',self._current_state_raw)
        turn = 1
        leave = None
        opponent = {'Black':'White','White':'Black'}
        current_player = 'White'
        while leave is None:
            print(current_player+'\'s Turn!')
            if current_player == 'White':
                if AI1 is not None:
                    leave = white_ai()
                    time.sleep(10)
                    if white_ai.type =='alpha-beta': leave = None
                    self._current_state_raw = white_ai._current_state_raw
                    self.get_current_state(self._current_state_raw)
                    leave = self.determine_checkmate(current_player)
                else:
                    pass
            else:
                if AI2 is not None:
                    leave = black_ai(self._current_state_raw)
                    if black_ai.type == 'alpha-beta': leave = None
                    self._current_state_raw = black_ai._current_state_raw
                    self.get_current_state(self._current_state_raw)
                    leave = self.determine_checkmate(current_player)
                else:
                    pass
            #self.Visual(self._current_state_raw)
            print(self)


            self.testing_holdback.append([copy.copy(self.current),copy.deepcopy(self._current_state_raw),
                                          black_ai.current_piece if current_player=='Black' else white_ai.current_piece])

            if leave is None: current_player = Chessgame.opponent[current_player]
            turn += 1
            if turn == 100:
                leave = -5
            else:
                turn +=1

        if leave == -1:
            return(turn,current_player)
        elif leave == -10:
            return(turn,'Stalemate')
        elif leave ==-5: return(turn,'Maximum Turns Reached')
        elif leave == -999:
            for i in range(-1, -6, -1):
                self.current = self.testing_holdback[i][0]
                print(self)
                self.current_piece = self.testing_holdback[i][2]
                print(self.__str__(True, self.testing_holdback[i][2].avalible_moves.keys()))
            return  [turn,current_player]


    def __str__(self, showmoves=False, moves=[]):

        """This just builds the actual board seen by the 'end-user' """

        rep_board = ''
        if showmoves == True:  # Outputs the board with the avalible moves for a given piece highlighted
            for dicts in self.current:
                rep_board += (
                                     "\n" + Back.LIGHTBLACK_EX + "|¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯|" + Back.RESET + "\n" + Back.LIGHTBLACK_EX + '|' + Back.RESET +
                                     (Back.LIGHTBLACK_EX + "||").join([(Back.MAGENTA if k in moves else
                                                                        Back.LIGHTBLACK_EX if k != self.current_piece.position
                                                                        else Fore.YELLOW + Back.LIGHTBLACK_EX) + ' ' + k
                                                                       + ': ' +
                                                                       (Back.MAGENTA if k in moves else
                                                                        Back.LIGHTBLACK_EX) + Style.BRIGHT + (
                                                                           Fore.YELLOW if k == (
                                                                               self.current_piece).position and self.is_in_check != True \
                                                                               else Fore.LIGHTWHITE_EX + Style.BRIGHT if i.owner == 'White'
                                                                           else Fore.BLACK + Style.BRIGHT if i.owner == 'Black'
                                                                           else Fore.RESET) + str(i)
                                                                       + ('   ' if str(i) == ' ' else '')
                                                                       + Fore.RESET for k, i in
                                                                       dicts.items()]) + Back.LIGHTBLACK_EX + "|" + Back.RESET
                                     + "\n" + Back.LIGHTBLACK_EX + "|_________||_________||_________||_________||_________||_________||_________||_________|") + Back.RESET + '\n'

        else:
            for dicts in self.current:
                rep_board += (
                                     "\n" + Back.LIGHTBLACK_EX + "|¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯||¯¯¯¯¯¯¯¯¯|" + Back.RESET + "\n" + Back.LIGHTBLACK_EX + '|' + Back.RESET +
                                     (Back.LIGHTBLACK_EX + "||").join([Back.LIGHTBLACK_EX + ' ' + k
                                                                       + ': ' + Back.LIGHTBLACK_EX + Style.BRIGHT + (
                                                                           Fore.LIGHTWHITE_EX + Style.BRIGHT if i.owner == 'White'
                                                                           else Fore.BLACK + Style.BRIGHT if i.owner == 'Black'
                                                                           else Fore.RESET) + str(i)
                                                                       + ('   ' if str(i) == ' ' else '')
                                                                       + Fore.RESET for k, i in dicts.items()
                                                                       ]) + Back.LIGHTBLACK_EX + "|" + Back.RESET
                                     + "\n" + Back.LIGHTBLACK_EX + "|_________||_________||_________||_________||_________||_________||_________||_________|") + Back.RESET + '\n'

        return '\n' + rep_board + '\n'