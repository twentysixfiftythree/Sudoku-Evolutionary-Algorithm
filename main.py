"""
CISC455/851 Group Project - EA for 9x9 Sudoku
"""

# 0s are designated as "empty" spots, they need to be filled in by the EA with 1-9 values
import random

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
    # Included for completeness, though box validity is mostly preserved by representation.
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
    """Mutation: swap two mutable values in one 3x3 box.

    Preference: choose a box that contains row/column conflicts, so the swap is useful.
    Fallback: choose any box with at least two mutable cells.
    """
    # Copy individual so the original candidate is not modified
    mutant = [row.copy() for row in individual]

    # Cells that are part of row/column duplicates (where fitness can improve)
    conflicted_cells = []
    for r in range(9):
        for c in range(9):
            if mask[r][c]:
                continue
            value = mutant[r][c]
            row_dups = mutant[r].count(value) - 1
            col_dups = sum(1 for rr in range(9) if mutant[rr][c] == value) - 1
            if row_dups + col_dups > 0:
                conflicted_cells.append((r, c))

    # Candidate boxes to mutate, preferred from conflicted cells
    preferred_boxes = []
    for r, c in conflicted_cells:
        box_idx = (r // 3) * 3 + (c // 3)
        if box_idx not in preferred_boxes:
            preferred_boxes.append(box_idx)

    # Fallback: any box with >=2 mutable cells
    all_valid_boxes = []
    for box_idx in range(9):
        box_row = (box_idx // 3) * 3
        box_col = (box_idx % 3) * 3
        mutable_count = 0
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if not mask[r][c]:
                    mutable_count += 1
        if mutable_count >= 2:
            all_valid_boxes.append(box_idx)

    if not all_valid_boxes:
        return mutant

    candidate_boxes = [b for b in preferred_boxes if b in all_valid_boxes]
    if not candidate_boxes:
        candidate_boxes = all_valid_boxes

    box = random.choice(candidate_boxes)
    box_row = (box // 3) * 3
    box_col = (box % 3) * 3

    mutable = []
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if not mask[r][c]:
                mutable.append((r, c))

    if len(mutable) < 2:
        return mutant

    (r1, c1), (r2, c2) = random.sample(mutable, 2)
    mutant[r1][c1], mutant[r2][c2] = mutant[r2][c2], mutant[r1][c1]

    return mutant

"""
Recombination methods
"""

def sudoku_box_crossover(parent1, parent2):
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

def replacement(current_pop, current_fitness, offspring, offspring_fitness):
    """Survivor selection that prefers unique individuals when possible."""

    combined_pop = current_pop + offspring
    combined_fit = current_fitness + offspring_fitness

    # sort by fitness (best first)
    pop_fit = list(zip(combined_pop, combined_fit))
    pop_fit.sort(key=lambda x: x[1], reverse=True)

    new_population = []
    new_fitness = []
    seen = set()
    duplicate_pool = []
    target_size = len(current_pop)

    # Keep the best unique individuals first, save duplicates for possible refill.
    for individual, fit in pop_fit:
        key = tuple(tuple(row) for row in individual)

        if key not in seen:
            new_population.append(individual)
            new_fitness.append(fit)
            seen.add(key)
        else:
            duplicate_pool.append((individual, fit))

        if len(new_population) == target_size:
            break

    # Refill if dedup removed too many candidates.
    # Sample from a top slice of duplicates so we keep fitness pressure
    # without repeatedly cloning only the very top individual.
    if len(new_population) < target_size:
        refill_pool = duplicate_pool if duplicate_pool else pop_fit
        top_slice = refill_pool[: max(1, min(len(refill_pool), 100))]

        while len(new_population) < target_size:
            individual, fit = random.choice(top_slice)
            new_population.append(individual)
            new_fitness.append(fit)

    if len(new_population) != target_size or len(new_fitness) != target_size:
        raise RuntimeError("Replacement failed to maintain population size.")

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
    mating_pool_size = 1000 # keep even
    tournament_size = 4
    xover_rate = 0.9
    mut_rate = 0.7
    gen_limit = 5000

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
        if len(population) < tournament_size:
            raise RuntimeError("Population too small for tournament selection.")

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
                off1, off2 = sudoku_box_crossover(p1, p2)
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