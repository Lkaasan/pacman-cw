# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

FOOD_REWARD = 10
EMPTY_REWARD = -0.04
CAPSULE_REWARD = 100
GHOST_REWARD = -1000
GAMMA = 0.9
DANGER_ZONE_RATIO = 6
DANGER = 500


class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman" 
        self.walls = None
        self.corners = None
        self.map = None

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        self.corners = api.corners(state)
        self.walls = api.walls(state)
        self.map = initial_map(self.corners, self.walls)
        
    # This is what gets run in between multiple games
    def final(self, state):
        self.map = None
        print "Looks like the game just ended!"

    # For now I just move randomly
    def getAction(self, state):
        self.map = v_iterations(self.map, state)
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        pacman_location = api.whereAmI(state)
        [scores, actions] = get_action_scores(legal, self.map, pacman_location[0], pacman_location[1])
        max_score_index = scores.index(max(scores))
        print scores
        print actions
        choice = actions[max_score_index]
        return api.makeMove(choice, legal)


def get_action_scores(legal, pacman_map, x, y):
    action_scores = {}
    for action in legal:
        value = None
        if action is Directions.NORTH:
            value = pacman_map[y + 1][x]
        elif action is Directions.SOUTH:
            value = pacman_map[y - 1][x]
        elif action is Directions.EAST:
            value = pacman_map[y][x + 1]
        elif action is Directions.WEST:
            value = pacman_map[y][x - 1]
        if value is not None:
            action_scores[action] = value

    scores = list(action_scores.values())
    actions = list(action_scores.keys())

    return scores, actions


def v_iterations(map, state):
    reward_map = populateRewards(state)
    corners = api.corners(state)
    width = corners[2][1] + 1
    height = corners[1][0] + 1
    
    pacman = api.whereAmI(state)
    pacman = (pacman[1], pacman[0])
    update_reward_map(reward_map, pacman, api.ghosts(state), height, width)

    for x in range(0, 10):
        temp_map = initial_map(api.walls(state), corners)
        for i in range(width):
            for j in range(height):
                current_cell_value = reward_map[i][j]
                current_cell = (i, j)
                temp_map[i][j] = bellmannEquation(current_cell_value, current_cell, width, height, reward_map)
        reward_map = temp_map
    return reward_map
    
def bellmannEquation(curr_value, currCell, width, height, map):
    x = currCell[0]
    y = currCell[1]
    if curr_value is None:
        return None
    e = None
    w = None
    n = None
    s = None
    
    if x < width - 1:
        east = map[x + 1][y]
    if x > 0:
        west = map[x - 1][y]
    if y < height - 1:
        north = map[x][y + 1]
    if y > 0:
        south = map[x][y - 1]

    if east is None:
        east = - 1
    if west is None:
        west = -1
    if north is None:
        north = -1
    if south is None:
        south = -1
    
    if north is not None:
        north_val = north * 0.8 + (east + west) * 0.1
    else:
        north_val = current
    if south is not None:
        south_val = south * 0.8 + (east + west) * 0.1
    else:
        south_val = current
    if east is not None:
        east_val = east * 0.8 + (north + south) * 0.1
    else:
        east_val = current
    if west is not None:
        west_val = west * 0.8 + (north + south) * 0.1
    else:
        west_val = current
        
    max_val = max([north_val, south_val, east_val, west_val])
    return float(float(curr_value) + float(GAMMA) * float(max_val))

def update_reward_map(reward_map, pacman, ghosts, h, w):
    """
    Update the reward map by applying mali to the cells that are close to pacman. The closest said
    cell is to a ghost, the greater the malus is that is applied to the reward value of the cell.
    Only a certain number of cells is taken into consideration. Specifically the same amount as the value
    of the global constant DANGER_ZONE
    @param reward_map: the reward map without any malus
    @type reward_map: list
    @param pacman: pacman's position
    @type pacman: Tuple[int, int]
    @param ghosts: a list of ghost positions
    @type ghosts: list
    @param h: the height of the map
    @type h: int
    @param w: the width of the map
    @type w: int
    """
    for n in get_neighbours(pacman, h, w):
        if n is not None and reward_map[n[0]][n[1]] is not None:
            [distance, cells] = distance_to_closest_ghost(n, ghosts, h, w)
            if distance > 0:
                # the further away we are from pacman, the less impactful the malus is
                reward_map[n[0]][n[1]] -= (DANGER / distance)
                for cell in cells:
                    if reward_map[cell[0]][cell[1]] is not None:
                        reward_map[cell[0]][cell[1]] -= (DANGER / distance)



def distance_to_closest_ghost(cell, ghosts, h, w):
    """
    Calculate the distance to the closest ghost as the value of cells explored before reaching the same position
    as the closest ghost, using a frontier traversing algorithm.
    @param cell: the cell from which to calculate the distance
    @type cell: list
    @param ghosts: the list containing the positions of ghosts
    @type ghosts: list
    @param h: the height of the map
    @type h: int
    @param w: the width of the map
    @type w: w
    @return: the distance to the ghost
    @rtype: int
    """
    frontier = util.Queue()
    frontier.push(cell)
    came_from = dict()
    came_from[cell] = None
    distance = 0
    found = False
    cells = []
    while not frontier.isEmpty() and distance < (h*w / DANGER_ZONE_RATIO):
        current = frontier.pop()
        cells.append(current)
        distance += 1
        if (current[1], current[0]) in ghosts:
            found = True
            break

        for neighbour in get_neighbours(current, h, w):
            if neighbour is not None and neighbour not in came_from:
                frontier.push(neighbour)
                came_from[neighbour] = current
    if found:
        return [distance, cells]
    else:
        return [0, cells]


def get_neighbours(cell, h, w):
    """
    Get the adjacent cells
    @param cell: the cell for which to retrieve the neighbours
    @type cell: list
    @param h: the height of the map
    @type h: int
    @param w: the width of the map
    @type w: int
    @return: list of the neighbours' coordinates
    @rtype: list
    """
    x = cell[0]
    y = cell[1]
    north = south = east = west = None
    if y + 1 < h:
        north = (x, y + 1)
    if y - 1 > 0:
        south = (x, y - 1)
    if x + 1 < w:
        east = (x + 1, y)
    if x - 1 > 0:
        west = (x - 1, y)

    return [north, south, east, west]


def populateRewards(state):
    f = api.food(state)
    g = api.ghosts(state)
    w = api.walls(state)
    co = api.corners(state)
    ca = api.capsules(state)
    
    m = initial_map(w, co)
    width = co[1][0] + 1
    height = co[2][1] + 1
    
    for i in range(width):
        for j in range(height):
            if (i, j) in f:
                m[j][i] = FOOD_REWARD
            if (i, j) in g:
                m[j][i] = GHOST_REWARD
            if (i, j) in ca:
                m[j][i] = CAPSULE_REWARD 
    return m

def initial_map(walls, corners):
    width = corners[1][0] + 1
    height = corners[2][1] + 1
    pacman_map = [[" " for x in range(width)] for y in range(height)]
    

    for i in range(width):
        for j in range(height):
            if (i, j) in walls:
                pacman_map[j][i] = None
            else:
                pacman_map[j][i] = EMPTY_REWARD
    return pacman_map