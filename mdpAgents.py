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
        v_iterations(self.map, state)
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)

def v_iterations(map, state):
    reward_map = populateRewards(state)
    
def bellmanEquation(currValue, currCell, xMax, yMax, map):
    x = currCell[0]
    y = currCell[1]
    if currValue is None:
        return None
    
def populateRewards(state):
    f = api.food(state)
    g = api.ghosts(state)
    w = api.walls(state)
    co = api.corners(state)
    ca = api.capsules(state)
    
    m = initial_map(w, co)
    xMax = co[1][0] + 1
    yMax = co[2][1] + 1
    
    for i in range(xMax):
        for j in range(yMax):
            if (i, j) in f:
                m[j][i] = FOOD_REWARD
            if (i, j) in g:
                m[j][i] = GHOST_REWARD
            if (i, j) in ca:
                m[j][i] = CAPSULE_REWARD 
    print m
    print
                
    return m

def initial_map(walls, corners):
    xMax = corners[1][0] + 1
    yMax = corners[2][1] + 1
    pacman_map = [[" " for x in range(xMax)] for y in range(yMax)]
    

    for i in range(xMax):
        for j in range(yMax):
            if (i, j) in walls:
                pacman_map[j][i] = None
            else:
                pacman_map[j][i] = EMPTY_REWARD
    return pacman_map