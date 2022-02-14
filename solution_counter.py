import math
import numpy as np
from sudoku import sudoku

class counter:

    def __init__(self,board):
        self.nn = len(board)
        self.n = math.sqrt(self.nn)
        if(type(board) == type("")):
            str_board = board
            split = str_board.split(",")
            size = len(split)
            for i in range(size):
                split[i] = int(split[i])
            self.nn = int(math.sqrt(size))
            self.n = int(math.sqrt(self.nn))
            board = []
            for i in range(self.nn):
                # Append each row as its own list
                board.append(split[i*self.nn:(i+1)*self.nn])
            board = np.array(board)
        self.original_board = board
        self.options = dict({})

    # Generate all possible options for each cell
    def generateOptions(self, board, options = dict({})):
        #options = dict({})
        if(options == {}):
            for row in range(len(board)):
                for col in range(len(board)):
                    for val in range(1,self.nn+1):
                        if(self.checkLegalMove(board,row,col,val) and ((row,col) not in options.keys() or val not in options.get((row,col)))):
                            # Add option to dictionary if it is not blacklisted
                            if((row,col) in options.keys()):
                                options[(row,col)].append(val)
                            else:
                                options.update({(row,col):[val]})
        else:
            delete_cells = []
            for cell in options.keys():
                # Remove keys that have empty lists for values
                if(options.get(cell) == []):
                    delete_cells.append(cell)
                else:
                    # Remove values that are blacklisted or otherwise impossible
                    for val in options.get(cell):
                        if(not self.checkLegalMove(board,cell[0],cell[1],val)):
                            options.get(cell).remove(val)
            for cell in delete_cells:
                del options[cell]
        return options

    def checkLegalBoard(self,board):
        for i in range(self.nn):
            # Check if the current row and column has all necessary values
            if(not (all(nums in board[i] for nums in range(1,self.nn+1)) and all(nums in np.rot90(board)[i] for nums in range(1,self.nn+1)))):
                return False
        for j in range(self.n):
            for k in range(self.n):
                # Check if current subboard has all necessary values
                if(not all(nums in board[int(j)*self.n:(int(j%self.n)+1)*self.n, int(k)*self.n:(int(k)+1)*self.n].flatten() for nums in range(1,self.nn+1))):
                    return False
        return True

    # Check if a move is legal
    def checkLegalMove(self, board, row, col, val):
        # Value is outside of the legal range
        if(val not in range(1, self.nn+1)):
            #print("Illegal value")
            return False
        # A value already exists in this cell
        elif(board[row][col] != 0):
            #print("Space already filled")
            return False
        # The value already exists in this row
        elif(val in board[row]):
            #print("Value already in row")
            return False
        # The value already exists in this column
        elif(val in np.rot90(board, 3)[col]):
            #print("Value already in column")
            return False
        rmin, rmax, cmin, cmax = self.getSubboardIndices(row,col)
        # The value already exists in this subboard
        if(val in board[rmin:rmax, cmin:cmax].flatten()):
            #print("Value already in subboard")
            return False
        return True

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

    def checkFullBoard(self,board):
        for i in range(self.nn):
            for j in range(self.nn):
                if(board[i][j] == 0):
                    return False
        return True

    def countSolutions(self,board_instance):
        board = board_instance.copy()
        #game = sudoku(self.n)
        #game.loadBoard(board)
        n_solutions = 0
        options = dict({})
        while 1:
            if(n_solutions > 1):
                return n_solutions

            min_cell = None
            options = self.generateOptions(board, options)

            if(self.checkFullBoard(board)):
                return n_solutions + 1

            if(len(options.keys()) == 0):
                return n_solutions
            for cell in options.keys():
                if(len(options.get(cell)) == 1 and self.checkLegalMove(board,cell[0],cell[1],options.get(cell)[0])):
                    board[cell[0],cell[1]] = options.get(cell)[0]
                elif(min_cell == None or len(options.get(cell)) < len(options.get(min_cell))):
                    min_cell = cell
            if(self.checkFullBoard(board)):
                return n_solutions + 1
            elif(min_cell != None):
                for val in options.get(min_cell):
                    if(self.checkLegalMove(board,min_cell[0],min_cell[1],val)):
                        copy_board = board.copy()
                        copy_board[min_cell[0],min_cell[1]] = val
                        n_solutions += self.countSolutions(copy_board)
                    if(n_solutions > 1):
                        return n_solutions
                return n_solutions
