from sudoku import sudoku
from solver import solver
import math, random
from multiprocessing import Process

# Generate nboards on nprocesses using multiprocessing
def multiprocessingGeneration(nprocesses,nboards,sub_size=3,difficulty="any"):
    for i in range(nprocesses):
        s = solver(sudoku(3))
        p = Process(target=s.generateNBoards, args = (nboards, sub_size, difficulty))
        p.start()
"""
if __name__ == '__main__':
    multiprocessingGeneration(4,100,3,"any")"""


s = solver(sudoku(3))

s.game.loadBoard([[0,0,0,8,5,4,0,0,6],
[4,5,0,1,6,7,0,0,8],
[0,7,0,3,9,2,5,4,1],
[0,0,4,5,3,0,0,9,2],
[0,0,5,9,4,0,6,0,3],
[9,3,0,2,7,0,4,0,5],
[1,9,2,7,8,5,3,6,4],
[5,6,7,4,0,3,0,0,9],
[0,4,0,6,0,9,0,5,7]])

print(s.game.getSudokuSolutionsLoadString())

s.solve()
