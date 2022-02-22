import numpy as np
import random
import math


class sudoku:
    """Sudoku game"""

    def __init__(self, n):
        """__init__ accepts an integer for n value

        Parameters:
            n (int): number of subboards within a given row or column
        """
        self.n = n # Dimension of each subboard (standard board has n = 3)
        self.nn = n*n # Dimension of full board (standard board has nn = 9)
        self.board = np.array(self.generateEmpty()) # Start with empty board
        self.options = dict({}) # Generated possible options for each cell
        self.blacklistedOptions=dict({}) # Options that have been excluded from option generation

    def generateEmpty(self):
        """Generate an empty board"""
        board = []
        row = [0]*self.nn
        for i in range(self.nn):
            board.append(row)
        return board

    def popRand(self):
        """Populate the board with random values"""
        for i in range(self.nn):
            for j in range(self.nn):
                if(random.randint(0,100) < 50): # 50% chance that a cell will be left empty
                    self.board[i][j] = random.randint(1,self.nn)
                else:
                    self.board[i][j] = 0

    def loadBoard(self, board):
        """Load a board"""
        self.board = np.array(board)
        self.n = int(math.sqrt(len(board)))
        self.nn = len(board)

    def checkLegalBoard(self):
        """Check if board is in a legal and complete state"""
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

    def checkLegalMove(self, row, col, val):
        """Check if a move is legal

        Parameters:
            row (int): row of the cell
            column (int): column of the cell
            val (int): value to fill the cell
        """
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

    def makeMove(self, row, col, val):
        """Make a move on the board

        Parameters:
            row (int): row of the cell
            column (int): column of the cell
            val (int): value to fill the cell
        """
        # Only make legal moves
        if(self.checkLegalMove(row, col, val)):
            self.board[row][col] = val
            #print(row+1,col+1,val)

    def getSubboardIndices(self, row, col):
        """Find the indices of the current subboard based on row and column

        Parameters:
            row (int): row of the cell
            col (int): column of the cell
        """
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

    def canSee(self, row_a, col_a, row_b, col_b):
        """Check if a cell is in the same row, column, or subboard of another cell

        Parameters:
            row_a (int): row of the first cell
            col_a (int): column of the first cell
            row_b (int): row of the second cell
            col_b (int): column of the second cell
        """
        rmin,rmax,cmin,cmax = self.getSubboardIndices(row_a, col_a)
        if(row_a == row_b or col_a == col_b or (row_b in range(rmin,rmax) and col_b in range(cmin,cmax))):
            return True
        else:
            return False

    def playGame(self):
        """Allow the user to the game
        Mostly exists for testing purposes
        """
        while True:
            self.printBoard()
            row = int(input("Enter the row: "))
            col = int(input("Enter the column: "))
            val = int(input("Enter the new value: "))
            self.makeMove(row, col, val)

    def printBoard(self):
        """Print the board"""
        for i in self.board:
            print(i)

    def getSudokuSolutionsLoadString(self):
        """Convert board to a string so that it can be loaded into sudoku-solutions.com
        Mostly exists for testing purposes
        """
        load = "("
        for i in self.board:
            for j in i:
                if(j == 0):
                    load += " "
                else:
                    load += str(j)
        return load + ")"

    def getSaveString(self):
        """Convert board into a string that can be nicely saved in text file"""
        save = ""
        for i in self.board:
            for j in i:
                save += str(j)
                save += ","
        save = save[:-1]
        save += "\n"
        return save

    def loadSaveString(self,save):
        """Load a saved board into game

        Parameters:
            save (String): save string to be loaded into board
        """
        split = save.split(",")
        size = len(split)
        for i in range(size):
            split[i] = int(split[i])
        self.nn = int(math.sqrt(size))
        self.n = int(math.sqrt(self.nn))
        board = []
        for i in range(self.nn):
            # Append each row as its own list
            board.append(split[i*self.nn:(i+1)*self.nn])
        self.loadBoard(board)

    def prettyPrint(self):
        """Print the board in a clean, readable format"""
        for i in range(self.nn):
            # Print a blank line between subboards
            if(i%self.n == 0):
                print()
            for j in range(self.nn):
                # Print a blank line between subbboards
                if(j%self.n == 0):
                    print("  ",end="")
                if(j == self.nn-1):
                    # Print "_" for empty values instead of 0
                    if(self.board[i][j] == 0):
                        print("_")
                    else:
                        print(self.board[i][j])
                else:
                    # End_val is the spaces added to the end of the value
                    # Appropriate number of spaces is the required number of spaces for
                    # the cell string to have the same length as the longest possible cell string + 1
                    # ex: max number = 100, current number = 1, # of spaces = 2 (+1)
                    end_val = " "
                    if(self.board[i][j] == 0):
                        # Print "_" for empty values instead of 0
                        for k in range(len(str(self.nn))-len("_")):
                            end_val += " "
                        print("_",end=end_val)
                    else:
                        for k in range(len(str(self.nn))-len(str(self.board[i][j]))):
                            end_val += " "
                        print(self.board[i][j],end=end_val)
