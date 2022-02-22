from sudoku import sudoku
from solver import solver
import os
import numpy as np
import math
import random

# Load and generate a puzzle from a template
def genPuzzle(difficulty="any",sub_size=3):
    """Generate a sudoku puzzle of a specified difficulty and subboard dimensions"""
    # Assign random difficulty chosen from existing templates
    if(difficulty == "any"):
        path = os.listdir("GeneratedBoards")
        possible_difficulties = []
        for entry in path:
            # If the file matches the specified subboard size, add difficulty to options
            if("." in str(entry) and str(entry).split("_")[1].split(".")[0] == str(sub_size)):
                possible_difficulties.append(str(entry).split("_")[0])
        # Choose a random difficulty from the available options if possible
        if(len(possible_difficulties) > 0):
            difficulty = random.choice(possible_difficulties)
        else:
            print("There are no templates for this board size")
            return

    # Get filepath that corresponds to puzzle specifications
    path = os.listdir("GeneratedBoards");
    filepath = ""
    for entry in path:
        if(str(entry) == f"{difficulty}_{sub_size}.txt"):
            filepath = f"GeneratedBoards\\{difficulty}_{sub_size}.txt"
    if(filepath == ""):
        print("There are no templates for this board size and difficulty")
        return

    # Select a random board save string from the chosen file
    f = open(filepath, "r")
    lines = list(f.readlines())
    board_string = random.choice(lines)

    # Load and shuffle the board template
    s = solver(sudoku(sub_size))
    s.game.loadSaveString(board_string)
    board = s.shuffleUnsolvedBoard(s.game.board)

    # Generate the board into a PDF
    docGen(board,difficulty)

