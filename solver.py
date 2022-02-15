from sudoku import sudoku
import numpy as np
from datetime import datetime
import random
import math
import traceback

class solver:

    # Construct solver with game as the sudoku game to be played
    def __init__(self, game):
        self.game = game
        self.options = dict({})
        self.blacklistedOptions = dict({})

    # Generate all possible options for each cell
    def generateOptions(self):
        #self.options = {} # Clear previous options
        if(self.options == {}):
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
        # Faster than erasing and remaking the options dict each time
        else:
            # Cells to be removed from dictionary
            delete_cells = []
            for cell in self.options.keys():
                # Remove keys that have empty lists for values
                if(self.options.get(cell) == []):
                    delete_cells.append(cell)
                else:
                    # Remove values that are blacklisted or otherwise impossible
                    for val in self.options.get(cell):
                        if(not self.game.checkLegalMove(cell[0],cell[1],val) or (cell in self.blacklistedOptions.keys() and val in self.blacklistedOptions.get(cell))):
                            self.options.get(cell).remove(val)
            for cell in delete_cells:
                del self.options[cell]

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

        # Get the cells in each row, col, and subboard
        rows = dict({})
        cols = dict({})
        subs = dict({})
        for i in self.options.keys():
            if(i[0] in rows.keys()):
                rows[i[0]].append(i)
            else:
                rows.update({i[0]:[i]})

            if(i[1] in cols.keys()):
                cols[i[1]].append(i)
            else:
                cols.update({i[1]:[i]})

            rmin,rmax,cmin,cmax = self.game.getSubboardIndices(i[0],i[1])
            tup = (rmin,rmax,cmin,cmax)

            if(tup in subs.keys()):
                subs[tup].append(i)
            else:
                subs.update({tup:[i]})

        # For each row, column, and subboard
        for house in [rows,cols,subs]:
            for h in list(house.values()):
                # Get all values and the cells they appear in
                values = dict({})
                for cell in h:
                    try:
                        for val in self.options.get(cell):
                            if(val in values.keys()):
                                values[val].append(cell)
                            else:
                                values.update({val:[cell]})
                    except Exception as e:
                        traceback.print_exc()
                # If there is only one cell with a value as an option, make the move
                for val in values.keys():
                    if(len(values.get(val)) == 1):
                        self.game.makeMove(values.get(val)[0][0],values.get(val)[0][1], val)
                        changes += 1
        return changes

    # Blacklist values when a naked pair is present
    # Naked pair is when there are two cells in a row, column, or subboard that
    # have the same set of only 2 possible options, meaning those options can be
    # eliminated from the row, column, or subboard
    def nakedPair(self):
        changes = 0
        checked_pairs = [] # Ignore checked pairs to speed up process || To be implemented
        self.generateOptions()
        for i in self.options.keys():
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
        self.generateOptions()
        for i in self.options.keys():
            try:

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
        self.generateOptions()
        for i in self.options.keys():
            try:


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

    # Find naked sets and blacklist impossible options
    # Naked sets (triples, quads, quints, etc.) are when there are set_size
    # possible values across set_size cells. This means that any other instance
    # of those values in the same container can be removed from possible options
    def nakedSet(self, set_size):
        changes = 0
        self.generateOptions()
        for i in self.options.keys():
            try:

                # Make lists containing cells of the row, colum, and subboard of the current cell
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

                for original_container in [row,col,subboard]:
                    container = original_container.copy()

                    # Remove cells that have more than set_size options
                    if(len(container) >= set_size):
                        remove_cells = []
                        for cell in container:
                            if(len(self.options.get(cell)) > set_size):
                                remove_cells.append(cell)
                        if(len(remove_cells) > 0):
                            for cell in remove_cells:
                                if(cell in container):
                                    container.remove(cell)

                    # Remove cells that contain values that only appear once
                    if(len(container) >= set_size):
                        remove_cells = []
                        for cell in container:
                            for val in self.options.get(cell):
                                # Count how many times a value appears
                                val_count = 0
                                for cell2 in container:
                                    if(val in self.options.get(cell2)):
                                        val_count += 1
                                # Add cells to list for removal
                                if(val_count < 2):
                                    remove_cells.append(cell)
                                    break
                        # Remove cells
                        if(len(remove_cells) > 0):
                            for cell in remove_cells:
                                if(cell in container):
                                    container.remove(cell)

                    # Remove cells that contain values that do not appear with at least 2 of the remaining values
                    if(len(container) >= set_size):
                        remaining_values = []
                        remove_cells = []
                        # Get list of all values that remain in the container
                        for cell in container:
                            for val in self.options.get(cell):
                                if(val not in remaining_values):
                                    remaining_values.append(val)

                        if(len(remaining_values) >= set_size):
                            for cell in container:
                                for val in self.options.get(cell):
                                    # Get the values that the current value appears with in the container
                                    appears_with = []
                                    for cell2 in container:
                                        if(val in self.options.get(cell2)):
                                            for val2 in self.options.get(cell2):
                                                if(val2 != val and val2 not in appears_with and val in remaining_values):
                                                    appears_with.append(val2)
                                    # If the value only appears with 1 other value, add cell to list for removal
                                    if(len(appears_with) < 2):
                                        remove_cells.append(cell)
                        # Remove cells
                        if(len(remove_cells) > 0):
                            for cell in remove_cells:
                                if(cell in container):
                                    container.remove(cell)

                    # There is a naked set if there are set_size remaining values across set_size cells
                    if(len(container) >= set_size):
                        remaining_values = []
                        for cell in container:
                            for val in self.options.get(cell):
                                if(val not in remaining_values):
                                    remaining_values.append(val)
                        if(len(remaining_values) == set_size):
                            #print(f"Naked {set_size} Found!",container,remaining_values)
                            # Blacklist values of the naked set in other cells of the container
                            for blacklist_cell in original_container:
                                if(blacklist_cell not in container):
                                    for blacklist_val in self.options.get(blacklist_cell):
                                        if(blacklist_val in remaining_values):
                                            self.addToBlacklist(blacklist_cell[0],blacklist_cell[1],blacklist_val)
                                            #print("Blacklisted",blacklist_cell[0],blacklist_cell[1],blacklist_val)
                                            changes += 1
            except Exception as e:
                print(e)
        return changes

    # Find hidden sets and blacklist impossible options
    # Hidden sets (triples, quads, quints, etc.) are when there are set_size
    # possible values that only occur in set_size cells. This means that any other
    # values in those cells can be removed
    def hiddenSet(self, set_size):
        changes = 0
        self.generateOptions()
        for i in self.options.keys():
            try:

                # Make lists containing cells of the row, colum, and subboard of the current cell
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
                for original_container in [row,col,subboard]:
                    container = original_container.copy()

                    # For each value, get the cells that it shows up in
                    value_cells = dict({})
                    for cell in original_container:
                        for value in self.options.get(cell):
                            if(value not in value_cells.keys()):
                                value_cells.update({value:[cell]})
                            else:
                                value_cells[value].append(cell)

                    # If the total number of values is less than set_size, it is impossible for there to be a hidden triple
                    if(len(value_cells.keys()) >= set_size):
                        remove_values = []
                        for value in value_cells.keys():
                            if(len(value_cells.get(value)) > set_size):
                                remove_values.append(value)
                        for value in remove_values:
                            value_cells.pop(value)

                    # Remove values that do not appear with at least 2 of the remaining values
                    if(len(value_cells.keys()) >= set_size):
                        remaining_values = value_cells.keys()
                        remove_values = []
                        if(len(remaining_values) >= set_size):
                            for val in remaining_values:
                                # Get the values that the current value appears with in the container
                                appears_with = []
                                for cell in container:
                                    if(val in self.options.get(cell)):
                                        for val2 in self.options.get(cell):
                                            if(val2 not in appears_with and val2 in remaining_values):
                                                appears_with.append(val2)
                                # If the value appears with less than 2 others, append it to list to be removed
                                if(len(appears_with) < 2):
                                    remove_values.append(val)

                        # Remove values
                        if(len(remove_values) > 0):
                            for value in remove_values:
                                if(value in value_cells.keys()):
                                    value_cells.pop(value)

                    # If the remaining number of values and cells both equal set_size, there is a hidden set
                    if(len(value_cells.keys()) == set_size):
                        all_cells = []
                        for cells in value_cells.values():
                            for cell in cells:
                                if(cell not in all_cells):
                                    all_cells.append(cell)
                        if(len(all_cells) == set_size):
                            #print(f"Hidden {set_size} Found!", value_cells)
                            for cell in all_cells:
                                for val in self.options.get(cell):
                                    if(val not in value_cells.keys()):
                                        self.addToBlacklist(cell[0],cell[1],val)
                                        changes += 1
            except Exception as e:
                print(e)
        return changes

    # Find X-Wing patterns and blacklist impossible options
    # X-Wing is when a rectangle can be formed by 4 cells that have the same value
    # as one of the options. If two opposite sides of the rectangle are the only two
    # instances of that value in their row/column, then the value cannot appear in
    # the rows or columns of the rectangle's sides
    def xWing(self):
        changes = 0
        # For every possible value on the board
        self.generateOptions()
        for val in range(1,self.game.nn):
            try:


                # Get dictionary of each row/col index and each cell that could be in an X-Wing for that row/col
                rows = dict({})
                cols = dict({})
                for cell in self.options.keys():
                    # Add each cell that has the current value from each row/col
                    if(val in self.options.get(cell)):
                        if(cell[0] in rows.keys()):
                            rows[cell[0]].append(cell)
                        else:
                            rows.update({cell[0]:[cell]})
                        if(cell[1] in cols.keys()):
                            cols[cell[1]].append(cell)
                        else:
                            cols.update({cell[1]:[cell]})

                # Potential X-Wing rows need to have exactly 2 cells with the current value
                potential_rows = dict({})
                for row in rows.keys():
                    if(len(rows.get(row)) == 2):
                        potential_rows.update({row:rows.get(row)})

                # Potential X-Wing cols need to have exactly 2 cells with the current value
                potential_cols = dict({})
                for col in cols.keys():
                    if(len(cols.get(col)) == 2):
                        potential_cols.update({col:cols.get(col)})

                x_wing = []
                if(len(potential_rows) > 1):
                    # For every potential row, check if there is another potential row that has its cells in the same columns
                    for row in potential_rows.keys():
                        col_vals = sorted([cell[1] for cell in potential_rows.get(row)])
                        for comp_row in potential_rows.keys():
                            # If comp_row's cells are in the same columns as the original row's cells, an X-Wing is present
                            if(sorted(cell[1] for cell in potential_rows.get(comp_row)) == col_vals):
                                x_wing = [potential_rows.get(row)[0],potential_rows.get(row)[1],potential_rows.get(comp_row)[0],potential_rows.get(comp_row)[1]]

                                # Make sure that not all cells are in the same subboard
                                indices = [self.game.getSubboardIndices(cell[0],cell[1]) for cell in x_wing]
                                valid = False
                                for i in indices:
                                    if(i != indices[0]):
                                        valid = True

                                # Make sure that each cell only appears once in the X-Wing
                                for i in x_wing:
                                    count = 0
                                    for j in x_wing:
                                        if(i == j):
                                            count += 1
                                    if(count > 1):
                                        valid = False

                                if(valid):
                                    rows = [cell[0] for cell in x_wing]
                                    cols = [cell[1] for cell in x_wing]
                                    # Blacklist the current value in cells that are in the same rows and columns of the X-Wing
                                    for i in self.options.keys():
                                        if(i not in x_wing and val in self.options.get(i) and (i[0] in rows or i[1] in cols)):
                                            self.addToBlacklist(i[0],i[1],val)
                                            changes += 1
                                else:
                                    x_wing = []

                if(len(potential_cols) > 1):
                    # For every potential column, check if there is another potential column that has its cells in the same rows
                    for col in potential_cols.keys():
                        row_vals = sorted([cell[0] for cell in potential_cols.get(col)])
                        for comp_col in potential_cols.keys():
                            # If comp_col's cells are in the same rows as the original col's cells, an X-Wing is present
                            if(sorted(cell[0] for cell in potential_cols.get(comp_col)) == row_vals):
                                x_wing = [potential_cols.get(col)[0],potential_cols.get(col)[1],potential_cols.get(comp_col)[0],potential_cols.get(comp_col)[1]]

                                # Make sure that not all cells are in the same subboard
                                indices = [self.game.getSubboardIndices(cell[0],cell[1]) for cell in x_wing]
                                valid = False
                                for i in indices:
                                    if(i != indices[0]):
                                        valid = True

                                # Make sure that each cell only appears once in the X-Wing
                                for i in x_wing:
                                    count = 0
                                    for j in x_wing:
                                        if(i == j):
                                            count += 1
                                    if(count > 1):
                                        valid = False

                                if(valid):
                                    rows = [cell[0] for cell in x_wing]
                                    cols = [cell[1] for cell in x_wing]
                                    # Blacklist the current value in cells that are in the same rows and columns of the X-Wing
                                    for i in self.options.keys():
                                        if(i not in x_wing and val in self.options.get(i) and (i[0] in rows or i[1] in cols)):
                                            self.addToBlacklist(i[0],i[1],val)
                                            changes += 1
                                else:
                                    x_wing = []
            except Exception as e:
                print(e)
        return changes

    # Find set_size-fish and blacklist impossible options
    # A set_size-fish is like an X-Wing, but instead of 2 rows/cols with the value,
    # there are set_size rows/cols with the value. A set_size of 3 means there are
    # 3 rows/cols with a value that spans across 3 cols/rows. This means that the
    # value can be blacklisted in cells that are in the same rows/cols as the fish,
    # but are not a part of the fish.
    def fish(self,set_size):
        changes = 0
        # For every possible value on the board
        self.generateOptions()
        for val in range(1,self.game.nn):
            try:


                # Get dictionary of each row/col index and each cell that could be in an X-Wing for that row/col
                rows = dict({})
                cols = dict({})
                for cell in self.options.keys():
                    # Add each cell that has the current value from each row/col
                    if(val in self.options.get(cell)):
                        if(cell[0] in rows.keys()):
                            rows[cell[0]].append(cell)
                        else:
                            rows.update({cell[0]:[cell]})
                        if(cell[1] in cols.keys()):
                            cols[cell[1]].append(cell)
                        else:
                            cols.update({cell[1]:[cell]})

                # Potential fish rows need to have between 2 and set_size cells with the current value
                potential_rows = dict({})
                for row in rows.keys():
                    if(len(rows.get(row)) >= 2 and len(rows.get(row)) <= set_size):
                        potential_rows.update({row:rows.get(row)})

                # Potential fish cols need to have between 2 and set_size cells with the current value
                potential_cols = dict({})
                for col in cols.keys():
                    if(len(cols.get(col)) >= 2 and len(cols.get(col)) <= set_size):
                        potential_cols.update({col:cols.get(col)})


                fish_cells = []
                if(len(potential_rows) >= set_size):
                    # Get all columns included in potential rows
                    count = 0
                    while(len(potential_rows) > set_size and count < self.game.nn):
                        count += 1
                        cols = dict({})
                        for row in potential_rows.keys():
                            for cell in potential_rows.get(row):
                                if(cell[1] not in cols.keys()):
                                    cols.update({cell[1]:[cell]})
                                else:
                                    cols[cell[1]].append(cell)

                        # Remove rows with columns that appear only once in pattern
                        for col in cols.keys():
                            remove_rows = []
                            if(len(cols.get(col)) == 1):
                                for row in potential_rows.keys():
                                    if(cols.get(col)[0][0] == row):
                                        remove_rows.append(row)
                                for row in remove_rows:
                                    potential_rows.pop(row)

                    # If there are exactly set_size potential rows, a fish may have been found
                    if(len(potential_rows) == set_size):
                        # Get the indices of each row and column in the set
                        row_indices = []
                        col_indices = []
                        for row in potential_rows.keys():
                            for cell in potential_rows.get(row):
                                fish_cells.append(cell)
                                if(cell[0] not in row_indices):
                                    row_indices.append(cell[0])
                                if(cell[1] not in col_indices):
                                    col_indices.append(cell[1])

                        # If there are set_sizes different column and row indices, a fish was found
                        if(len(col_indices) == set_size and len(row_indices) == set_size):
                            for cell in self.options.keys():
                                # Blacklist options that are impossible
                                if(cell not in fish_cells and (cell[0] in row_indices or cell[1] in col_indices) and val in self.options.get(cell)):
                                    self.addToBlacklist(cell[0],cell[1],val)
                                    #print(f"Fish {set_size} at ",val,fish_cells)
                                    changes += 1

                if(len(potential_cols) >= set_size):
                    # Get all rows included in potential columns
                    count = 0
                    while(len(potential_cols) > set_size and count < self.game.nn):
                        count += 1
                        rows = dict({})
                        for col in potential_cols.keys():
                            for cell in potential_cols.get(col):
                                if(cell[0] not in rows.keys()):
                                    rows.update({cell[0]:[cell]})
                                else:
                                    rows[cell[0]].append(cell)

                        # Remove columns with rows that appear only once in pattern
                        for row in rows.keys():
                            if(len(rows.get(row)) == 1):
                                remove_cols = []
                                for col in potential_cols.keys():
                                    if(rows.get(row)[0][1] == col):
                                        remove_cols.append(col)
                                for col in remove_cols:
                                    potential_cols.pop(col)

                    # If there are exactly set_size potential columns, a fish may have been found
                    if(len(potential_cols) == set_size):
                        for col in potential_cols.keys():
                            row_indices = []
                            col_indices = []
                            for cell in potential_cols.get(col):
                                fish_cells.append(cell)
                                if(cell[0] not in row_indices):
                                    row_indices.append(cell[0])
                                if(cell[1] not in col_indices):
                                    col_indices.append(cell[1])

                        # If there are set_sizes different column and row indices, a fish was found
                        if(len(col_indices) == set_size and len(row_indices) == set_size):
                            for cell in self.options.keys():
                                # Blacklist options that are impossible
                                if(cell not in fish_cells and (cell[0] in row_indices or cell[1] in col_indices) and val in self.options.get(cell)):
                                    self.addToBlacklist(cell[0],cell[1],val)
                                    #print(f"Fish {set_size} at ",val,fish_cells)
                                    changes += 1

            except Exception as e:
                print(e)
        return changes

    # Find XY-Wings and blacklist impossible options
    # XY-Wing explanation: https://sudokusolver.app/xywing.html
    def xyWing(self):
        changes = 0
        self.generateOptions()
        two_val_cells = []
        # Get all cells that have only 2 options
        for cell in self.options.keys():
            if(len(self.options.get(cell)) == 2):
                two_val_cells.append(cell)

        for cell in two_val_cells:
            try:

                # Get all cells that have 2 options, are visible from pivot cell,
                # and share at least 1 value with the pivot cell
                visible_shared = []
                for comp in two_val_cells:
                    if(comp != cell and self.game.canSee(cell[0],cell[1],comp[0],comp[1])):
                        for val in self.options.get(comp):
                            if(val in self.options.get(cell)):
                                visible_shared.append(comp)

                # Get all pairs of wings that are valid XY-Wings
                valid_wing_pairs = []
                for wing in visible_shared:
                    for comp_wing in visible_shared:
                        # Get all values that show up as options within the set
                        set_values = []
                        for val in self.options.get(cell):
                            set_values.append(val)
                        for val in self.options.get(wing):
                            set_values.append(val)
                        for val in self.options.get(comp_wing):
                            set_values.append(val)

                        # If every value shows up exactly twice, the set is valid
                        valid = True
                        for val in set_values:
                            count = 0
                            for comp_val in set_values:
                                if(val == comp_val):
                                    count += 1
                            if(count != 2):
                                valid = False

                        # Add wings to list of valid pairs
                        if(valid):
                            valid_wing_pairs.append([wing,comp_wing])

                # Run for every pair
                for pair in valid_wing_pairs:
                    shared_val = 0
                    # Get the value that is shared by the wings and not the pivot cell
                    for val in self.options.get(pair[0]):
                        if(val in self.options.get(pair[1])):
                            shared_val = val

                    # If there is a shared value, blacklist impossible options
                    if(shared_val != 0):
                        for b_cell in self.options.keys():
                            # If both wings can see a cell that has their shared value as an option, it is impossible
                            if(b_cell != cell and b_cell not in pair and shared_val in self.options.get(b_cell) and self.game.canSee(pair[0][0], pair[0][1], b_cell[0], b_cell[1]) and self.game.canSee(pair[1][0], pair[1][1], b_cell[0], b_cell[1])):
                                self.addToBlacklist(b_cell[0],b_cell[1],shared_val)
                                changes += 1
                                #print(f"XY-Wing Found! Pivot {cell}, Wings {pair}")
            except Exception as e:
                print(e)
        return changes

    # Find XYZ-Wings and blacklist impossible options
    # XYZ-Wing explanation: https://www.sudokuwiki.org/XYZ_Wing
    def xyzWing(self):
        changes = 0
        self.generateOptions()
        three_val_cells = []
        two_val_cells = []

        # Get all cells that have exactly 3 options
        for cell in self.options.keys():
            if(len(self.options.get(cell)) == 3):
                three_val_cells.append(cell)

        # If there are none, an XYZ-Wing is not possible
        if(len(three_val_cells) < 1):
            return changes

        # Get all cells that have exactly 2 options
        for cell in self.options.keys():
            if(len(self.options.get(cell)) == 2):
                two_val_cells.append(cell)

        # If there are less than 2, an XYZ-Wing is not possible
        if(len(two_val_cells) < 2):
            return changes

        # Pivot cell must have 3 options
        for cell in three_val_cells:
            try:

                # Get all cells that have 2 options, are visible from pivot cell,
                # and share both values with the pivot cell
                visible_shared = []
                for comp in two_val_cells:
                    if(comp != cell and self.game.canSee(cell[0],cell[1],comp[0],comp[1])):
                        n_shared = 0
                        for val in self.options.get(comp):
                            if(val in self.options.get(cell)):
                                n_shared += 1
                            if(n_shared == 2):
                                visible_shared.append(comp)

                # Get all pairs of wings that are valid XY-Wings
                valid_wing_pairs = []
                for wing in visible_shared:
                    for comp_wing in visible_shared:
                        # Get all values that show up as options within the set
                        set_values = []
                        for val in self.options.get(cell):
                            set_values.append(val)
                        for val in self.options.get(wing):
                            set_values.append(val)
                        for val in self.options.get(comp_wing):
                            set_values.append(val)

                        # If every value shows up 2 or 3 times, a valid XYZ-Wing was found
                        valid = True
                        for val in set_values:
                            count = 0
                            for comp_val in set_values:
                                if(val == comp_val):
                                    count += 1
                            if(count not in [2,3]):
                                valid = False
                        # Add wings to list of valid pairs
                        if(valid):
                            valid_wing_pairs.append([wing,comp_wing])

                # Run for every potential wing pair
                for pair in valid_wing_pairs:
                    shared_val = 0
                    n_shared = 0
                    # Get the value that is shared by all three cells
                    for val in self.options.get(pair[0]):
                        if(val in self.options.get(pair[1]) and val in self.options.get(cell)):
                            shared_val = val
                            n_shared += 1

                    # There should be only one value shared by all 3 cells
                    if(n_shared > 1):
                        shared_val = 0

                    # If there is a shared value, blacklist impossible options
                    if(shared_val != 0):
                        for b_cell in self.options.keys():
                            # If all cells can see a cell that has their shared value as an option, it is impossible
                            if(b_cell != cell and b_cell not in pair and shared_val in self.options.get(b_cell) and self.game.canSee(pair[0][0], pair[0][1], b_cell[0], b_cell[1]) and self.game.canSee(pair[1][0], pair[1][1], b_cell[0], b_cell[1]) and self.game.canSee(cell[0],cell[1],b_cell[0],b_cell[1])):
                                #print(f"XYZ-Wing Found! Pivot {cell}, Wings {pair}, Value {shared_val}")

                                self.addToBlacklist(b_cell[0],b_cell[1],shared_val)
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
                        if(board[i][j] != 0):
                            board[i][j] = order[board[i][j]-1]
        # Ensure that the board is still legal
        test_game = sudoku(int(math.sqrt(len(board))))
        test_game.loadBoard(board)
        if(not test_game.checkLegalBoard()):
            print("Illegal Board Generated")
        return board

    # Shuffle an unsolved board
    def shuffleUnsolvedBoard(self,board):
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
                        if(board[i][j] != 0):
                            board[i][j] = order[board[i][j]-1]
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
    # Difficulty values are: -1: any, 0: easy, 1: easyish, 2: medium, 3: hardish, 4: hard, 5:very_hard
    # Larger puzzle difficulties scale upwards, but values are still the same
    def generateBoard(self,sub_size=3,difficulty=-1):
        start = datetime.now()
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

            mult = 1
            # Remove a percentage of cells at random in the beginning to cut down on runtime
            for i in range(int(nn*nn*(1-mult))):
                cell = random.choice(positions)
                board[cell[0],cell[1]] = 0
                positions.remove(cell)

            # To make easy easier, remove <= 50% of values
            if(difficulty == 0 and sub_size != 2):
                mult = .55-(1-mult)
            for i in range(int(nn*nn*mult)):

                # Choose a random cell and set its value to 0
                cell = random.choice(positions)
                original_val = board[cell[0],cell[1]]
                board[cell[0],cell[1]] = 0

                # Load the board in its current state and clear blacklist dictionary
                self.game.loadBoard(board)
                self.blacklistedOptions = dict({})
                self.options = dict({})
                self.generateOptions()

                # Check if the puzzle is solvable
                changes = 1
                while(changes != 0):

                    # Naked singles can be used for all difficulties
                    changes = self.nakedSingle()

                    # Hidden singles can only be used in puzzles with difficulties >= easyish
                    if(changes == 0 and (difficulty >= 1 or difficulty == -1)):
                        changes += self.hiddenSingle()

                    # Naked pairs can only be used in puzzles with difficulties >= medium
                    if(changes == 0 and (difficulty >= 2 or difficulty == -1)):
                        changes += self.nakedPair()

                    # Hidden pairs can only be used in puzzles with difficulties >= medium
                    if(changes == 0 and (difficulty >= 2 or difficulty == -1)):
                        changes += self.hiddenPair()

                    # Pointing pairs can only be used in puzzles with difficulties >= medium
                    if(changes == 0 and (difficulty >= 2 or difficulty == -1)):
                        changes += self.pointingPair()

                    # Naked triples can only be used in puzzles with difficulties >= hardish
                    if(changes == 0 and (difficulty >= 3 or difficulty == -1)):
                        changes += self.nakedSet(3)

                    # Naked quads can only be used in puzzles with difficulties >= hardish
                    if(changes == 0 and (difficulty >= 3 or difficulty == -1)):
                        changes += self.nakedSet(4)

                    # Naked quints and higher can only be used in puzzles with difficulties >= hard
                    for i in range(5,self.game.n*2):
                        if(changes == 0 and (difficulty >= 4 or difficulty == -1)):
                            changes += self.nakedSet(i)

                    # Hidden sets can only be used in puzzles with difficulties >= hard
                    for i in range(3,self.game.n*2):
                        if(changes == 0 and (difficulty >= 4 or difficulty == -1)):
                            changes += self.hiddenSet(i)

                    # X-Wings can only be used in puzzles with difficulties >= hard
                    if(changes == 0 and (difficulty >= 4 or difficulty == -1)):
                        changes += self.xWing()

                    # Fish patterns (>= 3) can only be used in puzzles with difficulties >= very hard
                    for i in range(3,self.game.n*2):
                        if(changes == 0 and (difficulty >= 5 or difficulty == -1)):
                            changes += self.fish(i)

                    # XY-Wings can only be used in puzzles with difficulties >= very hard
                    if(changes == 0 and (difficulty >= 5 or difficulty == -1)):
                        changes += self.xyWing()

                    # XYZ-Wings can only be used in puzzles with difficulties >= very hard
                    if(changes == 0 and (difficulty >= 5 or difficulty == -1)):
                        changes += self.xyzWing()

                # If the board is not legal and solved, revert back to the last legal board
                if(not self.game.checkLegalBoard()):
                    board[cell[0],cell[1]] = original_val
                # If the board is legal and solved, remove the cell from the list of cells
                else:
                    positions.remove(cell)

            self.game.loadBoard(board)

            # Check to ensure that the puzzle difficulty matches requirements
            generated_difficulty = self.rateDifficulty(board)
            if((difficulty == -1 or generated_difficulty == difficulty) and generated_difficulty != -1):
                done = True
            else:
                print(f"Regenerating, difficulty was {generated_difficulty}, but expected was {difficulty}")

        # Account for difficulty being any, but producing an easy puzzle by solving a portion of the puzzle before saving
        if(generated_difficulty == 0 and difficulty == -1 and sub_size != 2):
            print("Restoring values")
            full_board = self.game.board
            zeroes = []
            for i in range(nn):
                for j in range(nn):
                    if(board[i][j] == 0):
                        zeroes.append([i,j])
            if(len(zeroes) > int(nn*nn*0.5)):
                for i in range(random.randint(int(nn*nn*.15),int(nn*nn*.2))):
                    cell = random.choice(zeroes)
                    board[cell[0]][cell[1]] = full_board[cell[0]][cell[1]]

        print(generated_difficulty, f"Elapsed Time: {datetime.now()-start}")
        self.game.loadBoard(board)

        # Write the board to a file based on difficulty and subboard size
        with open(f'GeneratedBoards\\{self.getDifficultyString(sub_size,generated_difficulty)}_{sub_size}.txt', 'a') as f:
            f.write(self.game.getSaveString())
        return board

    def getDifficultyString(self, sub_size=3, difficulty_int=0):
        if(sub_size <= 3):
            diff_increase = 0
        elif(sub_size > 7):
            diff_increase = 4
        else:
            diff_increase = sub_size-3

        return ["easy", "easyish", "medium", "hardish", "hard", "very_hard", "very_very_hard", "harder_than_hard", "extremely_hard", "nearly_impossible"][difficulty_int+diff_increase]

    # Rate a puzzle's difficulty
    def rateDifficulty(self,board):
        # Keep track of the number of times a technique of each difficulty is used
        difficulty_values = [0]*6
        easy = 0
        easyish = 0
        medium = 0
        hardish = 0
        hard = 0
        very_hard = 0

        # Load board, generate options, and clear the blacklist
        self.game.loadBoard(board)
        self.options = dict({})
        self.generateOptions()
        self.blacklistedOptions = dict({})

        # Solve the board and keep track of technique difficulty usage
        changes = 1
        while(changes > 0):

            # Find naked singles
            changes = self.nakedSingle()
            if(changes > 0):
                difficulty_values[0] += 1

            # Find hidden singles
            if(changes == 0):
                changes += self.hiddenSingle()
                if(changes > 0):
                    difficulty_values[1] += 1

            # Find naked pairs
            if(changes == 0):
                changes += self.nakedPair()
                if(changes > 0):
                    difficulty_values[2] += 1

            # Find hidden pairs
            if(changes == 0):
                changes += self.hiddenPair()
                if(changes > 0):
                    difficulty_values[2] += 1

            # Find pointing pairs
            if(changes == 0):
                changes += self.pointingPair()
                if(changes > 0):
                    difficulty_values[2] += 1

            # Find naked sets up to 2*subboard size
            for i in range(3,self.game.n*2):
                if(changes == 0):
                    changes += self.nakedSet(i)
                    if(changes > 0):
                        if(i > 4):
                            difficulty_values[4] += 1
                        else:
                            difficulty_values[3] += 1

            # Find hidden sets up to 2*subboard size
            for i in range(3,self.game.n*2):
                if(changes == 0):
                    changes += self.hiddenSet(i)
                    if(changes > 0):
                        difficulty_values[4] += 1

            # Find X-Wings
            if(changes == 0):
                changes += self.xWing()
                if(changes > 0):
                    difficulty_values[4] += 1

            # Find fish patterns
            for i in range(3,self.game.n*2):
                if(changes == 0):
                    changes += self.fish(i)
                    if(changes > 0):
                        difficulty_values[5] += 1

            # Find XY-Wings
            if(changes == 0):
                changes += self.xyWing()
                if(changes > 0):
                    difficulty_values[5] += 1

            # Find XYZ-Wings
            if(changes == 0):
                changes += self.xyzWing()
                if(changes > 0):
                    difficulty_values[5] += 1

        print(difficulty_values)
        max_non_zero = 0
        for i in range(len(difficulty_values)):
            if(difficulty_values[i] > 0):
                max_non_zero = i

        # Return calculated difficulty
        if(self.game.checkLegalBoard()):
            return max_non_zero
        else:
            return -1

    # Generate multiple boards
    def generateNBoards(self,n,sub_size=3,difficulty="any"):
        for i in range(n):
            self.generateBoard(sub_size,difficulty)

    # Run solver
    def solve(self):
        start_time = datetime.now()
        total_changes = 0
        changes = 1
        self.blacklistedOptions = dict({})
        self.options = dict({})
        self.generateOptions()
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

            # Try all realistic naked sets for the board size
            for i in range(3,self.game.n*2):
                if(changes == 0):
                    changes += self.nakedSet(i)

            # Try all realistic hidden sets for the board size
            for i in range(3,self.game.n*2):
                if(changes == 0):
                    changes += self.hiddenSet(i)

            if(changes == 0):
                changes += self.xWing()

            # Try all realistic fish patterns for the board size
            for i in range(3,self.game.n*2):
                if(changes == 0):
                    changes += self.fish(i)

            if(changes == 0):
                changes += self.xyWing()

            if(changes == 0):
                changes += self.xyzWing()

            total_changes += changes

        # Output board in final state and whether it is solved or not
        print()
        print(f"Total Changes: {total_changes}")
        if(self.game.checkLegalBoard()):
            print("Solved")
            print("Time to solve:",datetime.now()-start_time) # Show time to complete puzzle
        else:
            print("Unsolved")
