# Sudoku Evolutionary Algorithm

A Python implementation of a 9x9 Sudoku solver using an evolutionary algorithm (EA).

This project was built for our course presentation in CISC 455: Evolutionary Optimization.

## What it does

- Solves Sudoku puzzles where `0` means an empty/mutable cell.
- Keeps given clues fixed throughout evolution.
- Uses fitness maximization, with a perfect score of `243`.

## Quick start

From the project root, run:

```powershell
python main.py
```

This runs one interactive EA solve using the default puzzle in `main.py`.

For batch experiments (multiple puzzles/runs + plots/CSVs):

```powershell
python analysis.py
```

## Dependencies

`main.py` uses only Python standard library.

`analysis.py` also requires:

- `numpy`
- `matplotlib`

Install if needed:

```powershell
pip install numpy matplotlib
```

## Project layout

- `main.py` - core EA operators and single-run pipeline.
- `analysis.py` - repeated experiments and artifact generation.
- `puzzles.py` - puzzle registry (`PUZZLES`).
- `plots/` - generated convergence and success-rate plots.
- `results/` - generated CSV summaries.

## Notes

- Stop condition: generation limit reached, or best fitness reaches `243`.
- Batch analysis uses deterministic per-run seeds (`seed=r`) for reproducibility.
- Puzzle strings must contain 81 digits.
