from sudoku import sudoku
from solver import solver

# Create game
game = sudoku(3)

solver = solver(game)

# Generate boards
while 1:
    solver.generateBoard(3, "any")
