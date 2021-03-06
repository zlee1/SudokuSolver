import math
import numpy as np
from sudoku import sudoku

# Check if a board has multiple solutions
class counter:
    """Counter class checks if there are multiple solutions for a board"""

    def __init__(self,board):
        """__init__ accepts a board in sudoku.py save string or np array format

        Parameters:
            board (2 dimensional numpy array or String): sudoku board
        """
        self.nn = len(board)
        self.n = math.sqrt(self.nn)

        # If the board is loaded as a save string, turn it into a numpy array
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

    def generateOptions(self, board, options = dict({})):
        """Generate all possible options for each cell

        Parameters:
            board (2 dimensional numpy array): sudoku board
            options (dictionary): current options for each cell in board
        """
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
        """Check that the board is complete and legal

        Parameters:
            board (2 dimensional numpy array): sudoku board
        """
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

    def checkLegalMove(self, board, row, col, val):
        """Check if a move is legal

        Parameters:
            board (2 dimensional numpy array): sudoku board
            row (int): row of the cell
            col (int): column of the cell
            val (int): value to fill the cell
        """
        # Value is outside of the legal range
        if(val not in range(1, self.nn+1)):
            return False
        # A value already exists in this cell
        elif(board[row][col] != 0):
            return False
        # The value already exists in this row
        elif(val in board[row]):
            return False
        # The value already exists in this column
        elif(val in np.rot90(board, 3)[col]):
            return False
        rmin, rmax, cmin, cmax = self.getSubboardIndices(row,col)
        # The value already exists in this subboard
        if(val in board[rmin:rmax, cmin:cmax].flatten()):
            return False
        return True

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

    def checkFullBoard(self,board):
        """Check if the board is fully populated

        Parameters:
            board (2 dimensional numpy array): sudoku board
        """
        for i in range(self.nn):
            for j in range(self.nn):
                # If there is an empty cell, the board is not fully populated
                if(board[i][j] == 0):
                    return False
        return True


    def countSolutions(self,board_instance):
        """Check if there are multiple solutions for the provided board
        Solution checking is done by recursively solving the board with different
        attempts at legal values for each empty cell.

        Parameters:
            board_instance (2 dimensional numpy array): sudoku board
        """
        
        board = board_instance.copy()

        n_solutions = 0
        options = dict({})
        while 1:
            # If there are multiple solutions, return the number. It does not matter
            # how many solutions there actually are because >1 means the board is
            # illegal
            if(n_solutions > 1):
                return n_solutions

            min_cell = None
            # Generate all possible options
            options = self.generateOptions(board, options)

            # If the board is full, a solution was found. Since only legal moves
            # can be made, a full board means a solved board.
            if(self.checkFullBoard(board)):
                return n_solutions + 1

            # If there are no possible moves and the board is not full, return the
            # current number of solutions
            if(len(options.keys()) == 0):
                return n_solutions

            for cell in options.keys():
                # If there are cells with only one possible option, make the move
                if(len(options.get(cell)) == 1 and self.checkLegalMove(board,cell[0],cell[1],options.get(cell)[0])):
                    board[cell[0],cell[1]] = options.get(cell)[0]
                # If the cell has fewer possible options than the current min_cell,
                # it is the new min_cell
                elif(min_cell == None or len(options.get(cell)) < len(options.get(min_cell))):
                    min_cell = cell

            # Check if the board is full again because of filling in naked singles
            if(self.checkFullBoard(board)):
                return n_solutions + 1
            elif(min_cell != None):
                for val in options.get(min_cell):
                    # For each possible value for min_cell, recursively call this
                    # function exploring the board with that value.
                    if(self.checkLegalMove(board,min_cell[0],min_cell[1],val)):
                        copy_board = board.copy()
                        copy_board[min_cell[0],min_cell[1]] = val
                        n_solutions += self.countSolutions(copy_board)
                    # Again, if there are multiple solutions, there is no need to
                    # explore more
                    if(n_solutions > 1):
                        return n_solutions
                # Return after the loop
                return n_solutions
