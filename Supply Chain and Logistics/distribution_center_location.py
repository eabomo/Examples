import pandas as pd
import pathlib
import os
from pulp import *
from math import radians, cos, sin, asin, sqrt, ceil
from itertools import combinations
import json

# This is a toy problem to decide where to place two distribution centers.
#
# Possible Distribution Centers
# Fresno, Colorado Springs, Kansas City, Minneapolis, Charlotte
#
# Delivering To
# All those locations, plus
# Dallas, Houston, San Francisco, Seattle, San Diego, Salt Lake City, New Orleans, Memphis, Atlanta,
# Pittsburgh, Boston, Miami
#
# Choose the two distribution centers that minimize the total transportation costs.
# Assume transportation cost is essentially the distance between the cities.
# Each city will be served by a single distribution center.
# The number of cities served by one distribution center should be within one of the number of cities served by the other.
# Some cities will be served twice during a planning period. All others will be served once.
# Once: Salt Lake City, New Orleans, Memphis, Pittsburgh, San Diego, Fresno, Colorado Springs, Kansas City, Minneapolis, Charlotte
# Twice: All others
#
# DISCLAIMER: We'd need A LOT more information and detail to make this problem realistic! 
# 
# For each pair of possible distribution centers, solve the following IP
# min sum_(i,j) n_j * c_(i, j) * x_(i, j)
# s.t.
# sum_i x_(i,j) = 1, for all j (each city is assigned to one distribution center)
# sum_(j) x_(0,j) - sum_(j) x_(1,j) <= 1  (distribution center 0 can have at most 1 more city than dc 1)
# sum_(j) x_(1,j) - sum_(j) x_(0,j) <= 1  (distribution center 1 can have at most 1 more city than dc 0)
# where
# n_j is the number of times city j will be served
# c_(i,j) is the transportation cost from city i to city j
# x_(i,j) = 1 if distribution center i is assigned to city j

# The following function was modified from
# https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
# There are several other ways to get the haversine distance in python: scgraph, sklearn, haversine
def haversine(loc1, loc2):
    """
    Calculate the great circle distance, in miles, between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [loc1[1], loc1[0], loc2[1], loc2[0]])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3956 # Radius of earth in  miles
    return ceil(c * r) # Rounding up to the nearest mile


def read_data(this_directory, filename):
    # Read the airport location for each city (got the list from ChatGPT)
    filepath = os.path.join(this_directory, filename)
    data = pd.read_csv(filepath) # The pandas csv reader is very good
    data['Coordinates'] = list(zip(data['Latitude'], data['Longitude']))
    return data


def get_distances(data):
    cities = data['City'].values
    coordinates = data['Coordinates'].values
    distance = {}
    for c in cities:
        distance[c] = {}

    for i in range(len(cities)-1):
        for j in range(i+1, len(cities)):
            distance[cities[i]][cities[j]] = haversine(coordinates[i], coordinates[j])
            distance[cities[j]][cities[i]] = distance[cities[i]][cities[j]]
    return distance


def build_and_solve_model(distribution_centers, other_cities):
    model = LpProblem("Min Cost Assignment", LpMinimize)

    #### Decision Variables
    x = dict()
    for i in distribution_centers:
        for j in other_cities:
            x[i, j] = LpVariable("x_(%s,%s)" % (i, j), cat='Binary')

    z = LpVariable("ObjDummy", lowBound=0)

    #### Objective
    model += lpSum(number_visits[j] * distance[i][j] * x[i, j] for i in distribution_centers for j in other_cities), 'Transportation Cost'

    #### Constraints
    for j in other_cities:
        model += lpSum(x[i, j] for i in distribution_centers) == 1, 'Assign %s' % (j)
    
    model += (lpSum(x[i, j] for i in [distribution_centers[0]] for j in other_cities) 
              - lpSum(x[i, j] for i in [distribution_centers[1]] for j in other_cities)) <= 1, 'Balance_A'
    model += (lpSum(x[i, j] for i in [distribution_centers[1]] for j in other_cities) 
              - lpSum(x[i, j] for i in [distribution_centers[0]] for j in other_cities)) <= 1, 'Balance_B'
    
    solver = PULP_CBC_CMD(msg=False)
    model.solve(solver)

    assignments = {}
    for i in distribution_centers:
        assignments[i] = []
        for j in other_cities:
            if x[i, j].varValue == 1:
                assignments[i].append(j)
    return model.objective.value(), assignments


# Info used by every pair of distribution centers in the experiment
this_directory = pathlib.Path(__file__).parent.resolve()
data = read_data(this_directory, 'airport_coordinates.csv')
distance = get_distances(data)
number_visits = {}
one_visit = [
    'Salt Lake',
    'New Orleans',
    'Memphis',
    'Pittsburgh',
    'San Diego',
    'Fresno', 
    'Colorado Springs', 
    'Kansas City', 
    'Minneapolis',
    'Charlotte'
]
for city in data['City'].values:
    if city in one_visit:
        number_visits[city] = 1
    else:
        number_visits[city] = 2

possible_distribution_centers = [
    'Fresno', 
    'Colorado Springs', 
    'Kansas City', 
    'Minneapolis',
    'Charlotte'
]

solutions = []
min_cost = 1e9
best_pair = ''
# Iterate through each pair of distribution centers
for distribution_centers in combinations(possible_distribution_centers, 2):
    other_cities = []
    for city in data['City'].values:
        if city not in distribution_centers:
            other_cities.append(city)
    transportation_cost, assignments = build_and_solve_model(distribution_centers, other_cities)
    solution_details = {}
    solution_details['Distribution Centers'] = distribution_centers
    solution_details['Transportation Cost'] = transportation_cost
    solution_details['Assignments'] = assignments
    if transportation_cost < min_cost:
        min_cost = transportation_cost
        best_pair = distribution_centers
    solutions.append(solution_details)

print(min_cost, best_pair)
with open(os.path.join(this_directory, 'solutions.json'), 'w') as f:
    json.dump(solutions, f)
