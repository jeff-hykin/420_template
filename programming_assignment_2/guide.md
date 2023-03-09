Notes:
- **Submission instructions**: same as pa1, but push the `pa2` tag.

    (Sorry this wasn't mentioned in the PDF)
- **Asking for help**: 
  *Everyone is bad at debugging pa2, including people who've done the assignment before like myself*. The assignment is inheriently hard to debug.
                                   ⬞
I will list all the useful tips I have below.

Tips:
- #### Quick forms of debugging
  `print()` and debuggers generally do not work well/quickly on this assignment.
                                   ⬞
     
   Some worthwhile alternatives:
    1. Mini-tests; check the base cases. For example, create a `evaluate_board(depth, board)` function that returns `None` if the game isn't over, `0` if the board shows a tie, and `1 * depth` if X wins. Its surprisingly easy to screw up the easy things, so  prove that it works with test cases:
        - `assert 1    == evaluate_board(0, [['X','X','X'],['.','.','.'],['.','.','.'],])`
        - `assert 0.1  == evaluate_board(9, [['X','X','X'],['.','.','.'],['.','.','.'],])`
        - `assert None == evaluate_board(9, [['X','.','X'],['.','.','.'],['.','.','.'],])`
    2. I know it sounds dumb/basic but often reading over the code and try to find off-by-one scenarios works.
        - Does the game alternate min/max and X/O
        - Does the initial value work correctly
- #### Powerful Debugging

   If you're really stuck, try this.
                                  ⬞
   1. Download this [output_reference.txt](https://45-79-48-20.ip.linodeusercontent.com/s/Qf5RzMbP3E7tzCB) file
   2. `pip install blissful-basics`

       (sorry I'm biased to Python over C++)
   3. Add 7 lines to your ttt.py (pseudo-example below)
   ```py
   from blissful_basics import print  # <- ADD THIS
   

   ... # <your stuff>


   @print.indent.function  # <- ADD THIS
   def min_score(...):

       print(YOUR_GAME_BOARD)     # <- ADD THIS
       print(SCORE_RELATIVE_TO_X) # <- ADD THIS

       ... # <your stuff>


   ... # <your stuff>


   @print.indent.function  # <- ADD THIS
   def max_score(...):

       print(YOUR_GAME_BOARD)     # <- ADD THIS
       print(SCORE_RELATIVE_TO_X) # <- ADD THIS

       ... # <your stuff>


   ... # your stuff
    ```
    4. Now you want to run your program, `Choose X` and dump all the output to a file.

       On Linux/Mac that can be done with the following command:
       ```sh
       echo 'Choose X
       ' | python ./ttt.py > output.txt
       ```
       (Its not a mistake that its two lines)
   5. Compare that^ output file with the one you downloaded
      **NOTE:** Just because your output is different does not mean it is wrong.
      For example: if, for some reason, your algorithm defaults looks left-to-right instead of right-to-left when trying to find an available move, then your output will be entirely different.
                                  ⬞
      The reference output was generated looking for open spaces by first doing left-to-right, then trying top-to-bottom (And if this is still unclear, look at the reference output and you'll probably see what I mean)