# -*- coding: utf-8 -*-
"""
@author: JUSTINHILL

This program uses binary integer programming to solve a sudoku. There are certainly
better ways to solve a sudoku, but this works! 
"""

from pulp import *

# These are the given values in the sudoku.
# Fixed values (row, column, value), so in the example,
# the first row and second column contains a 3.
# Rows and columns indexed from zero
# Values are digit values 1-9
# fixed_values = [
    # (0, 1, 3), (0, 3, 9), (0, 5, 8),
    # (1, 1, 7),
    # (2, 2, 5), (2, 5, 3),
    # (3, 3, 1),
    # (4, 2, 7), (4, 4, 2), (4, 6, 8), (4, 7, 5),
    # (5, 0, 2), (5, 1, 4), (5, 2, 8), (5, 8, 6),
    # (6, 4, 1), (6, 7, 9),
    # (7, 0, 5), (7, 8, 3),
    # (8, 3, 5), (8, 6, 7), (8, 7, 2), (8, 8, 4)
# ]
# The fixed values above correspond to the sudoku below:
# +-----+-----+-----+
# |  3  |9   8|     |
# |  7  |     |     |
# |    5|    3|     |
# +-----+-----+-----+
# |     |1    |     |
# |    7|  2  |8 5  |
# |2 4 8|     |  6  |
# +-----+-----+-----+
# |     |  1  |  9  |
# |5    |     |    3|
# |     |5    |7 2 4|
# +-----+-----+-----+

fixed_values = [
    (0, 1, 3), (0, 3, 9), (0, 5, 8),
    (1, 1, 7),
    (2, 2, 5), (2, 5, 3),
    (3, 3, 1),
    (4, 2, 7), (4, 4, 2), (4, 6, 8), (4, 7, 5),
    (5, 0, 2), (5, 1, 4), (5, 2, 8), (5, 8, 6),
    (6, 4, 1), (6, 7, 9),
    (7, 0, 5), (7, 8, 3),
    (8, 3, 5), (8, 6, 7), (8, 7, 2), (8, 8, 4)
]

# These are indices for sections of cells on the sudoku board
# UL is Upper-Left, UM is Upper-Middle, etc.
# [ UL | UM | UR ]
# [ ML | MM | MR ]
# [ LL | LM | LR ]
squares = {
 'UL': [(0, 0), (0, 1), (0, 2),
        (1, 0), (1, 1), (1, 2),
        (2, 0), (2, 1), (2, 2)],
 'UM': [(0, 3), (0, 4), (0, 5),
        (1, 3), (1, 4), (1, 5),
        (2, 3), (2, 4), (2, 5)],
 'UR': [(0, 6), (0, 7), (0, 8),
        (1, 6), (1, 7), (1, 8),
        (2, 6), (2, 7), (2, 8)],
 'ML': [(3, 0), (3, 1), (3, 2),
        (4, 0), (4, 1), (4, 2),
        (5, 0), (5, 1), (5, 2)],
 'MM': [(3, 3), (3, 4), (3, 5),
        (4, 3), (4, 4), (4, 5),
        (5, 3), (5, 4), (5, 5)],
 'MR': [(3, 6), (3, 7), (3, 8),
        (4, 6), (4, 7), (4, 8),
        (5, 6), (5, 7), (5, 8)],
 'LL': [(6, 0), (6, 1), (6, 2),
        (7, 0), (7, 1), (7, 2),
        (8, 0), (8, 1), (8, 2)],
 'LM': [(6, 3), (6, 4), (6, 5),
        (7, 3), (7, 4), (7, 5),
        (8, 3), (8, 4), (8, 5)],
 'LR': [(6, 6), (6, 7), (6, 8),
        (7, 6), (7, 7), (7, 8),
        (8, 6), (8, 7), (8, 8)]
}

rows = range(9)
cols = range(9)
values = range(1,10)

model = LpProblem("Sudoku", LpMinimize)

#### Decision Variables
x = dict()
for r in rows:
    for c in cols:
        for v in values:
            x[r, c, v] = LpVariable("x_(%s,%s,%s)" % (r, c, v), lowBound=0, upBound=1, cat='Binary')

z = LpVariable("ObjDummy", lowBound=0)

#### Objective
model += z, "Dummy Obj"

#### Constraints
## Fixed values
for value in fixed_values:
    r, c, v = value
    model += x[value] == 1, 'Fixed(r{0}c{1}) {2}'.format(r, c, v)

## General Sudoku Constraints
# Only 1 digit in a cell
for r in rows:
    for c in cols:
        model += lpSum(x[r, c, v] for v in values) == 1, 'Cell({0},{1})'.format(r, c)
# Digit only once in each row
for r in rows:
    for v in values:
        model += lpSum(x[r, c, v] for c in cols) == 1, 'Row({0}) {1}s'.format(r, v)
# Digit only once in each col
for c in cols: 
    for v in values:
        model += lpSum(x[r, c, v] for r in rows) == 1, 'Col({0}) {1}s'.format(c, v)
# Digit only once in each square
for label, square in squares.items():
    for v in values:
        model += lpSum(x[r, c, v] for (r, c) in square) == 1, 'Sq({0}) {1}s'.format(label, v)

#### Solution
## Solve
model.writeLP("Sudoku.lp")
model.writeMPS("Sudoku.mps")
solver = PULP_CBC_CMD(msg=False)
model.solve(solver)

## Display
results = []
for v in model.variables():
    if v.varValue == 1:
        results.append(v.name[-2:-1])

divider_row = '+-----+-----+-----+'
for row in range(13):
    for col in range(19):
        if row % 4 == 0:
            print(divider_row)
            break
        elif col in [0, 6, 12]:
            print('|', end='')
        elif col == 18:
            print('|')
        elif col % 2 == 0:
            print(' ', end='')
        else:
            print(results.pop(0), end='')
