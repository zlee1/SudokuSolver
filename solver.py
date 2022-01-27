from game import sudoku
import numpy as np
import datetime

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
                            if(j[0] == j[0]): # True if values are in the same row
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

    # Add value to blacklist for a given cell
    def addToBlacklist(self,row,col,val):
        if((row,col) in self.blacklistedOptions.keys()):
            if(val not in self.blacklistedOptions.get((row,col))):
                self.blacklistedOptions[(row,col)].append(val)
        else:
            self.blacklistedOptions.update({(row,col):[val]})

    # Run solver
    def solve(self):
        start_time = datetime.datetime.now()
        total_changes = 0
        changes = 1
        while(not self.game.checkLegalBoard() and changes != 0): # Continue until board is complete and correct or no changes have been made
        
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

            total_changes += changes

        # Output board in final state and whether it is solved or not
        print()
        self.game.printBoard()
        print(f"Total Changes: {total_changes}")
        if(self.game.checkLegalBoard()):
            print("Solved")
            print("Time to solve:",datetime.datetime.now()-start_time)
        else:
            print("Unsolved")

game = sudoku(3)

# Board presets can be found in games.txt
game.loadBoard([[0,5,0,4,0,0,0,0,0],
[0,0,8,0,7,1,0,0,0],
[0,9,0,0,2,0,0,3,7],
[9,0,5,7,0,0,0,0,8],
[0,0,7,9,5,8,0,0,0],
[0,0,1,0,0,4,0,0,0],
[0,0,0,3,0,0,0,5,0],
[0,1,0,0,9,0,0,4,0],
[0,0,0,0,0,0,8,0,2]])

print(game.getSudokuSolutionsLoadString())

solver = solver(game)

solver.solve()
