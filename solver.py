from sudoku import sudoku
import numpy as np
import datetime
import random
import math
import threading

class solver:

    # Construct solver with game as the sudoku game to be played
    def __init__(self, game):
        self.game = game
        self.options = dict({})
        self.blacklistedOptions = dict({})

    # Generate all possible options for each cell
    def generateOptions(self):
        self.options = {} # Clear previous options
        for row in range(self.game.nn):
            for col in range(self.game.nn):
                for val in range(1,self.game.nn+1):
                    if(self.game.checkLegalMove(row,col,val)):
                        if(((row,col) in self.blacklistedOptions.keys() and val not in self.blacklistedOptions.get((row,col))) or (row,col) not in self.blacklistedOptions.keys()):
                            # Add option to dictionary if it is not blacklisted
                            if((row,col) in self.options.keys()):
                                self.options[(row,col)].append(val)
                            else:
                                self.options.update({(row,col):[val]})

    # Fill in all naked singles
    # Naked single is when there is only one possible move for a cell
    def nakedSingle(self):
        changes = 0
        self.generateOptions()
        for i in self.options.keys():
            if(len(self.options.get(i)) == 1):
                self.game.makeMove(i[0], i[1], self.options.get(i)[0])
                changes += 1
        return changes

    # Fill in all hidden singles
    # Hidden single is when there is only one instance of a value in a given row, column, or subboard
    def hiddenSingle(self):
        changes = 0
        self.generateOptions()
        for i in self.options.keys():
            try:
                rmin,rmax,cmin,cmax = self.game.getSubboardIndices(i[0], i[1])
                self.generateOptions()
                for val in self.options.get(i):
                    ronly = True # If value is the only one in the row
                    conly = True # If value is the only one in the column
                    sonly = True # If value is the only one in the subboard
                    for j in self.options.keys():
                        if(j != i):
                            if(j[0] == i[0]): # True if values are in the same row
                                if(val in self.options.get(j)):
                                    ronly = False
                            if(j[1] == i[1]): # True if values are in the same column
                                if(val in self.options.get(j)):
                                    conly = False
                            if(j[0] in range(rmin,rmax) and j[1] in range(cmin,cmax)): # True if values are in the same subboard
                                if(val in self.options.get(j)):
                                    sonly = False
                    if(ronly or conly or sonly): # Make move only if the value is the only one in the row, column, or subboard
                        self.game.makeMove(i[0], i[1], val)
                        changes += 1
                        break
            except Exception as e:
                print(e)
        return changes

    # Blacklist values when a naked pair is present
    # Naked pair is when there are two cells in a row, column, or subboard that
    # have the same set of only 2 possible options, meaning those options can be
    # eliminated from the row, column, or subboard
    def nakedPair(self):
        changes = 0
        checked_pairs = [] # Ignore checked pairs to speed up process || To be implemented
        for i in self.options.keys():
            self.generateOptions()
            try:
                # Continue if there are only 2 options for this cell
                if(i in self.options.keys() and len(self.options.get(i)) == 2):
                    for j in self.options.keys():
                        # Continue if the cells are not the same and they both have only 2 options
                        if(i != j and len(self.options.get(j)) == 2):
                            # Continue if cells are in the same row and have the same options
                            if(i[0] == j[0] and self.options.get(i) == self.options.get(j)):
                                #print(f"Row-wise Naked Pair Found, {i}, {j}")
                                for k in self.options.keys():
                                    # Continue if cells are in the same row and are not the same
                                    if(k[0] == i[0] and k != i and k != j):
                                        for l in self.options.get(i):
                                            # If value is in cell that is not in pair, blacklist it
                                            if(l in self.options.get(k)):
                                                #print(f"Blacklisted, {k} {l}")
                                                # Add option to blacklist
                                                self.addToBlacklist(k[0],k[1],l)
                                                changes += 1

                            # Continue if cells are in the same column and have the same options
                            if(i[1] == j[1] and self.options.get(i) == self.options.get(j)):
                                #print(f"Column-wise Naked Pair Found, {i}, {j}")
                                for k in self.options.keys():
                                    # Continue if cells are in the same column and are not the same
                                    if(k[1] == i[1] and k != i and k != j):
                                        for l in self.options.get(i):
                                            # If value is in cell that is not in pair, blacklist it
                                            if(l in self.options.get(k)):
                                                #print(f"Blacklisted, {k} {l}")
                                                # Add option to blacklist
                                                self.addToBlacklist(k[0],k[1],l)
                                                changes += 1

                            rmin,rmax,cmin,cmax = self.game.getSubboardIndices(i[0],i[1])
                            # Continue if cells are in the same subboard and have the same options
                            if(j[0] in range(rmin,rmax) and j[1] in range(cmin,cmax) and self.options.get(i) == self.options.get(j)):
                                #print(f"Subboard-wise Naked Pair Found, {i}, {j}")
                                for k in self.options.keys():
                                    # Continue if cells are in the same subboard and are not the same
                                    if(k[0] in range(rmin,rmax) and k[1] in range(cmin,cmax) and k != i and k != j):
                                        for l in self.options.get(i):
                                            # If value is in cell that is not in pair, blacklist it
                                            if(l in self.options.get(k)):
                                                #print(f"Blacklisted, {k} {l}")
                                                # Add option to blacklist
                                                self.addToBlacklist(k[0],k[1],l)
                                                changes += 1
            except Exception as e:
                print(e)
        return changes

    # Handle hidden pair logic
    # Hidden pairs are when there are only 2 possible places for a pair of numbers
    # which means that all other options for those cells can be eliminated
    def hiddenPair(self):
        changes = 0
        checked_sections = [] # Ignore checked sections to speed up process || To be implemented
        for i in self.options.keys():
            try:
                self.generateOptions()
                # Row handling
                pairs = dict({})
                for j in self.options.keys():
                    if(i[0] == j[0]):
                        # Update dictionary for each value that is an option for this cell
                        for k in range(1,self.game.nn+1):
                            if(k in self.options.get(j)):
                                if(k in pairs.keys()):
                                    pairs[k].append(j)
                                else:
                                    pairs.update({k:[j]})
                changes += self.blacklistHiddenPairs(pairs)

                # Column handling
                pairs = dict({})
                for j in self.options.keys():
                    if(i[1] == j[1]):
                        # Update dictionary for each value that is an option for this cell
                        for k in range(1,self.game.nn+1):
                            if(k in self.options.get(j)):
                                if(k in pairs.keys()):
                                    pairs[k].append(j)
                                else:
                                    pairs.update({k:[j]})
                changes += self.blacklistHiddenPairs(pairs)

                # Subboard handling
                rmin,rmax,cmin,cmax = self.game.getSubboardIndices(i[0],i[1])
                pairs = dict({})
                for j in self.options.keys():
                    if(j[0] in range(rmin,rmax) and j[1] in range(cmin,cmax)):
                        # Update dictionary for each value that is an option for this cell
                        for k in range(1,self.game.nn+1):
                            if(k in self.options.get(j)):
                                if(k in pairs.keys()):
                                    pairs[k].append(j)
                                else:
                                    pairs.update({k:[j]})
                changes += self.blacklistHiddenPairs(pairs)

            except Exception as e:
                print(e)
        return changes

    # Find hidden pairs and blacklist impossible options
    def blacklistHiddenPairs(self, pairs):
        changes = 0
        for i in pairs.items():
            num = i[0]
            cells = i[1]
            # Only dealing with pairs
            if(len(cells) == 2):
                pair_vals = [num]
                for j in range(len(pairs.items())):
                    # If the two pairs are not from the same number but have the same cells, they form a pair
                    if(list(pairs.items())[j][0] != num and list(pairs.items())[j][1] == cells):
                        pair_vals.append(list(pairs.items())[j][0])
                # If there is a pair, remove impossible options from cells in pair
                if(len(pair_vals) > 1):
                    for cell in cells:
                        for option in self.options.get(cell):
                            if(option not in pair_vals):
                                self.addToBlacklist(cell[0],cell[1],option)
                                changes += 1
        return changes

    # Find pointing pairs and blacklist impossible options
    # Pointing pairs are when the only options for a value in a subboard are also
    # in the same row or column which means that the value must be within that
    # subboard and can be eliminated from other cells in the row or column
    def pointingPair(self):
        changes = 0
        for i in self.options.keys():
            try:
                self.generateOptions()

                # Row handling
                pairs = dict({})
                for j in self.options.keys():
                    if(j[0] == i[0]):
                        # Update dictionary for each value that is an option for this cell
                        for k in range(1,self.game.nn+1):
                            if(k in self.options.get(j)):
                                if(k in pairs.keys()):
                                    pairs[k].append(j)
                                else:
                                    pairs.update({k:[j]})

                for j in pairs.items():
                    rmin,rmax,cmin,cmax = self.game.getSubboardIndices(j[1][0][0],j[1][0][1])
                    # Continue if the value has possible cells > 1 and <= the subboard size
                    if(len(j[1]) <= self.game.n and len(j[1]) > 1):
                        # Check to ensure that the pair is contained in one subboard
                        all_in_sub = True
                        for k in j[1]:
                            if(k[1] not in range(cmin,cmax)):
                                all_in_sub = False

                        if(all_in_sub):
                            for k in self.options.keys():
                                # If the value is not in the pair and is in the subboard, blacklist pair value
                                if(k not in j[1] and k[0] in range(rmin,rmax) and k[1] in range(cmin,cmax)):
                                    if(j[0] in self.options.get(k)):
                                        self.addToBlacklist(k[0],k[1],j[0])
                                        changes += 1

                # Column handling
                pairs = dict({})
                for j in self.options.keys():
                    if(j[1] == i[1]):
                        # Update dictionary for each value that is an option for this cell
                        for k in range(1,self.game.nn+1):
                            if(k in self.options.get(j)):
                                if(k in pairs.keys()):
                                    pairs[k].append(j)
                                else:
                                    pairs.update({k:[j]})

                for j in pairs.items():
                    rmin,rmax,cmin,cmax = self.game.getSubboardIndices(j[1][0][0],j[1][0][1])
                    # Continue if the value has possible cells > 1 and <= the subboard size
                    if(len(j[1]) <= self.game.n and len(j[1]) > 1):
                        # Check to ensure that the pair is contained in one subboard
                        all_in_sub = True
                        for k in j[1]:
                            if(k[0] not in range(rmin,rmax)):
                                all_in_sub = False

                        if(all_in_sub):
                            for k in self.options.keys():
                                # If the value is not in the pair and is in the subboard, blacklist pair value
                                if(k not in j[1] and k[0] in range(rmin,rmax) and k[1] in range(cmin,cmax)):
                                    if(j[0] in self.options.get(k)):
                                        self.addToBlacklist(k[0],k[1],j[0])
                                        changes += 1


                # Subboard handling
                rmin,rmax,cmin,cmax = self.game.getSubboardIndices(i[0],i[1])
                pairs = dict({})
                for j in self.options.keys():
                    if(j[0] in range(rmin,rmax) and j[1] in range(cmin,cmax)):
                        # Update dictionary for each value that is an option for this cell
                        for k in range(1,self.game.nn+1):
                            if(k in self.options.get(j)):
                                if(k in pairs.keys()):
                                    pairs[k].append(j)
                                else:
                                    pairs.update({k:[j]})

                for j in pairs.items():
                    # Continue if the value has possible cells > 1 and <= the subboard size
                    if(len(j[1]) <= self.game.n and len(j[1]) > 1):
                        row = j[1][0][0]
                        col = j[1][0][1]
                        row_wise = True
                        col_wise = True
                        # Check if all possible cells for this value are in the same row or column
                        for k in j[1]:
                            if(k[0] != row):
                                row_wise = False
                            if(k[1] != col):
                                col_wise = False

                        # If there is a pointing pair present, blacklist impossible values
                        for k in self.options.keys():
                            # Check to ensure that there is a pointing pair,
                            # that the cell is in the same row/column as the pair,
                            # and that the cell is not in the same subboard as the pair
                            if(row_wise and k[0] == row and k[1] not in range(cmin,cmax)):
                                if(j[0] in self.options.get(k)):
                                    self.addToBlacklist(k[0],k[1],j[0])
                                    changes += 1
                            elif(col_wise and k[1] == col and k[0] not in range(rmin,rmax)):
                                if(j[0] in self.options.get(k)):
                                    self.addToBlacklist(k[0],k[1],j[0])
                                    changes += 1
            except Exception as e:
                print(e)
        return changes

    # Handle naked triples
    def nakedTriple(self):
        changes = 0
        for i in self.options.keys():
            try:
                self.generateOptions()
                row = []
                col = []
                subboard = []
                rmin,rmax,cmin,cmax = self.game.getSubboardIndices(i[0],i[1])
                for j in self.options.keys():
                    if(j[0] == i[0]):
                        row.append(j)
                    if(j[1] == i[1]):
                        col.append(j)
                    if(j[0] in range(rmin,rmax) and j[1] in range(cmin,cmax)):
                        subboard.append(j)
                for original_house in [row,col,subboard]:
                    house = original_house.copy()
                    # Remove cells that have more than 3 options
                    if(len(house) >= 3):
                        remove_cells = []
                        for cell in house:
                            if(len(self.options.get(cell)) > 3):
                                remove_cells.append(cell)
                        if(len(remove_cells) > 0):
                            for cell in remove_cells:
                                if(cell in house):
                                    house.remove(cell)

                    # Remove cells that contain values that only appear once
                    if(len(house) >= 3):
                        remove_cells = []
                        for cell in house:
                            for val in self.options.get(cell):
                                val_count = 0
                                for cell2 in house:
                                    if(val in self.options.get(cell2)):
                                        val_count += 1
                                if(val_count < 2):
                                    remove_cells.append(cell)
                                    break
                        if(len(remove_cells) > 0):
                            for cell in remove_cells:
                                if(cell in house):
                                    house.remove(cell)

                    # Remove cells that contain values that do not appear with at least 2 of the remaining values
                    if(len(house) >= 3):
                        remaining_values = []
                        remove_cells = []
                        for cell in house:
                            for val in self.options.get(cell):
                                if(val not in remaining_values):
                                    remaining_values.append(val)
                        if(len(remaining_values) >= 3):
                            for cell in house:
                                for val in self.options.get(cell):
                                    appears_with = []
                                    for cell2 in house:
                                        if(val in self.options.get(cell2)):
                                            for val2 in self.options.get(cell2):
                                                if(val2 != val and val2 not in appears_with and val in remaining_values):
                                                    appears_with.append(val2)
                                    if(len(appears_with) < 2):
                                        remove_cells.append(cell)
                        if(len(remove_cells) > 0):
                            for cell in remove_cells:
                                if(cell in house):
                                    house.remove(cell)

                    # Check if there is naked triple
                    if(len(house) >= 3):
                        remaining_values = []
                        for cell in house:
                            for val in self.options.get(cell):
                                if(val not in remaining_values):
                                    remaining_values.append(val)
                        if(len(remaining_values) == 3):
                            #print("Naked Triple Found!",house)
                            for blacklist_cell in original_house:
                                if(blacklist_cell not in house):
                                    for blacklist_val in self.options.get(blacklist_cell):
                                        if(blacklist_val in remaining_values):
                                            self.addToBlacklist(blacklist_cell[0],blacklist_cell[1],blacklist_val)
                                            #print("Blacklisted",blacklist_cell[0],blacklist_cell[1],blacklist_val)
                                            changes += 1
            except Exception as e:
                print(e)
        return changes

    # Add value to blacklist for a given cell
    def addToBlacklist(self,row,col,val):
        if((row,col) in self.blacklistedOptions.keys()):
            if(val not in self.blacklistedOptions.get((row,col))):
                self.blacklistedOptions[(row,col)].append(val)
                #print("Blacklisted",row+1,col+1,val)
        else:
            self.blacklistedOptions.update({(row,col):[val]})
            #print("Blacklisted",row+1,col+1,val)

    # Generate a legal, solved board
    def generateSolvedBoard(self,sub_size):
        # First row is all possible values in ascending order
        board = np.array([[0]*sub_size*sub_size]*sub_size*sub_size)
        test_game = sudoku(sub_size)
        board[0] = list(range(1,sub_size*sub_size+1))
        # Other rows in same subboard are the same, but shifted sub_size times
        for i in range(1,sub_size):
            board[i] = self.shiftRow(board[i-1],sub_size)
        # Other rows in other subboards take from the same row in the previous
        # subboard and then shift once
        for i in range(sub_size,sub_size*sub_size):
            board[i] = self.shiftRow(board[i-sub_size],1)
        test_game.loadBoard(board)
        return board

    # Shift a row to the left by nshift such that the front wraps around to the back
    def shiftRow(self,row,nshift):
        return list(row[nshift:]) + list(row[:nshift])

    # Shuffle a fully solved board
    def shuffleSolvedBoard(self,board):
        # Random range determined in a way that will ensure well-shuffled board
        for i in range(random.randint(len(board)*len(board),len(board)*len(board)*2)):
            r = random.randint(1,6)
            if(r == 1):
                # Perform a row-wise subboard shift
                board = self.subShift(board)
            elif(r == 2):
                # Perform a column-wise subboard shift
                rotated = np.rot90(board,3)
                rotated = self.subShift(rotated)
                board = np.rot90(rotated,1)
            elif(r == 3):
                # Perform a subboard-wise row shift
                board = self.individualShift(board)
            elif(r == 4):
                # Perform a subboard-wise column shift
                rotated = np.rot90(board,3)
                rotated = self.individualShift(rotated)
                board = np.rot90(rotated,1)
            elif(r == 5):
                # Rotate the board
                board = np.rot90(board,1)
            else:
                # Randomly change values (ex: all 1s become 5s, all 2s become 3s, etc.)
                order = list(np.arange(1,len(board)+1,1))
                random.shuffle(order)
                for i in range(len(board)):
                    for j in range(len(board)):
                        board[i][j] = order[board[i][j]-1]
        # Ensure that the board is still legal
        test_game = sudoku(int(math.sqrt(len(board))))
        test_game.loadBoard(board)
        if(not test_game.checkLegalBoard()):
            print("Illegal Board Generated")
        return board

    # Shift subboards row-wise (2nd row of subboards becomes 1st, 3rd becomes 2nd, etc.)
    def subShift(self,board):
        sub_size = int(math.sqrt(len(board)))
        copy = board.copy()
        board[sub_size*sub_size-sub_size:] = copy[:sub_size]
        board[:sub_size*sub_size-sub_size] = copy[sub_size:]
        return board

    # Shift individual row within subboard (within a subboard, 2nd row becomes 1st, 3rd becomes 2nd, etc.)
    def individualShift(self,board):
        sub_size = int(math.sqrt(len(board)))
        # Randomly pick a subboard to apply shift to
        i = random.randint(1,sub_size)
        sub = board[(i-1)*sub_size:i*sub_size]
        sub_copy = sub.copy()

        sub[0] = sub_copy[-1]
        sub[1:] = sub_copy[:-1]
        board[(i-1)*sub_size:i*sub_size] = sub
        return board

    # Generate a legal puzzle with a given difficulty and subboard size
    def generateBoard(self,sub_size=3,difficulty="any"):
        done = False
        while(not done):
            # Start with a fully solved, shuffled board
            board = self.shuffleSolvedBoard(self.generateSolvedBoard(sub_size))
            test_game = sudoku(sub_size)
            test_game.loadBoard(board)
            self.game = test_game
            n = sub_size
            nn = n*n
            # Generate all possible cell indices
            positions = []
            for i in range(nn):
                for j in range(nn):
                    positions.append([i,j])


            for i in range(nn*nn):
                # Choose a random cell and set its value to 0
                cell = random.choice(positions)
                original_val = board[cell[0],cell[1]]
                board[cell[0],cell[1]] = 0

                # Load the board in its current state and clear blacklist dictionary
                self.game.loadBoard(board)
                self.blacklistedOptions = dict({})

                # Check if the puzzle is solvable
                changes = 1
                while(changes != 0):
                    changes = self.nakedSingle()

                    # Hidden singles can only be used in puzzles with difficulties >= normal
                    if(changes == 0 and difficulty in ["normal","medium","hardish","any"]):
                        changes += self.hiddenSingle()

                    # Naked pairs can only be used in puzzles with difficulties >= medium
                    if(changes == 0 and difficulty in ["medium","hardish","any"]):
                        changes += self.nakedPair()

                    # Hidden pairs can only be used in puzzles with difficulties >= medium
                    if(changes == 0 and difficulty in ["medium","hardish","any"]):
                        changes += self.hiddenPair()

                    # Pointing pairs can only be used in puzzles with difficulties >= medium
                    if(changes == 0 and difficulty in ["medium","hardish","any"]):
                        changes += self.pointingPair()

                    # Naked triples can only be used in puzzles with difficulties >= hardish
                    if(changes == 0 and difficulty in ["hardish","any"]):
                        changes += self.nakedTriple()

                # If the board is not legal and solved, revert back to the last legal board
                if(not self.game.checkLegalBoard()):
                    board[cell[0],cell[1]] = original_val
                # If the board is legal and solved, remove the cell from the list of cells
                else:
                    positions.remove(cell)

            self.game.loadBoard(board)

            # Check to ensure that the puzzle difficulty matches requirements
            generated_difficulty = self.rateDifficulty(board)
            if(difficulty == "any" or generated_difficulty == difficulty):
                done = True
            else:
                print(f"Regenerating, difficulty was {generated_difficulty}, but expected was {difficulty}")
        print(generated_difficulty)
        self.game.loadBoard(board)

        # Write the board to a file based on difficulty and subboard size
        with open(f'GeneratedBoards\\{generated_difficulty}_{sub_size}.txt', 'a') as f:
            f.write(self.game.getSaveString())
        return board

    # Rate a puzzle's difficulty
    def rateDifficulty(self,board):
        # Keep track of the number of times a technique of each difficulty is used
        easy = 0
        normal = 0
        medium = 0
        hardish = 0

        # Load board, generate options, and clear the blacklist
        self.game.loadBoard(board)
        self.generateOptions()
        self.blacklistedOptions = dict({})

        # Solve the board and keep track of technique difficulty usage
        changes = 1
        while(changes > 0):
            changes = self.nakedSingle()
            if(changes > 0):
                easy += 1

            if(changes == 0):
                changes += self.hiddenSingle()
                if(changes > 0):
                    normal += 1

            if(changes == 0):
                changes += self.nakedPair()
                if(changes > 0):
                    medium += 1

            if(changes == 0):
                changes += self.hiddenPair()
                if(changes > 0):
                    medium += 1

            if(changes == 0):
                changes += self.pointingPair()
                if(changes > 0):
                    medium += 1

            if(changes == 0):
                changes += self.nakedTriple()
                if(changes > 0):
                    hardish += 1

        # Return calculated difficulty
        if(self.game.checkLegalBoard()):
            if(hardish > 0):
                return "hardish"
            elif(medium > 0):
                return "medium"
            elif(normal > 0):
                return "normal"
            elif(easy > 0):
                return "easy"
        else:
            return "illegal"

    # Generate multiple boards
    def generateNBoards(self,n,sub_size=3,difficulty="any"):
        for i in range(n):
            self.generateBoard(sub_size,difficulty)

    # Run solver
    def solve(self):
        start_time = datetime.datetime.now()
        total_changes = 0
        changes = 1
        loss = 0
        while(not self.game.checkLegalBoard() and loss < 3): # Continue until board is complete and correct or no changes have been made

            changes = self.nakedSingle()

            # SLower processes should only be done if no other things can happen
            if(changes == 0):
                changes += self.hiddenSingle()

            if(changes == 0):
                changes += self.nakedPair()

            if(changes == 0):
                changes += self.pointingPair()

            if(changes == 0):
                changes += self.hiddenPair()

            if(changes == 0):
                changes += self.nakedTriple()

            total_changes += changes

            if(changes == 0):
                loss += 1
            else:
                loss = 0

        # Output board in final state and whether it is solved or not
        print()
        self.game.printBoard()
        print(f"Total Changes: {total_changes}")
        if(self.game.checkLegalBoard()):
            print("Solved")
            print("Time to solve:",datetime.datetime.now()-start_time) # Show time to complete puzzle
        else:
            print("Unsolved")
