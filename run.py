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

if __name__ == '__main__':
    multiprocessingGeneration(4,100,3,"any")


"""s = solver(sudoku(3))

s.game.loadBoard([[0,0,3,8,0,0,5,1,0],
[0,0,8,7,0,0,9,3,0],
[1,0,0,3,0,5,7,2,8],
[0,0,0,2,0,0,8,4,9],
[8,0,1,9,0,6,2,5,7],
[0,0,0,5,0,0,1,6,3],
[9,6,4,1,2,7,3,8,5],
[3,8,2,6,5,9,4,7,1],
[0,1,0,4,0,0,6,9,2]])

print(s.game.getSudokuSolutionsLoadString())

s.solve()"""
