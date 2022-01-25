import numpy as np
import random
import math


class sudoku:

    # Construct game with subboards of dimension n
    def __init__(self, n):
        self.n = n # Dimension of each subboard (standard board has n = 3)
        self.nn = n*n # Dimension of full board (standard board has nn = 9)
        self.board = np.array(self.generateEmpty()) # Start with empty board
        self.options = dict({}) # Generated possible options for each cell
        self.blacklistedOptions=dict({}) # Options that have been excluded from option generation

    # Generate an empty board
    def generateEmpty(self):
        board = []
        row = [0]*self.nn
        for i in range(self.nn):
            board.append(row)
        return board

    # Populate the board with random values
    def popRand(self):
        for i in range(self.nn):
            for j in range(self.nn):
                if(random.randint(0,100) < 50): # 50% chance that a cell will be left empty
                    self.board[i][j] = random.randint(1,self.nn)
                else:
                    self.board[i][j] = 0

    # Load a board
    def loadBoard(self, board):
        self.board = np.array(board)
        self.n = int(math.sqrt(len(board)))
        self.nn = len(board)

    # Check if board is in a legal and complete state
    def checkLegalBoard(self):
        for i in range(self.nn):
            # Check if the current row and column has all necessary values
            if(not (all(nums in self.board[i] for nums in range(1,self.nn+1)) and all(nums in np.rot90(self.board)[i] for nums in range(1,self.nn+1)))):
                return False
        for j in range(self.n):
            for k in range(self.n):
                # Check if current subboard has all necessary values
                if(not all(nums in self.board[int(j)*self.n:(int(j%self.n)+1)*self.n, int(k)*self.n:(int(k)+1)*self.n].flatten() for nums in range(1,self.nn+1))):
                    return False
        return True

    # Check if a move is legal
    def checkLegalMove(self, row, col, val):
        # Value is outside of the legal range
        if(val not in range(1, self.nn+1)):
            #print("Illegal value")
            return False
        # A value already exists in this cell
        elif(self.board[row][col] != 0):
            #print("Space already filled")
            return False
        # The value already exists in this row
        elif(val in self.board[row]):
            #print("Value already in row")
            return False
        # The value already exists in this column
        elif(val in np.rot90(self.board, 3)[col]):
            #print("Value already in column")
            return False
        rmin, rmax, cmin, cmax = self.getSubboardIndices(row,col)
        # The value already exists in this subboard
        if(val in self.board[rmin:rmax, cmin:cmax].flatten()):
            #print("Value already in subboard")
            return False
        return True

    # Make a move
    def makeMove(self, row, col, val):
        # Only make legal moves
        if(self.checkLegalMove(row, col, val)):
            self.board[row][col] = val
            #print(row,col,val)
        else:
            print(f"Cannot make move {row}, {col}, {val}")

    # Find the indices of the current subboard based on row and column
    def getSubboardIndices(self, row, col):
        rmin = 0
        rmax = 0
        cmin = 0
        cmax = 0
        for i in range(self.n):
            # Check if values are in specified range
            # For a standard board, the ranges are: 0:3, 3:6, 6:9
            if(row in range(i*self.n, (i+1)*self.n)):
                rmin = i*self.n
                rmax = (i+1)*self.n
            if(col in range(i*self.n, (i+1)*self.n)):
                cmin = i*self.n
                cmax = (i+1)*self.n
        return rmin,rmax,cmin,cmax

    # Allow the user to the game (Mostly exists for testing purposes)
    def playGame(self):
        while True:
            self.printBoard()
            row = int(input("Enter the row: "))
            col = int(input("Enter the column: "))
            val = int(input("Enter the new value: "))
            self.makeMove(row, col, val)

    # Print the board
    def printBoard(self):
        for i in self.board:
            print(i)

    # Convert board to a string so that it can be loaded into sudoku-solutions.com
    def getSudokuSolutionsLoadString(self):
        load = "("
        for i in self.board:
            for j in i:
                if(j == 0):
                    load += " "
                else:
                    load += str(j)
        return load + ")"
