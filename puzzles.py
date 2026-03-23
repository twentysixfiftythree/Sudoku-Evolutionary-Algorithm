"""
Collection of Sudoku puzzles (81-digit strings; 0 = empty) for testing.
Each entry is a tuple (name, puzzle_string).
"""
PUZZLES = [
#  standard
    ("default",
"530070000"
"600195000"
"098000060"
"800060003"
"400803001"
"700020006"
"060000280"
"000419005"
"000080079"),
# --- ONLINE-SOURCED  ---
# Source: urgentclick medium puzzle string
    ("valid_new_1",
"530070000"
"600195000"
"098000060"
"800060003"
"400803001"
"700020006"
"060000280"
"000419005"
"000080079"),
# Same dataset style (standard benchmark-style puzzles)
    ("medium_online_2",
"000260701"
"680070090"
"190004500"
"820100040"
"004602900"
"050003028"
"009300074"
"040050036"
"703018000"),
    ("medium_online_3",
"300200000"
"000107000"
"706030500"
"070009080"
"900020004"
"010800050"
"009040301"
"000702000"
"000008006"),
    ("medium_online_4",
"200080300"
"060070084"
"030500209"
"000105408"
"000000000"
"402706000"
"301007040"
"720040060"
"004010003"),
    ("medium_online_5",
"000000000"
"009805100"
"051907420"
"290401065"
"000000000"
"140508093"
"026709580"
"005103600"
"000000000"),
# Slightly harder but still standard human-solvable
    ("valid_new_2",
"600120384"
"008459072"
"000006005"
"000264030"
"070080006"
"940003000"
"310000050"
"089700000"
"502000190"),

# --- HARD / EXPERT ---
# Arto Inkala 2012 — rated one of the hardest ever published (21 clues)
# Source: https://www.telegraph.co.uk/news/science/science-news/9359579/Worlds-hardest-sudoku-can-you-crack-it.html
    ("inkala_2012",
"800000000"
"003600000"
"070090200"
"050007000"
"000045700"
"000100030"
"001000068"
"008500010"
"090000400"),

# Al Escargot — Arto Inkala 2006, one of the first "world's hardest" claims (23 clues)
# Source: https://en.wikipedia.org/wiki/Sudoku_solving_algorithms
    ("al_escargot",
"100007090"
"030020008"
"009600500"
"005300900"
"010080002"
"600004000"
"300000010"
"040000007"
"007000300"),

# Top95 #1 — from Peter Norvig's canonical hard puzzle test set (17 clues)
# Source: https://norvig.com/sudoku.html
    ("top95_1",
"400000805"
"030000000"
"000700000"
"020000060"
"000080400"
"000010000"
"000603070"
"500200000"
"104000000"),

# "Hardest Known" — 17-clue puzzle from sudoku benchmark suites
# Requires advanced techniques; no simple naked/hidden singles
    ("hardest_known",
"000000000"
"000003085"
"001020000"
"000507000"
"004000100"
"090000000"
"500000073"
"002010000"
"000040009"),

# Easter Monster — 20-clue expert puzzle, famous in competitive solving circles
    ("easter_monster",
"010000050"
"060008000"
"000360000"
"400090007"
"007000900"
"500070006"
"000045000"
"000900060"
"030000010"),

# Tarek Hard — 18-clue, requires XY-wing / forcing chains to solve
    ("tarek_hard",
"000000000"
"000000060"
"030080070"
"000510000"
"500700200"
"070600900"
"080000003"
"000090040"
"600000700"),
]

if __name__ == "__main__":
    for name, p in PUZZLES:
        print(name, len([c for c in p if c.isdigit()]))