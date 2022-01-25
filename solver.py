from game import sudoku

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
                                                if((k[0],k[1]) in self.blacklistedOptions.keys()):
                                                    self.blacklistedOptions[(k[0],k[1])].append(l)
                                                    changes += 1
                                                else:
                                                    self.blacklistedOptions.update({(k[0],k[1]):[l]})
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
                                                if((k[0],k[1]) in self.blacklistedOptions.keys()):
                                                    self.blacklistedOptions[(k[0],k[1])].append(l)
                                                    changes += 1
                                                else:
                                                    self.blacklistedOptions.update({(k[0],k[1]):[l]})
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
                                                if((k[0],k[1]) in self.blacklistedOptions.keys()):
                                                    self.blacklistedOptions[(k[0],k[1])].append(l)
                                                    changes += 1
                                                else:
                                                    self.blacklistedOptions.update({(k[0],k[1]):[l]})
                                                    changes += 1
            except Exception as e:
                print(e)
        return changes

    # Run solver
    def solve(self):
        total_changes = 0
        changes = 1
        while(not self.game.checkLegalBoard() and changes != 0): # Continue until board is complete and correct or no changes have been made
            #print()
            #self.game.printBoard()

            # Make naked single moves
            changes = self.nakedSingle()

            # If no naked singles exist, make hidden single moves
            changes += self.hiddenSingle()

            changes += self.nakedPair()

            total_changes += changes

        # Output board in final state and whether it is solved or not
        print()
        self.game.printBoard()
        print(f"Total Changes: {total_changes}")
        if(self.game.checkLegalBoard()):
            print("Solved")
        else:
            print("Unsolved")

game = sudoku(3)

# Board presets can be found in games.txt
game.loadBoard([[7,0,0,0,0,5,0,0,9],
[0,0,5,2,0,0,0,1,0],
[0,0,0,1,0,0,0,0,5],
[0,7,0,0,0,0,8,0,0],
[9,0,0,6,0,1,0,0,4],
[0,0,4,0,0,0,0,2,0],
[2,0,0,0,0,8,0,0,0],
[0,3,0,0,0,7,9,0,0],
[8,0,0,3,0,0,0,0,6]])

print(game.getSudokuSolutionsLoadString())

solver = solver(game)

solver.solve()
