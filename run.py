from sudoku import sudoku
from solver import solver
import math
from multiprocessing import Process

# Generate nboards on nprocesses using multiprocessing
def multiprocessingGeneration(nprocesses,nboards,sub_size=3,difficulty="any"):
    for i in range(nprocesses):
        s = solver(sudoku(3))
        p = Process(target=s.generateNBoards, args = (nper_process, sub_size, difficulty))
        p.start()

if __name__ == '__main__':
    multiprocessingGeneration(4,8,3,"any")