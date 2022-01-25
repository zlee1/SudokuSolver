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
                        if(not ((row,col) in self.blacklistedOptions.keys() and val not in self.blacklistedOptions.get((row,col)))):
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
        for j in self.options.keys():
            try:
                rmin,rmax,cmin,cmax = self.game.getSubboardIndices(j[0], j[1])
                self.generateOptions()
                for val in self.options.get(j):
                    ronly = True # If value is the only one in the row
                    conly = True # If value is the only one in the column
                    sonly = True # If value is the only one in the subboard
                    for k in self.options.keys():
                        if(k != j):
                            if(k[0] == j[0]): # True if values are in the same row
                                if(val in self.options.get(k)):
                                    ronly = False
                            if(k[1] == j[1]): # True if values are in the same column
                                if(val in self.options.get(k)):
                                    conly = False
                            if(k[0] in range(rmin,rmax) and k[1] in range(cmin,cmax)): # True if values are in the same subboard
                                if(val in self.options.get(k)):
                                    sonly = False
                    if(ronly or conly or sonly): # Make move only if the value is the only one in the row, column, or subboard
                        self.game.makeMove(j[0], j[1], val)
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
        print()

    # Run solver
    def solve(self):
        loss = 0
        changes = 1
        while(not self.game.checkLegalBoard() and changes != 0): # Continue until board is complete and correct or no changes have been made
            #print()
            #self.game.printBoard()

            # Make naked single moves
            changes = self.nakedSingle()

            # If no naked singles exist, make hidden single moves
            changes += self.hiddenSingle()

        # Output board in final state and whether it is solved or not
        print()
        self.game.printBoard()
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

#print(game.getSudokuSolutionsLoadString())

solver = solver(game)

solver.solve()
