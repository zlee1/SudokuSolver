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
    #multiprocessingGeneration(8,10,4,-1)


    s = solver(sudoku(3))

    s.game.loadBoard([[0,0,0,2,0,0,9,0,0],
    [8,0,0,0,6,0,0,0,0],
    [9,0,1,0,3,0,7,0,2],
    [0,0,0,5,0,0,8,0,0],
    [0,0,0,6,7,3,0,0,0],
    [0,0,7,0,0,4,0,0,0],
    [4,0,9,0,0,0,5,0,7],
    [0,0,0,0,4,0,0,0,1],
    [0,0,5,3,0,1,0,0,0]])

    print(s.game.getSudokuSolutionsLoadString())

    s.solve()
