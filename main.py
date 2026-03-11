"""
CISC455/851 Group Project - EA for 9x9 Sudoku
"""

# 0s are designated as "empty" spots, they need to be filled in by the EA with 1-9 values
DEFAULT_PUZZLE = (
    "530070000"
    "600195000"
    "098000060"
    "800060003"
    "400803001"
    "700020006"
    "060000280"
    "000419005"
    "000080079"
)

"""
Evaluation Methods
"""

def row_conflicts(grid):
    conflicts = 0
    for row in grid:
        conflicts = conflicts + (9 - len(set(row)))
    return conflicts

def col_conflicts(grid):
    conflicts = 0
    for col in range(0, 9):
        values = []
        for row in range(0, 9):
            values.append(grid[row][col])
        conflicts = conflicts + (9 - len(set(values)))
    return conflicts

def box_conflicts(grid):
    conflicts = 0
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            values = []
            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    values.append(grid[row][col])
            conflicts = conflicts + (9 - len(set(values)))
    return conflicts

def fitness_sudoku(individual):
    """Compute fitness of an individual for Sudoku (maximization)."""
    max_score = 243 # 27 groups (9 rows, 9 cols, 9 boxes) * 9 max points each
    violations = row_conflicts(individual) + col_conflicts(individual) + box_conflicts(individual)
    return max_score - violations

"""
Puzzle helpers
"""

def parse_puzzle(puzzle):
    digits = [ch for ch in puzzle if ch.isdigit()]
    if len(digits) != 81:
        raise ValueError("Puzzle must contain exactly 81 digits.")

    grid = []
    for i in range(0, 81, 9):
        row = []
        for value in digits[i:i + 9]:
            row.append(int(value))
        grid.append(row)
    return grid

def fixed_mask(given_grid):
    mask = []
    for row in range(0, 9):
        mask_row = []
        for col in range(0, 9):
            mask_row.append(given_grid[row][col] != 0)
        mask.append(mask_row)
    return mask

"""
Initialization methods
"""

def sudoku_population(pop_size, given_grid):
    """Initialize a population of Sudoku candidates."""

    population = []

    return population

"""
Mutation methods
"""

def sudoku_swap(individual, mask):
    """Swap two mutable values in one row."""

    mutant = []

    return mutant

"""
Recombination methods
"""

def sudoku_row_crossover(parent1, parent2):
    offspring1 = []
    offspring2 = []

    return offspring1, offspring2

"""
Parent selection methods
"""

def tournament(fitness, mating_pool_size, tournament_size):
    selected_to_mate = []

    return selected_to_mate

"""
Survivor selection methods
"""

def sort_population(population, fitness):
    sorted_pop = []
    sorted_fit = []

    return sorted_pop, sorted_fit

def replacement(current_pop, current_fitness, offspring, offspring_fitness):
    population = []
    fitness = []

    return population, fitness

def print_grid(grid):
    print("=====================")
    for row in range(0, 9):
        if row > 0 and row % 3 == 0:
            print("------+-------+------")
        line = []
        for col in range(0, 9):
            if col > 0 and col % 3 == 0:
                line.append("|")
            line.append(str(grid[row][col]))
        print(" ".join(line))
    print("=====================")

"""
An evolutionary algorithm for the Sudoku puzzle
"""

def main():
    puzzle = DEFAULT_PUZZLE
    given_grid = parse_puzzle(puzzle) # reads puzzle string into a 2D list of integers
    mask = fixed_mask(given_grid) # converts grid to a mask of true false, with values that are 0 taking the value of false, as they are modifiable by the EA

    print_grid(given_grid)
    print_grid(mask)

    # with the default puzzle the printout below doesn't really make sense, since it is evaluating 0s as part of the
    # actual solution; the first generation would fill in the 0s with actual values
    fitness = fitness_sudoku(given_grid)
    print(f"Initial fitness: {fitness}")

if __name__ == "__main__":
    main()