# Create PDF of board using LaTeX
def docGen(board,difficulty):
    """Generate PDF of a specified board and difficulty label"""
    nn = len(board)
    n = int(math.sqrt(nn))

    # Document header
    doc = r"\documentclass[" + str(10/nn) + r"""pt]{article}
            \usepackage[pdftex,active,tightpage]{preview}

            \usepackage{tikz}
            \usetikzlibrary{matrix}
            \PreviewEnvironment{tikzpicture}
            \renewcommand{\familydefault}{\sfdefault}
            \usepackage{anyfontsize}


            \begin{document}
            \begin{tikzpicture}[inner sep=1,outer sep=1]
            \begin{scope}""".lstrip()

    # Grids that make up the empty board
    doc += f"\draw[step={10/nn},align=center] (0,0) grid (10,10);"
    doc += f"\draw[step={10/n},align=center,very thick] (0,0) grid (10,10);"

    # Adding values into the board as a matrix
    if(nn in [49]):
        doc += r"\matrix[matrix of nodes,nodes={inner sep=0pt,text width=" + str(10/nn) + "cm,align=center,minimum height=" + str(10/nn) + "cm}] at (" + str(5) + ", " + str(5) + "){"
    elif(nn in [36]):
        doc += r"\matrix[matrix of nodes,nodes={inner sep=0pt,text width=" + str(10/nn) + "cm,align=center,minimum height=" + str(10/nn*.97) + "cm}] at (" + str(5) + ", " + str(5) + "){"
    elif(nn in [16,25]):
        doc += r"\matrix[matrix of nodes,nodes={inner sep=0pt,text width=" + str(10/nn) + "cm,align=center,minimum height=" + str(10/nn*.99) + "cm}] at (" + str(5) + ", " + str(5) + "){"
    else:
        doc += r"\matrix[matrix of nodes,nodes={inner sep=0pt,text width=" + str(10/nn) + "cm,align=center,minimum height=" + str(10/nn) + "cm}] at (" + str(5) + ", " + str(5) + "){"

    # Setting font size to fit cells
    font_size = 30-(n-2)*10
    # Minimum font size
    if(font_size <= 0):
        if(nn > 36):
            font_size = 4
        else:
            font_size = 5

    # Populate the board
    for i in range(nn):
        row = ""
        for j in range(nn):
            if(board[i][j] == 0):
                # Display white 0 for empty spot so that it is not visible, but a space is taken up
                row += r"\color{white}{\fontsize{" + str(font_size) + r"pt}{" + str(font_size) + r"pt}\selectfont 0}"
            else:
                # Use different character sets so that puzzle is not multiple numeric digits
                if(nn >= 16):
                    if(nn > 36):
                        row += r"\color{black}{\fontsize{" + str(font_size) + r"pt}{" + str(font_size) + r"pt}\selectfont " + str(board[i][j]) + "}"
                    elif(board[i][j]-1 > 9):
                        row += r"\color{black}{\fontsize{" + str(font_size) + r"pt}{" + str(font_size) + r"pt}\selectfont " + str(chr(board[i][j]+54)) + "}"
                    elif(board[i][j]-1 >= 34):
                        row += r"\color{black}{\fontsize{" + str(font_size) + r"pt}{" + str(font_size) + r"pt}\selectfont " + str(chr(board[i][j]+54+6)) + "}"
                    else:
                        row += r"\color{black}{\fontsize{" + str(font_size) + r"pt}{" + str(font_size) + r"pt}\selectfont " + str(board[i][j]-1) + "}"
                else:
                    row += r"\color{black}{\fontsize{" + str(font_size) + r"pt}{" + str(font_size) + r"pt}\selectfont " + str(board[i][j]) + "}"

            # Append necessary syntaxes
            if(j != nn-1):
                row += " & "
            else:
                row += r"\\"
        doc += row
    doc += "};"

    # End document
    doc += r"""\end{scope}
                \end{tikzpicture}
                \end{document}""".lstrip()

    # Create appropriate directories if necessary
    count = 0
    folder_exists = False
    final_path = f"GeneratedBoards\\Documents\\{nn}x{nn}\\" + difficulty.title().replace("_","")
    for entry in os.listdir("GeneratedBoards\\Documents"):

        if(entry == f"{nn}x{nn}"):
            for i in os.listdir(f"GeneratedBoards\\Documents\\{nn}x{nn}"):
                if(i == difficulty.title().replace("_","")):
                    folder_exists = True
            if(not folder_exists):
                os.system(f"mkdir {final_path}")
                folder_exists = True

    # Create directories if no directories for the puzzle specifications exist
    if(not folder_exists):
        os.system(f"mkdir GeneratedBoards\\Documents\\{nn}x{nn}")
        os.system(f"mkdir {final_path}")

    # Number of boards of the same difficulty and type
    count = len(os.listdir(final_path))

    # Write LaTeX code to the appropriate .tex file
    with open(f"{final_path}\\{difficulty}_{nn}_{count}_template.tex", "w+") as f:
        f.write(doc)

    # Generate and output the PDF
    os.system(f"pdflatex -output-directory={final_path} {final_path}\\{difficulty}_{nn}_{count}_template.tex")

    # LaTeX 2: Electric Boogaloo
    # Formatting was very challenging with the original LaTeX code, so this code
    # embeds the previously generated PDF and formats it nicely.
    # Credit to Ethan Hawk for helping to figure out this workaround
    doc=r"""\documentclass{article}
    \usepackage{pdfpages}
    \usepackage{anyfontsize}

    \linespread{1.8}
    \renewcommand{\familydefault}{\sfdefault}
    \usepackage[%
        left=0.50in,%
        right=0.50in,%
        top=1in,%
        bottom=""".lstrip()

    if(nn > 36):
        bottom_margin = .5
    else:
        bottom_margin = .7

    doc += str(bottom_margin) + r"""in,%
        paperheight=11in,%
        paperwidth=8.5in%
    ]{geometry}%
    \begin{document}
    \begin{center}""".lstrip()

    # Add board size and difficulty at top of page
    doc += r"{\fontsize{36pt}{36pt}\selectfont "
    if(nn != 9):
        doc += str(nn) + "x" + str(nn) + " "
    doc += r"SUDOKU} \\ {\fontsize{24pt}{24pt}\selectfont " + difficulty.upper().replace("_"," ")

    # Add bottom text of how to play and what characters to use
    doc += r"} \linespread{1} \mbox{} \vfill {\fontsize{10pt}{10pt}\selectfont EVERY ROW, COLUMN AND HOUSE MUST HAVE EXACTLY ONE OF EACH OF THE FOLLOWING VALUES} \\ {\fontsize{10pt}{10pt}\selectfont "
    for i in range(nn):
        if(nn <= 9):
            doc += str(i+1) + ", "
        elif(nn >= 16):
            if(nn > 36):
                doc += str(i+1) + ", "
            elif(i > 9):
                doc += str(chr(i+55)) + ", "
            else:
                doc += str(i) + ", "

    # Remove extra comma
    doc = doc[:-2]

    # Begin the minipage so that embedded PDF and text can be on the same page
    doc += r"}\end{center} \begin{minipage}[t]{\linewidth}".lstrip()

    # Embed PDF
    doc += r"\includepdf[pages=1,templatesize={4.5in}{4.5in}]{GeneratedBoards/Documents/" + str(nn) + "x" + str(nn) + r"/" + difficulty.title().replace("_","") + r"/" + f"{difficulty}_{nn}_{count}_template.pdf" + r"}\end{minipage} \end{document}"

    # Write LaTeX code to the appropriate .tex file
    with open(f"{final_path}\\{difficulty}_{nn}_{count}.tex", "w+") as f:
        f.write(doc)

    # Generate and output the PDF
    os.system(f"pdflatex -output-directory={final_path} {final_path}\\{difficulty}_{nn}_{count}.tex")

    # Clean up output so that only PDF remains
    path = os.listdir(final_path)
    for entry in path:
        if(not entry.endswith(".pdf") or entry.endswith("template.pdf")):
            p = os.path.join(final_path, entry)
            os.remove(p)

if __name__ == '__main__':
    for j in range(5):
        genPuzzle("very_very_hard",6)
