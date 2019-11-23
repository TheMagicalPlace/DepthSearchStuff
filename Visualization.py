
from collections import defaultdict
from matplotlib import pyplot as plt
import numpy as np
from ChessBoard import *
class BoardRepresentation:

    def __init__(self,raw_data):
        self.plt = plt
        self.plt.ion()
        self.fig ,self.ax = plt.subplots()
        self.sc = self.ax.scatter(x=[],y=[])
        self.plt.draw()
        self.plt.xticks([0, 1, 2, 3,4,5,6,7], ['              a', '              b', '              c', '              d'
                                           ,'              e','              f','              g','              h'])
        self.plt.yticks([ 0,1, 2, 3,4,5,6,7],['\n\n1', '\n\n2', '\n\n3', '\n\n4','\n\n5','\n\n6','\n\n7','\n\n8'])
        self.plt.grid(b=True)
        self.graphtable = {}
        self.piecedata = defaultdict(list)

    def animate_scatter(self,frames):

        self.sc.set_offsets(np.c_[frames[0], frames[1]])
        self.fig.canvas.draw_idle()
        self.plt.pause(0.001)

    def converter(self,raw_data):


        conversion = {j:i-0.5 for i,j in enumerate('abcdefgh')}

        for position,piece in raw_data.items():
            if self.piecedata[position] == []:
                self.piecedata[position].append([int(position[1])-0.5,conversion[position[0]]]) # 0
                self.piecedata[position].append(f'${piece.piece}$' if piece.piece != 'Not a Piece' else '') # 1
                self.piecedata[position].append('grey' if piece.owner == 'White' else '#000000' if piece.owner == 'Black' else None) # 2
                self.piecedata[position].append(self.animate_scatter((self.piecedata[position][0][0], self.piecedata[position][0][1]))) #3
                self.piecedata[position].append(self.ax.scatter(x=self.piecedata[position][0][0], y=self.piecedata[position][0][1], c=self.piecedata[position][2], #4
                                marker=self.piecedata[position][1], s=300, alpha=1, ))
            else:
                self.piecedata[position][0] = [int(position[1])-0.5,conversion[position[0]]]
                self.piecedata[position][1] = f'${piece.piece}$' if piece.piece != 'Not a Piece' else ''
                self.piecedata[position][2] = 'grey' if piece.owner == 'White' else '#000000' if piece.owner == 'Black' else None
                self.piecedata[position][4].remove()
                self.piecedata[position][3] = self.animate_scatter((self.piecedata[position][0][0], self.piecedata[position][0][1]))
                self.piecedata[position][4] = self.ax.scatter(x=self.piecedata[position][0][0], y=self.piecedata[position][0][1], c=self.piecedata[position][2], #4
                                marker=self.piecedata[position][1], s=300, alpha=1, )

    def __call__(self,data):
        piecedata = self.converter(data)


if __name__ == '__main__':


    test = Chessgame()
    b = BoardRepresentation(test._current_state_raw)

    b.converter(test._current_state_raw)
    plt.waitforbuttonpress()
