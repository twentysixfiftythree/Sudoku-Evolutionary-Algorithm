"""
CISC455/851 Group Project - EA for 9x9 Sudoku
"""

# 0s are designated as "empty" spots, they need to be filled in by the EA with 1-9 values
import random
import operator

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

    for _ in range(pop_size):
        candidate = []

        for row in range(9):
            new_row = given_grid[row].copy()

            # numbers already used in the row
            used = [x for x in new_row if x != 0]

            # numbers missing from the row
            missing = [x for x in range(1, 10) if x not in used]

            random.shuffle(missing)

            idx = 0
            for col in range(9):
                if new_row[col] == 0:
                    new_row[col] = missing[idx]
                    idx += 1

            candidate.append(new_row)

        population.append(candidate)

    return population

"""
Mutation methods
"""

def sudoku_swap(individual, mask):
    """Swap two mutable values in one row."""
    mutant = [row.copy() for row in individual]

    # find rows that have at least 2 mutable cells
    valid_rows = []
    for r in range(9):
        mutable_cols = [c for c in range(9) if not mask[r][c]]
        if len(mutable_cols) >= 2:
            valid_rows.append((r, mutable_cols))

    # nothing to mutate
    if not valid_rows:
        return mutant

    # pick one row, then swap 2 mutable positions
    row, mutable_cols = random.choice(valid_rows)
    c1, c2 = random.sample(mutable_cols, 2)

    mutant[row][c1], mutant[row][c2] = mutant[row][c2], mutant[row][c1]

    return mutant

"""
Recombination methods
"""

def sudoku_row_crossover(parent1, parent2):
    point = random.randint(1, 8)

    offspring1 = []
    offspring2 = []

    for r in range(point):
        offspring1.append(parent1[r].copy())
        offspring2.append(parent2[r].copy())

    for r in range(point, 9):
        offspring1.append(parent2[r].copy())
        offspring2.append(parent1[r].copy())

    return offspring1, offspring2

"""
Parent selection methods
"""

def tournament(fitness, mating_pool_size, tournament_size):
    """Tournament selection"""
    selected_to_mate = []

    while len(selected_to_mate) < mating_pool_size:

        # pick random individuals for the tournament
        competitors = random.sample(range(len(fitness)), tournament_size)

        # find the best among them
        best = competitors[0]
        for idx in competitors:
            if fitness[idx] > fitness[best]:
                best = idx

        # add winner to mating pool
        selected_to_mate.append(best)

    return selected_to_mate

"""
Survivor selection methods
"""

def sort_population(population, fitness):
    pop_fit_pair = list(map(list, zip(population, fitness)))
    pop_fit_pair.sort(key=operator.itemgetter(1), reverse=True)

    sorted_pop = []
    sorted_fit = []

    for entry in pop_fit_pair:
        sorted_pop.append(entry[0])
        sorted_fit.append(entry[1])

    return sorted_pop, sorted_fit

def replacement(current_pop, current_fitness, offspring, offspring_fitness):
    """Offspring replace the worst individuals in the current generation."""
    population = []
    fitness = []

    sorted_pop, sorted_fit = sort_population(current_pop.copy(), current_fitness.copy())
    k = len(current_pop) - len(offspring)  # number of elites to keep

    # keep top-k from current population
    for i in range(0, k):
        population.append(sorted_pop[i])
        fitness.append(sorted_fit[i])

    # add all offspring
    for j in range(0, len(offspring)):
        population.append(offspring[j])
        fitness.append(offspring_fitness[j])

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
    random.seed()

    puzzle = DEFAULT_PUZZLE
    given_grid = parse_puzzle(puzzle) # reads puzzle string into a 2D list of integers
    mask = fixed_mask(given_grid) # converts grid to a mask of true false, with values that are 0 taking the value of false, as they are modifiable by the EA

    print("Given puzzle:")
    print_grid(given_grid)

    # EA parameters
    popsize = 1000
    mating_pool_size = 500  # keep even so parents pair cleanly
    tournament_size = 2
    xover_rate = 0.65
    mut_rate = 0.85
    gen_limit = 1000

    # initialize population
    gen = 0
    population = sudoku_population(popsize, given_grid)
    fitness = []
    for i in range(0, popsize):
        fitness.append(fitness_sudoku(population[i]))

    print("generation", gen, ": best fitness", max(fitness),
          "average fitness", round(sum(fitness) / len(fitness), 2))

    # evolution begins
    while gen < gen_limit and max(fitness) < 243:
        parents_index = tournament(fitness, mating_pool_size, tournament_size)
        random.shuffle(parents_index)

        offspring = []
        offspring_fitness = []

        # pair parents safely: (0,1), (2,3), ...
        for i in range(0, len(parents_index) - 1, 2):
            p1 = population[parents_index[i]]
            p2 = population[parents_index[i + 1]]

            # recombination
            if random.random() < xover_rate:
                off1, off2 = sudoku_row_crossover(p1, p2)
            else:
                off1 = [row.copy() for row in p1]
                off2 = [row.copy() for row in p2]

            # mutation
            if random.random() < mut_rate:
                off1 = sudoku_swap(off1, mask)
            if random.random() < mut_rate:
                off2 = sudoku_swap(off2, mask)

            offspring.append(off1)
            offspring_fitness.append(fitness_sudoku(off1))
            offspring.append(off2)
            offspring_fitness.append(fitness_sudoku(off2))

        # survivor selection
        population, fitness = replacement(population, fitness, offspring, offspring_fitness)

        gen = gen + 1
        print("generation", gen, ": best fitness", max(fitness),
              "average fitness", round(sum(fitness) / len(fitness), 2))

    # print best candidate found
    best_index = fitness.index(max(fitness))
    best = population[best_index]
    best_fit = fitness[best_index]

    print("\nBest candidate after evolution:")
    print_grid(best)
    print("fitness:", best_fit)
    print("total conflicts:", 243 - best_fit)
    print("generations:", gen)

if __name__ == "__main__":
    main()