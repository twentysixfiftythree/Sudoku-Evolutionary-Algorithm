"""
Run repeated EA experiments per puzzle, record per-generation best/avg fitness,
and produce convergence plots and a success-rate summary.

Default: 5 repeats per puzzle (adjustable).
"""
import os
import time
import random

import numpy as np
import matplotlib.pyplot as plt

from puzzles import PUZZLES
from main import (
    parse_puzzle,
    fixed_mask,
    sudoku_population,
    fitness_sudoku,
    sudoku_swap,
    sudoku_box_crossover,
    tournament,
    replacement,
)


def run_ea_collect(puzzle_string, seed=None,
                   popsize=500, mating_pool_size=500, tournament_size=4,
                   xover_rate=0.9, mut_rate=0.7, gen_limit=500):
    if seed is not None:
        random.seed(seed)
    else:
        random.seed()

    given_grid = parse_puzzle(puzzle_string)
    mask = fixed_mask(given_grid)

    population = sudoku_population(popsize, given_grid)
    fitness = [fitness_sudoku(ind) for ind in population]

    best_hist = [max(fitness)]
    avg_hist = [sum(fitness) / len(fitness)]

    gen = 0
    start = time.perf_counter()

    while gen < gen_limit and max(fitness) < 243:
        parents_index = tournament(fitness, mating_pool_size, tournament_size)
        random.shuffle(parents_index)

        offspring = []
        offspring_fitness = []

        for i in range(0, len(parents_index) - 1, 2):
            p1 = population[parents_index[i]]
            p2 = population[parents_index[i + 1]]

            if random.random() < xover_rate:
                off1, off2 = sudoku_box_crossover(p1, p2)
            else:
                off1 = [row.copy() for row in p1]
                off2 = [row.copy() for row in p2]

            if random.random() < mut_rate:
                off1 = sudoku_swap(off1, mask)
            if random.random() < mut_rate:
                off2 = sudoku_swap(off2, mask)

            offspring.append(off1)
            offspring_fitness.append(fitness_sudoku(off1))
            offspring.append(off2)
            offspring_fitness.append(fitness_sudoku(off2))

        population, fitness = replacement(population, fitness, offspring, offspring_fitness)
        gen += 1

        best_hist.append(max(fitness))
        avg_hist.append(sum(fitness) / len(fitness))

    end = time.perf_counter()

    best_index = fitness.index(max(fitness))
    best_fit = fitness[best_index]

    return {
        "best_fitness": best_fit,
        "total_conflicts": 243 - best_fit,
        "generations": gen,
        "time_s": round(end - start, 4),
        "solved": best_fit == 243,
        "best_hist": best_hist,
        "avg_hist": avg_hist,
    }


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def plot_convergence(puzzle_name, all_best, all_avg, outdir):
    # all_best: list of lists (runs x gens)
    max_len = max(len(x) for x in all_best)

    # pad with last value so arrays align
    best_arr = np.array([np.pad(run, (0, max_len - len(run)), 'edge') for run in all_best])
    avg_arr = np.array([np.pad(run, (0, max_len - len(run)), 'edge') for run in all_avg])

    gen = np.arange(0, max_len)

    mean_best = best_arr.mean(axis=0)
    std_best = best_arr.std(axis=0)
    mean_avg = avg_arr.mean(axis=0)
    std_avg = avg_arr.std(axis=0)

    plt.figure(figsize=(8, 4.5))
    plt.fill_between(gen, mean_best - std_best, mean_best + std_best, alpha=0.2, label='best ± std')
    plt.plot(gen, mean_best, label='mean best')
    plt.fill_between(gen, mean_avg - std_avg, mean_avg + std_avg, alpha=0.15)
    plt.plot(gen, mean_avg, label='mean avg')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title(f'Convergence: {puzzle_name}')
    plt.legend()
    plt.tight_layout()

    out = os.path.join(outdir, f'convergence_{puzzle_name}.png')
    plt.savefig(out)
    plt.close()


def plot_success_rate(summary, outdir):
    names = [s['puzzle'] for s in summary]
    rates = [s['success_rate'] * 100 for s in summary]

    plt.figure(figsize=(6, 4))
    bars = plt.bar(names, rates, color='tab:blue')
    plt.ylim(0, 100)
    plt.ylabel('Success rate (%)')
    plt.title('EA Success Rate per Puzzle')
    for b, r in zip(bars, rates):
        plt.text(b.get_x() + b.get_width() / 2, r + 1, f'{r:.0f}%', ha='center')
    plt.tight_layout()
    out = os.path.join(outdir, 'success_rate.png')
    plt.savefig(out)
    plt.close()


def main(repeats=5, popsize=500, gen_limit=500):
    random.seed(0)
    ensure_dir('plots')
    ensure_dir('results')

    summary = []

    for name, puzzle in PUZZLES:
        print(f'Running puzzle: {name}')
        all_best = []
        all_avg = []
        solved_count = 0
        runs_info = []

        for r in range(repeats):
            print(f'  run {r+1}/{repeats}', end='... ')
            stats = run_ea_collect(puzzle, seed=r, popsize=popsize, gen_limit=gen_limit)
            all_best.append(stats['best_hist'])
            all_avg.append(stats['avg_hist'])
            if stats['solved']:
                solved_count += 1
            runs_info.append(stats)
            print(f"solved={stats['solved']}, best={stats['best_fitness']}, gens={stats['generations']}, time_s={stats['time_s']}")

        # save per-puzzle run info
        csv_path = os.path.join('results', f'{name}_runs.csv')
        with open(csv_path, 'w') as fh:
            fh.write('run,solved,best_fitness,generations,time_s\n')
            for i, info in enumerate(runs_info):
                fh.write(f"{i+1},{int(info['solved'])},{info['best_fitness']},{info['generations']},{info['time_s']}\n")

        success_rate = solved_count / repeats
        summary.append({'puzzle': name, 'success_rate': success_rate, 'runs': repeats})

        # plot convergence
        plot_convergence(name, all_best, all_avg, 'plots')

    # save summary CSV
    sum_csv = os.path.join('results', 'analysis_summary.csv')
    with open(sum_csv, 'w') as fh:
        fh.write('puzzle,success_rate,runs\n')
        for s in summary:
            fh.write(f"{s['puzzle']},{s['success_rate']},{s['runs']}\n")

    plot_success_rate(summary, 'plots')
    print('\nAnalysis complete. Plots in plots/, CSVs in results/')


if __name__ == '__main__':
    main(repeats=5, popsize=500, gen_limit=500)
