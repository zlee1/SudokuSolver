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

#if __name__ == '__main__':
#    multiprocessingGeneration(4,8,3,"any")

s = solver(sudoku(3))

s.game.loadBoard([[1,0,0,0,0,4,0,5,0],
[0,0,0,0,2,0,4,0,3],
[0,0,6,0,0,7,9,0,0],
[7,6,0,0,0,0,0,1,0],
[0,0,0,0,3,0,0,0,0],
[0,2,0,0,0,0,0,9,4],
[0,0,7,9,0,0,5,0,0],
[3,0,2,0,8,0,0,0,0],
[0,1,0,2,0,0,0,0,9]])

print(s.game.getSudokuSolutionsLoadString())

s.solve()
