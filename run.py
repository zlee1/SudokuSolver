from sudoku import sudoku
from solver import solver
import math, threading

# Generate boards with multithreading
def threadedGeneration(nthreads,nboards,sub_size=3,difficulty="any"):
    nper_thread = int(math.ceil(nboards/nthreads))
    for i in range(nthreads):
        s = solver(sudoku(3))
        threading.Thread(target = s.generateNBoards, args = (nper_thread, sub_size, difficulty)).start()

threadedGeneration(4,8,3,"any")
