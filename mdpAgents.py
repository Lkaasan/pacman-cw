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
        #self.map = initial_map(self.corners, self.walls)
        
    # This is what gets run in between multiple games
    def final(self, state):
        self.map = None
        print "Looks like the game just ended!"

    # For now I just move randomly
    def getAction(self, state):
        self.map = v_iterations(self.map, state)
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)

def v_iterations(map, state):
    reward_map = populateRewards(state)
    
    width = api.corners(state)[2][1] + 1
    height = api.corners(state)[1][0] + 1
    
    for x in range(0, 10):
        temp_map = initial_map(api.walls(state), api.corners(state))
        for i in range(width):
            for j in range(height):
                current_cell_value = reward_map[i][j]
                current_cell = (i, j)
                temp_map[i][j] = bellmanEquation(current_cell_value, current_cell, width, height, reward_map)
        reward_map = temp_map
    return reward_map
    
def bellmanEquation(curr_value, currCell, width, height, map):
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
    
def populateRewards(state):
    f = api.food(state)
    g = api.ghosts(state)
    w = api.walls(state)
    co = api.corners(state)
    ca = api.capsules(state)
    
    m = initial_map(w, co)
    width = co[1][0] + 1
    height = co[2][1] + 1
    print (width, height)
    
    for i in range(width):
        for j in range(height):
            if (i, j) in f:
                m[j][i] = FOOD_REWARD
            if (i, j) in g:
                m[j][i] = GHOST_REWARD
            if (i, j) in ca:
                m[j][i] = CAPSULE_REWARD 
    #print m
    #print
                
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