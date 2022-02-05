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

"""if __name__ == '__main__':
    multiprocessingGeneration(4,100,3,"any")"""


s = solver(sudoku(3))

s.game.loadBoard([[3,1,0,0,6,4,2,5,7],
[4,2,0,5,3,7,0,0,9],
[0,0,7,1,0,2,3,4,0],
[0,0,5,7,0,1,4,0,3],
[7,3,0,0,0,0,0,0,1],
[1,0,2,3,0,6,9,7,5],
[2,7,3,4,0,9,5,0,0],
[8,0,0,6,0,3,7,9,2],
[0,6,0,2,7,0,0,3,4]])

print(s.game.getSudokuSolutionsLoadString())

s.solve()
