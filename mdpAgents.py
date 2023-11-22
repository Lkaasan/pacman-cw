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


class Cell:

    def __init__(self, value, coordinate):
        self.value = value
        self.coordinate = coordinate


class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman" 
        self.corners = self.walls = self.map = self.width = self.height = self.capsules = None
        self.food_reward = 10
        self.empty_reward = -0.04
        self.capsule_reward = 100
        self.ghost_reward = -1000
        self.gamma = 0.9
        self.repeat = False        

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        self.corners = api.corners(state)
        self.walls = api.walls(state)
        self.capsules = api.capsules(state)
        self.width = self.corners[1][0] + 1
        self.height = self.corners[2][1] + 1
        self.map = self.create_empty_map()
        
        
    # This is what gets run in between multiple games
    def final(self, state):
        self.map = None
        print "Looks like the game just ended!"

    # For now I just move randomly
    def getAction(self, state):
        self.map = self.create_empty_map()
        self.populate_rewards(state)
        self.v_iteration(state)
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        pacman_location = api.whereAmI(state)

        if self.is_in_corner(pacman_location) or self.repeat == True:
            self.repeat = not self.repeat
            return api.makeMove(random.choice(legal), legal)
        [scores, actions] = self.get_action_scores(legal, self.map, pacman_location[0], pacman_location[1])
        print scores
        print actions
        max_score_index = scores.index(max(scores))
        choice = actions[max_score_index]
        return api.makeMove(choice, legal)



    def get_action_scores(self, legal, pacman_map, x, y):
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

    def v_iteration(self, state):
        for x in range (0, 10):
            temp_map = self.create_empty_map()
            for i in range(self.height):
                for j in range(self.width):
                    c = Cell(self.map[i][j], (i, j))
                    temp_map[i][j] = self.bellmann_equation(c)
            self.map = temp_map

    def bellmann_equation(self, c):
        x = c.coordinate[0]
        y = c.coordinate[1]
        if c.value is None:
            return None
        e = None
        w = None
        n = None
        s = None
        
        if x < self.width - 1:
            e = self.map[x + 1][y]
        if x > 0:
            w = self.map[x - 1][y]
        if y < self.height - 1:
            n = self.map[x][y + 1]
        if y > 0:
            s = self.map[x][y - 1]

        if e is None:
            e = - 1
        if w is None:
            w = -1
        if n is None:
            n = -1
        if s is None:
            s = -1
        
        if n is not None:
            n_val = n * 0.8 + (e + w) * 0.1
        else:
            n_val = c.value
        if s is not None:
            s_val = s * 0.8 + (e + w) * 0.1
        else:
            s_val = c.value
        if e is not None:
            e_val = e * 0.8 + (n + s) * 0.1
        else:
            e_val = c.value
        if w is not None:
            w_val = w * 0.8 + (n + s) * 0.1
        else:
            w_val = c.value
            
        max_val = max([n_val, s_val, e_val, w_val])
        return float(float(c.value) + float(self.gamma) * float(max_val))

    def populate_rewards(self, state):
        ghosts = api.ghosts(state)
        food = api.food(state)

        for i in range(self.width):
            for j in range(self.height):
                if (i, j) in ghosts:
                    distance_to_ghost = self.distance_to_closest_ghost(state)
                    self.map[j][i] = self.ghost_reward * (1.0 / distance_to_ghost)
                elif (i, j) in self.capsules:
                    self.map[j][i] = self.capsule_reward
                elif (i, j) in food:
                    self.map[j][i] = self.food_reward

    def create_empty_map(self):
        p_map = [[" " for x in range(self.width)] for y in range(self.height)]
        for i in range(self.width):
            for j in range(self.height):
                if (i, j) in self.walls:
                    p_map[j][i] = None
                else: 
                    p_map[j][i] = self.empty_reward
        return p_map

    def distance_to_closest_ghost(self, state):

        return min(util.manhattanDistance(api.whereAmI(state), ghost) for ghost in api.ghosts(state))

    def is_in_corner(self, location):
        return location in [(1, 1), (1, self.height - 2), (self.width - 2, 1), (self.width - 2, self.height - 2)]