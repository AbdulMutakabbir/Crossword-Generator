import sys
import copy

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        # init domain variable to a copy of self.domains
        domains = copy.deepcopy(self.domains)

        # enforce domain consistency by looping over variables
        for variable in domains:
            # init variable length
            variable_length = variable.length

            # loop over words in variable domain
            for word in domains[variable]:
                # remove the words whose length is not equal to variables length
                if len(word) != variable_length:
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        # init revised_flag as False
        revised_flag = False

        # init domain variable as a copy of self.domains
        domains = copy.deepcopy(self.domains)

        # init overlap
        overlap = self.crossword.overlaps[x, y]

        # check for overlap
        if overlap is not None:
            # get cell positions
            x_cell_position = overlap[0]        # x overlapping cell
            y_cell_position = overlap[1]        # y overlapping cell

            # loop over words in x's domain
            for x_word in domains[x]:

                # init same_letter_flag to True
                same_letter_flag = False

                # loop over words in y's domain
                for y_word in domains[y]:

                    # check if the letter match in overlapping position
                    if x_word[x_cell_position] == y_word[y_cell_position]:
                        # if true
                        # mark revised_flag as true
                        # mark same_letter_flag as True
                        # break the loop since the word should be there in domain
                        same_letter_flag = True
                        revised_flag = True
                        break

                # revised_flag is False
                # remove the word from the domain of "X" since that is not a possible value for that domain
                if not same_letter_flag:
                    self.domains[x].remove(x_word)

        # return False if no overlap
        else:
            return revised_flag

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # init queue as arcs
        queue = arcs

        # if queue is None, initial list of all arcs in the problem
        if queue is None:
            # assign empty array to queue
            queue = []

            # init domains as self.domains
            domains = self.domains

            # loop over all the variables
            for variable in domains:
                # init neighbouring variables
                neighbouring_variables = self.crossword.neighbors(variable)

                # loop over neighbours
                for neighbour_variable in neighbouring_variables:
                    # init overlap
                    overlap = self.crossword.overlaps[variable,neighbour_variable]

                    # if overlap append to queue
                    if overlap is not None:
                        queue.append((variable, neighbour_variable))

        # Apply AC-3 algorithm
        while len(queue) != 0:
            # Dequeue
            variable_x, variable_y = queue.pop()

            # init revised
            revised = self.revise(variable_x,variable_y)

            # check revised
            if revised:
                # if domain of x is empty return False
                if len(self.domains[variable_x]) == 0:
                    return False

                # init neighbours
                neighbours = self.crossword.neighbors(variable_x)

                # enqueue (neighbour, x) each neighbour in domain x.neighbours - y
                for neighbour in neighbours:
                    if neighbour != variable_y:
                        queue.append((neighbour, variable_x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        # Check for assignments
        for variable in self.domains:
            # if variable is not in assignment return False
            if variable not in assignment:
                return False

        # assignment is complete return True
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # check if all values are distinct
        values = set(assignment.values())           # init values as a set consisting values of assignment
        if len(assignment) != len(values):
            return False

        # check if every value is the correct length
        for variable in assignment:
            if len(assignment[variable]) != variable.length:
                return False

        # check if there are any conflicts between neighbouring variables
        # if the neighbour is assigned and the overlap has the same value then true
        for variable in assignment:
            neighbours = self.crossword.neighbors(variable)
            for neighbour in neighbours:
                if neighbour in assignment:
                    overlap = self.crossword.overlaps[variable, neighbour]
                    char_variable = assignment[variable][overlap[0]]
                    char_neighbour = assignment[neighbour][overlap[1]]
                    if char_variable != char_neighbour:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # init domain
        var_domain = self.domains[var]

        # init neighbours
        neighbours = self.crossword.neighbors(var)

        # init assigned_words as array of values of assignment
        assigned_words = list(assignment.values())

        # init variable_heuristic_dictionary
        variable_heuristic_dictionary = {}
        for word in var_domain:
            variable_heuristic_dictionary[word] = 0

        # loop over neighbours and increment the count of words in neighbours domain and variable domain
        for neighbour in neighbours:
            for word in var_domain:
                if word in self.domains[neighbour] and word not in assigned_words:
                    variable_heuristic_dictionary[word] += 1

        # Sort the list of words in ascending order
        sorted_words = list(dict(sorted(variable_heuristic_dictionary.items(), key=lambda val: val[1])).keys())

        # return sorted list
        return sorted_words

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # init possible_variable as empty dictionary
        possible_variables = {}

        # loop over self.domains
        for variable in self.domains:
            # if variable not in assignment push (count of remaining variable, neighbours count) in possible_variables
            if variable not in assignment:
                remaining_values_count = len(self.domains[variable])
                neighbours_count = len(self.crossword.neighbors(variable))
                possible_variables[variable] = (remaining_values_count, neighbours_count)

        # sort possible variable
        sorted_variables = sorted(possible_variables.items(), key=lambda var: (var[1][0], var[1][1]))

        # return minimum heuristic value variable
        return sorted_variables[0][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # check if assignment is complete
        assignment_completed = self.assignment_complete(assignment)

        # if completed return assignment
        if assignment_completed:
            return assignment

        # select an unassigned variable
        variable = self.select_unassigned_variable(assignment)

        # loop over words in variable domain
        for word in self.order_domain_values(variable, assignment):

            # assign value to assignment
            assignment[variable] = word

            # check if value is consistent
            if self.consistent(assignment):
                # recursively call backtracking
                result = self.backtrack(assignment)

                # check if result is not a failure
                if result is not None:
                    # return result
                    return result

            # remove value from assignment
            assignment.pop(variable)

        # return failure
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
