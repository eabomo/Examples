# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 15:44:54 2023

@author: JUSTINHILL
"""

from pulp import *

def check_islands(rows, cols, island):
    '''
    This function makes sure that each row and column
    is accounted for in the island dictionary.
    '''
    # initialize the grid to zero, for "not checked"
    checked = [[0 for r in range(rows)] for c in range(cols)]
    # iterate through each coordinate listed in the island and set
    # the appropriate value in "checked" to 1
    for isle in island:
        for coord in island[isle]:
            checked[coord[0]][coord[1]] += 1
    # If all cells aren't checked, the isles in island do not cover
    # the board
    for r in range(rows):
        for c in range(cols):
            if checked[r][c] != 1:
                return False
    return True


def solve_star_game(rows, cols, island):
    # If the island scheme checks out, solve the problem.
    if check_islands(rows, cols, island):

        model = LpProblem("Star_Game", LpMinimize)
        
        #### Decision Variables
        y = dict()
        for r in range(rows):
            for c in range(cols):
                # The y-variable will equal 1 when a star is placed in cell (r, c); 0 otherwise
                y[r, c] = LpVariable("y_(%s,%s)" % (r, c), lowBound=0, cat='Binary')
        
        z = LpVariable("ObjDummy", lowBound=0)
        
        #### Objective
        model += z, "Dummy Obj"
        
        #### Constraints
        # Each row gets two stars
        for r in range(rows):
            model += lpSum(y[r, c] for c in range(cols)) == 2, 'Row[%s]' % (r)
        # Each column gets two stars
        for c in range(cols):
            model += lpSum(y[r, c] for r in range(rows)) == 2, 'Col[%s]' % (c)
        # Each isle gets two stars
        for isle in island:
            model += lpSum(y[pair] for pair in island[isle]) == 2, 'Island[%s]' % (isle)
        # Space between cells; no two stars can be in adjacent cells
        for r in range(rows):
            for c in range(cols):
                for rx in range(-1, 2):
                    for cx in range(-1, 2):
                        if r != r + rx or c != c + cx:
                            if 0 <= r + rx <= rows-1 and 0 <= c + cx <= cols-1:
                                model += y[r, c] + y[r + rx, c + cx] <= 1, 'Adj[%s,%s,%s,%s]' % (r, c, r+rx, c+cx)

        #### Record and solve the model
        model.writeLP("Star_Game.lp")
        model.writeMPS("Star_Game.mps")
        solver = PULP_CBC_CMD(msg=False)
        model.solve(solver)
        
        # Print the solution status to the screen
        print("Status:", LpStatus[model.status])
        # Print the relevant decision variables to the screen    
        for v in model.variables():
            if v.varValue == 1:
                print(v.name, "=", v.varValue)
    else:
        print("fix islands")


if __name__=="__main__":
    # LAY OUT THE GAME BOARD
    # This is a picture of the island scheme defined
    # in the island dictionary below.
    #   | 0   1   2   3   4   5   6   7   8   9 |
    #   +---------------------------------------+
    # 0 |               |           |           |
    #   |   a   +-------+---+   +---+           |
    # 1 |       |     d     |   |        h      |
    #   +---+   +-----------+   +---+           |
    # 2 |   |   |   |               |           |
    #   |   |   |   +---+   f   +---+-----------+
    # 3 |   |   |       |       |               |
    #   |   +---+       |       |       i       |
    # 4 |               |       |               |
    #   |               |   +---+-----------+   |
    # 5 |               |   |               |   |
    #   |    b      +---+---+           +---+---+
    # 6 |           |                   |       |
    #   |           +---+               |       |
    # 7 |           |   |       g       |       |
    #   +-------+   |   |               |   j   |
    # 8 |       |   | e |               |       |
    #   |   c   +---+   +---+           |       |
    # 9 |           |       |           |       |
    #   +-----------+-------+-----------+-------+
    #   | 0   1   2   3   4   5   6   7   8   9 |

    island = {
        'a': [(0, 0), (0, 1), (0, 2), (0, 3),
              (1, 0), (1, 1),
                      (2, 1),
                      (3, 1)],
        'b': [(2, 0),         (2, 2),
              (3, 0),         (3, 2), (3, 3),
              (4, 0), (4, 1), (4, 2), (4, 3),
              (5, 0), (5, 1), (5, 2), (5, 3),
              (6, 0), (6, 1), (6, 2),
              (7, 0), (7, 1), (7, 2),
                              (8, 2)],
        'c': [(8, 0), (8, 1),
              (9, 0), (9, 1), (9, 2)],
        'd': [(1, 2), (1, 3), (1, 4)],
        'e': [(7, 3),
              (8, 3),
              (9, 3), (9, 4)],
        'f': [        (0, 4), (0, 5), (0, 6),
                              (1, 5),
              (2, 3), (2, 4), (2, 5), (2, 6),
                      (3, 4), (3, 5),
                      (4, 4), (4, 5),
                      (5, 4)],
        'g': [                (5, 5), (5, 6), (5, 7), (5, 8),
              (6, 3), (6, 4), (6, 5), (6, 6), (6, 7),
                      (7, 4), (7, 5), (7, 6), (7, 7),
                      (8, 4), (8, 5), (8, 6), (8, 7),
                              (9, 5), (9, 6), (9, 7)],
        'h': [        (0, 7), (0, 8), (0, 9),
              (1, 6), (1, 7), (1, 8), (1, 9),
                      (2, 7), (2, 8), (2, 9)],
        'i': [(3, 6), (3, 7), (3, 8), (3, 9),
              (4, 6), (4, 7), (4, 8), (4, 9),
                                      (5, 9)],
        'j': [(6, 8), (6, 9),
              (7, 8), (7, 9),
              (8, 8), (8, 9),
              (9, 8), (9, 9)]
    }
    rows = 10
    cols = 10
    solve_star_game(rows, cols, island)
    # The solution to the test model provided above 
    # looks like this:
    #   | 0   1   2   3   4   5   6   7   8   9 |
    #   +---------------------------------------+
    # 0 | *             |         * |           |
    #   |       +-------+---+   +---+           |
    # 1 |       | *       * |   |               |
    #   +---+   +-----------+   +---+           |
    # 2 |   |   |   |               | *       * |
    #   |   |   |   +---+       +---+-----------+
    # 3 |   | * |       |     * |               |
    #   |   +---+       |       |               |
    # 4 |               |       |     *       * |
    #   |               |   +---+-----------+   |
    # 5 |             * |   | *             |   |
    #   |           +---+---+           +---+---+
    # 6 |     *     |                   | *     |
    #   |           +---+               |       |
    # 7 |           | * |         *     |       |
    #   +-------+   |   |               |       |
    # 8 | *     |   |   |               | *     |
    #   |       +---+   +---+           |       |
    # 9 |         * |     * |           |       |
    #   +-----------+-------+-----------+-------+
    #   | 0   1   2   3   4   5   6   7   8   9 |