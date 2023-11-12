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
        print self.map
        
    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    # For now I just move randomly
    def getAction(self, state):
        v_iterations(self.map, state)
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)

def v_iterations(map, state):
    print populatateRewards(api.food(state), api.ghosts(state), api.walls(state), api.corners(state), api.capsules(state))[1]

def populatateRewards(f, g, w, co, ca):
    m = initial_map(w, co)
    xMax = co[2][1] + 1
    yMax = co[1][0] + 1
    
    for i in range(yMax):
        for j in range(xMax):
            current_cell = (i, j)

            if current_cell in f:
                m[j][i] = FOOD_REWARD
            elif current_cell in g:
                m[j][i] = GHOST_REWARD
            elif current_cell in w:
                m[j][i] = None
            elif current_cell in ca:
                m[j][i] = CAPSULE_REWARD
            else:
                m[j][i] = EMPTY_REWARD
    return m

def initial_map(walls, corners):
    h = corners[1][0] + 1
    w = corners[2][1] + 1
    pacman_map = []
    for i in range(w):
        pacman_map.append([])
        for j in range(h):
            pacman_map[i].append("  ")

    for i in range(w):
        for j in range(h):
            if (j, i) in walls:
                pacman_map[i][j] = None
            else:
                pacman_map[i][j] = EMPTY_REWARD
    return pacman_map