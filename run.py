from sudoku import sudoku
from solver import solver
import math, random
from multiprocessing import Process
from datetime import datetime
import time
from solution_counter import counter

# Generate nboards on nprocesses using multiprocessing
def multiprocessingGeneration(nprocesses,nboards,sub_size=3,difficulty="any"):
    """Generate boards with mutliprocessing for faster results"""
    for i in range(nprocesses):
        s = solver(sudoku(3))
        p = Process(target=s.generateNBoards, args = (nboards, sub_size, difficulty))
        p.start()

if __name__ == '__main__':
    multiprocessingGeneration(8,10,2,-1)

    """
    s = solver(sudoku(3))

    for i in range(3):
        s.game.loadSaveString("0,2,0,7,0,5,0,0,4,0,0,8,9,0,6,1,5,0,5,0,0,3,0,0,0,0,0,0,9,0,0,0,1,0,0,0,0,3,0,6,0,2,0,0,0,0,0,0,0,0,4,0,2,6,0,0,9,0,0,0,3,0,0,0,0,3,0,0,0,0,0,1,0,1,0,0,8,0,0,9,0")

        #print(s.game.getSudokuSolutionsLoadString())

        s.solve()"""
