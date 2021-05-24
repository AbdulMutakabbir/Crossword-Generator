# Crossword-Generator
Applying Constraint Satisfaction along with Greedy Search to Optimizes and generate Crossword puzzle form an input of word list and structure.

# Introduction
How might you go about generating a crossword puzzle? Given the structure of a crossword puzzle, and a list of words to use, the problem becomes one of choosing which words should go in each vertical or horizontal sequence of squares. I can model this sort of problem as a constraint satisfaction problem. Each sequence of squares is one variable, for which we need to decide on its value.

# Usage 
```
> Clone the Git Reposoratory
> cd into "Crossword-Generator" directory
> Add word list and crossword structure as needed or use the smaples already preasent.
> pip install requirements.py
> python generate.py <path-to-crossword-structure> <path-to-word-list> <output-file-name>
```

# Output 
![crossword](https://github.com/AbdulMutakabbir/Crossword-Generator/blob/main/output.png)

# Technologies
* python
* pillow
