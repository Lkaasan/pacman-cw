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
import time


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
        self.scared_ghost_reward = 1000

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        self.corners = api.corners(state)
        self.walls = api.walls(state)
        
        self.width = self.corners[1][0] + 1
        self.height = self.corners[2][1] + 1
        self.map = self.create_empty_map()
        
        
    # This is what gets run in between multiple games
    def final(self, state):
        self.map = None
        print "Looks like the game just ended!"

    # For now I just move randomly
    def getAction(self, state):
        self.capsules = api.capsules(state)
        self.map = self.create_empty_map()
        self.populate_rewards(state)
        self.v_iteration(state)
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        pacman_location = api.whereAmI(state)
        [scores, actions] = self.get_action_scores(legal, self.map, pacman_location[0], pacman_location[1])
        if all(score == scores[0] for score in scores):
            # print 'yes'
            self.move_towards_closest_food(legal, state)
            [scores, actions] = self.get_action_scores(legal, self.map, pacman_location[0], pacman_location[1])
            if all(score == scores[0] for score in scores):
                return api.makeMove(random.choice(legal), legal)
        max_score_index = scores.index(max(scores))
        choice = actions[max_score_index]
        
        print actions 
        print scores
        print choice
        return api.makeMove(choice, legal)
    
    def move_towards_closest_food(self, legal, state):
        food = api.food(state)
        pacman = api.whereAmI(state)
        closest_food = self.find_closest_food(pacman, food)
        
        # print(api.whereAmI(state))
        # print(closest_food)
        # print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')

        if pacman[0] < closest_food[0]:
            if self.map[pacman[1]][pacman[0] + 1] is not None:
                self.map[pacman[1]][pacman[0] + 1] += 5

        if pacman[1] < closest_food[1]:
            if self.map[pacman[1] + 1][pacman[0]] is not None:
                self.map[pacman[1] + 1][pacman[0]] += 5

        if pacman[0] > closest_food[0]:
            if self.map[pacman[1]][pacman[0] - 1] is not None:
                self.map[pacman[1]][pacman[0] - 1] += 5

        if pacman[1] > closest_food[1]:
            if self.map[pacman[1] - 1][pacman[0]] is not None:
                self.map[pacman[1] - 1][pacman[0]] += 5

        
    def find_closest_food(self, pacman, food):
        distance = 100
        closest_food = ()
        for f in food:
            d = util.manhattanDistance(pacman, f)
            if d < distance:
                distance = d
                closest_food = f
        return closest_food

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
        self.update_ghost_rewards(state)
        for x in range (0, 10):
            empty_map = self.create_empty_map()
            temp_map = self.map
            for i in range(self.height):
                for j in range(self.width):
                    c = Cell(self.map[i][j], (i, j))
                    empty_map[i][j] = self.bellmann_equation(c, temp_map)
            self.map = empty_map
        

    def update_ghost_rewards(self, state): 
        ghosts = api.ghosts(state)
        ghosts_with_states = api.ghostStates(state)
        pacman_location = api.whereAmI(state)
        pacman_neighbours = self.neighbours(pacman_location)
        counter = 0
        for ghost in ghosts:
            neighbours = self.neighbours(ghost)
            for n in neighbours:
                x = int(n[0])
                y = int(n[1])
                if self.map[y][x] is not None:
                    if n in pacman_neighbours:
                        if ghosts_with_states[counter][1] == 0: 
                            self.map[y][x] -= (200000)
                        else:
                            self.map[y][x] += (1000)
                    else:
                        if ghosts_with_states[counter][1] == 0: 
                            self.map[y][x] -= (1000 / self.distance_to_ghost(state, ghost))
                        else:
                            self.map[y][x] += (600 / self.distance_to_ghost(state, ghost))
        counter += 1
        
    def bellmann_equation(self, c, m):
        x, y = c.coordinate

        if c.value is None:
            return None

        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        valid_neighbors = [(nx, ny) for nx, ny in neighbors if 0 <= nx < self.width and 0 <= ny < self.height]

        values = [m[nx][ny] if m[nx][ny] is not None else -1 for nx, ny in valid_neighbors]

        weighted_values = [0.8 * v for v in values]
        weighted_values.append(0.1 * c.value)  

        max_val = max(weighted_values)
        return round((c.value + self.gamma * max_val), 2)

    def populate_rewards(self, state):
        ghosts = api.ghosts(state)
        food = api.food(state)
        ghosts_states = api.ghostStates(state)

        for i in range(self.width):
            for j in range(self.height):
                counter = 0
                for ghost in ghosts:
                    if (i, j) == ghost:
                        if ghosts_states[counter][1] == 0:
                            self.map[j][i] = self.ghost_reward 
                        else:
                            self.map[j][i] = self.scared_ghost_reward
                    counter += 1
                if (i, j) in self.capsules:
                    self.map[j][i] = self.capsule_reward
                elif (i, j) in food:
                    self.map[j][i] = self.food_reward
                elif (i, j) == (9, 6) or (i, j) == (10, 6):
                    self.map[j][i] = -100000000
        
    def create_empty_map(self):
        p_map = [[" " for i in range(self.width)] for j in range(self.height)]
        for i in range(self.width):
            for j in range(self.height):
                if (i, j) in self.walls:
                    p_map[j][i] = None
                else: 
                    p_map[j][i] = self.empty_reward
        return p_map

    def distance_to_ghost(self, state, ghost):
        return util.manhattanDistance(api.whereAmI(state), ghost)
    
    def neighbours(self, location):
        neighbours = []
        x = location[0] 
        y = location[1]
        if y < self.height - 1:
            neighbours.append((x, y + 1))
        if y > 0:
            neighbours.append((x, y - 1))
        if x < self.width - 1:
            neighbours.append((x + 1, y))
        if x > 0:
            neighbours.append((x - 1, y))
        
        return neighbours
            
    def prettyDisplay(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.map[self.height - (i + 1)][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print
        