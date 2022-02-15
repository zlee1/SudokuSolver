# Sudoku Solver

This sudoku solver was built with the intention of being used to generate sudoku boards. Because of this, a simple "brute force" methodology was not feasible. Therefore, the solver uses logic and sudoku techniques to solve puzzles. Different solving techniques have been built in, including naked singles, hidden singles, naked pairs, naked triples, x-wings, swordfish, xy-wings, xyz-wings, and more. Using these techniques, the solver is able to generate legal sudoku boards and gauge their difficulty. A puzzle that requires the use of the jellyfish technique (one of the hardest techniques included), for example, is far harder than one that only contains naked and hidden singles (the easiest techniques included).

This project also generates sudoku puzzles of varying sizes. It can produce the standard 9x9 sudoku puzzles, but also 4x4s, 16x16s, 25x25s, and so on. Theoretically, any puzzle can be produced as long as its dimensions are perfect squares (although very large puzzles will take quite a while to generate). Included in the "GeneratedBoards" folder is a collection of text files that contain strings which can be loaded into the sudoku solver. The text files are named in the format <difficulty>_<subboard_size>.txt. Meaning an easy 9x9 sudoku puzzle will have the name "easy_3.txt" because 3 is the dimension for the subboards within the puzzle.

The file "docgen.py" utilizes LaTeX to produce PDFs of boards. Specifying a difficulty and size will find a board string that matches the given parameters and then turn it into a PDF that can be easily printed or distributed.

Sudoku board generation is available in the "run.py" file, and allows utilization of multiprocessing to generate large quantities of sudoku boards as fast as possible. Providing a difficulty will restrict the techniques that can be used for the puzzle and will not allow the generator to return a puzzle that does not match the specified difficulty. It is recommended to set the difficulty to "-1", which means that any difficulty is accepted unless you are specifically wanting an easy puzzle. Generation time will be faster for lower difficulties because it take less computing time on complicated techniques, but also is more likely to produce a puzzle that meets requirements. Puzzle difficulties can be between -1 and 5 inclusively and will be saved as the appropriate text file. Since difficulty changes based on board size as well as technique, the text version of the difficulty will be different for each board. A difficulty of 0 on a 9x9 board corresponds to an "easy" difficulty, but a difficulty of 0 on a 16x16 board corresponds to an "easyish" difficulty. The full difficulty layout is as follows:

  4x4: easy (it is not possible to produce harder puzzles that follow rules of sudoku)
  9x9: easy, easyish, medium, hardish, hard, very hard
  16x16: easyish, medium, hardish, hard, very hard, very very hard
  25x25: medium, hardish, hard, very hard, very very hard, harder than hard
  36x36: hardish, hard, very hard, very very hard, harder than hard, extremely hard
  49x49: hard, very hard, very very hard, harder than hard, extremely hard, near-impossible

Board generation for dimensions higher than 49x49 is not recommended, as the LaTeX code does not handle it well, and the difficulties do not extend past "near-impossible".

Feel free to contact me with questions at zack.lee@valpo.edu.
