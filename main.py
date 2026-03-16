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
        candidate = [row.copy() for row in given_grid]

        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):

                present = []
                empty = []

                for r in range(box_row, box_row+3):
                    for c in range(box_col, box_col+3):
                        if candidate[r][c] != 0:
                            present.append(candidate[r][c])
                        else:
                            empty.append((r,c))

                missing = [x for x in range(1,10) if x not in present]
                random.shuffle(missing)

                for i,(r,c) in enumerate(empty):
                    candidate[r][c] = missing[i]

        population.append(candidate)

    return population

"""
Mutation methods
"""

def sudoku_swap(individual, mask):
    """Mutation: swap two mutable values in a row that contains conflicts."""

    # Copy individual so original candidate is not modified
    mutant = [row.copy() for row in individual]

    conflict_rows = []

    # Identify rows that currently violate Sudoku constraints (duplicates)
    for r in range(9):
        if len(set(mutant[r])) < 9:
            conflict_rows.append(r)

    if not conflict_rows:
        return mutant

    r = random.choice(conflict_rows)

    # Only swap cells that were not fixed in the original puzzle
    mutable = [c for c in range(9) if not mask[r][c]]

    if len(mutable) < 2:
        return mutant

    # Swap two mutable positions to introduce variation
    c1, c2 = random.sample(mutable, 2)

    mutant[r][c1], mutant[r][c2] = mutant[r][c2], mutant[r][c1]

    return mutant

"""
Recombination methods
"""

def sudoku_row_crossover(parent1, parent2):
    """Crossover: exchange a random 3x3 box between parents."""

    offspring1 = [row.copy() for row in parent1]
    offspring2 = [row.copy() for row in parent2]

    # Choose a random 3x3 box
    box = random.randint(0, 8)

    box_row = (box // 3) * 3
    box_col = (box % 3) * 3

    # Swap all values inside the selected box
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            offspring1[r][c] = parent2[r][c]
            offspring2[r][c] = parent1[r][c]

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
    """Survivor selection that preserves diversity."""

    combined_pop = current_pop + offspring
    combined_fit = current_fitness + offspring_fitness

    # sort by fitness (best first)
    pop_fit = list(zip(combined_pop, combined_fit))
    pop_fit.sort(key=lambda x: x[1], reverse=True)

    new_population = []
    new_fitness = []

    seen = set()

    for individual, fit in pop_fit:
        key = tuple(tuple(row) for row in individual)

        # avoid duplicates to keep population diverse
        if key not in seen:
            new_population.append(individual)
            new_fitness.append(fit)
            seen.add(key)

        if len(new_population) == len(current_pop):
            break

    return new_population, new_fitness

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
    
    best_seen = max(fitness)
    stagnation = 0

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

        # check improvement
        current_best = max(fitness)

        if current_best > best_seen:
            best_seen = current_best
            stagnation = 0
        else:
            stagnation += 1

        # restart if stuck
        if stagnation > 100:
            print("Restarting population due to stagnation...")
            population = sudoku_population(popsize, given_grid)
            fitness = [fitness_sudoku(ind) for ind in population]
            stagnation = 0

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