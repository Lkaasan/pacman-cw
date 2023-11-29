from pacman import Directions
from game import Agent
import api
import random
import game
import util
import time


"""
Class to represent a cell in the map
"""
class Cell:

    """
    Constructor for the Cell class
    @param value with type Double: reward value of the cell
    @param coordinate with type Tupele (int, int)
    """
    def __init__(self, value, coordinate):
        self.value = value
        self.coordinate = coordinate

class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman" 
        
        #Initiallising class variables
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
        
        #setting game parameters to class variables 
        self.corners = api.corners(state)
        self.walls = api.walls(state)
        self.width = self.corners[1][0] + 1
        self.height = self.corners[2][1] + 1
        self.map = self.create_empty_map()
        

    def final(self, state):
        self.map = None
        print "Looks like the game just ended!"

    def getAction(self, state):
        self.capsules = api.capsules(state)
        self.map = self.create_empty_map()
        self.populate_rewards(state)
        self.v_iteration(state)
        
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
            
        pacman_location = api.whereAmI(state)
        [scores, actions] = self.get_score_for_actions(legal, pacman_location[0], pacman_location[1])
        
        if all(score == scores[0] for score in scores):
            self.move_towards_closest_food(legal, state)
            [scores, actions] = self.get_score_for_actions(legal, pacman_location[0], pacman_location[1])
            if all(score == scores[0] for score in scores):
                return api.makeMove(random.choice(legal), legal)
            
        max_score_index = scores.index(max(scores))
        choice = actions[max_score_index]
        return api.makeMove(choice, legal)
    
    """
        Function that alters the map rewards when pacman is stuck with no path, to help move
        him towards the nearest food
        @param legal of type list: a list of all legal moves 
        @param state, the state of the game
    """
    def move_towards_closest_food(self, legal, state):
        food = api.food(state)
        pacman = api.whereAmI(state)
        closest_food = self.find_closest_food(pacman, food)
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

    """
    Finds the closest food to pacman at the current state of the game
    @param pacman of type tuple [int, int]: the location of pacman
    @param food of type list: a list of food in the current game state
    @return closest_food of type tuple: location of closest food
    """
    def find_closest_food(self, pacman, food):
        distance = 100
        closest_food = ()
        for f in food:
            d = util.manhattanDistance(pacman, f)
            if d < distance:
                distance = d
                closest_food = f
        return closest_food

    """
    Gets the actions pacman can take and the score of those actions
    @param legal of type list: a list of all legal moves
    @param x of type int: x coordinate
    @param y of type int: y coordinate
    @return scores of type list: list of scores
    @return actions of type list: list of actions
    """
    def get_score_for_actions(self, legal, x, y):
        scores = []
        actions = []
        for a in legal:
            if a is Directions.NORTH:
                scores.append(self.map[y + 1][x])
                actions.append(a)
            elif a is Directions.SOUTH:
                scores.append(self.map[y - 1][x])
                actions.append(a)
            elif a is Directions.EAST:
                scores.append(self.map[y][x + 1])
                actions.append(a)
            elif a is Directions.WEST:
                scores.append(self.map[y][x - 1])
                actions.append(a)

        return scores, actions

    """
    Implments value iteration of the map for 10 iterations
    @param state: current state of the game
    """
    def v_iteration(self, state):
        if self.height == 7:
           self.small_map_update_ghost_values(state)
        else:
            self.update_ghost_rewards(state)
        for x in range (0, 10):
            empty_map = self.create_empty_map()
            temp_map = self.map
            for i in range(self.height):
                for j in range(self.width):
                    c = Cell(self.map[i][j], (i, j))
                    empty_map[i][j] = self.bellmann_equation(c, temp_map)
            self.map = empty_map
        

    """
    Updates the reward values for the space around the ghost, negative if ghost is normal 
    and posive if ghost is scared
    @param state: current state of the game
    """
    def update_ghost_rewards(self, state): 
        ghosts = api.ghosts(state)
        ghosts_with_states = api.ghostStates(state)
        counter = 0
        for g in ghosts:
            ghost_neighbours = self.neighbours(g, 1)
            for n in ghost_neighbours:
                x = int(n[0])
                y = int(n[1])
                if self.map[y][x] is not None:
                    if ghosts_with_states[counter][1] == 0:
                        self.map[y][x] = self.ghost_reward / 2
                    else:
                        self.map[y][x] = self.scared_ghost_reward / 2
            counter += 1
    
    
    """
    Updates the reward values for the space around the ghost on the small map
    @param state: current state of the game 
    """
    def small_map_update_ghost_values(self, state):
        ghosts = api.ghosts(state)
        ghosts_with_states = api.ghostStates(state)
        pacman_location = api.whereAmI(state)
        pacman_neighbours = self.neighbours(pacman_location, 0)
        for ghost in ghosts:
            neighbours = self.neighbours(ghost, 0)
            for n in neighbours:
                x = int(n[0])
                y = int(n[1])
                if self.map[y][x] is not None:
                    self.map[y][x] = self.ghost_reward / 2
            
    """
    Implements the bellmann equation of a cell
    @param c type Cell: the cell
    @param m of type 2D Array: the current map
    @return new value of the cell, type float
    """
    def bellmann_equation(self, c, m):
        x, y = c.coordinate 

        if c.value is None:
            return None

        neighbors = self.neighbours(c.coordinate, 0)
        valid_neighbors = [(nx, ny) for nx, ny in neighbors if 0 <= nx < self.width and 0 <= ny < self.height]

        values = [m[nx][ny] if m[nx][ny] is not None else -1 for nx, ny in valid_neighbors]

        weighted_values = [0.8 * v for v in values]
        weighted_values.append(0.1 * c.value)  

        m_val = max(weighted_values)
        return round((c.value + self.gamma * m_val), 2)

    """
    Populate the initial reward values of the map depending on the game constrants
    @param state: current state of the game
    """
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
                    self.map[j][i] = -1000
        
    """
    Creates an empty map, only with empy cells and walls
    @return p_map: empty map
    """
    def create_empty_map(self):
        p_map = [[" " for i in range(self.width)] for j in range(self.height)]
        for i in range(self.width):
            for j in range(self.height):
                if (i, j) in self.walls:
                    p_map[j][i] = None
                else: 
                    p_map[j][i] = self.empty_reward
        return p_map
    """
    Returns the neighbouring cells of a location, can either be a small size of large size
    @param location of type tuple (int, int): location for neighbours to be found
    @param t of type int: 0 for small range and 1 for large range
    @return neighbours of type list: a list of neighbouring cells
    """
    def neighbours(self, location, t):
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
            
        if t == 1:
            if y < self.height - 2:
                neighbours.append((x, y + 2))
            if y > 1:
                neighbours.append((x, y - 2))
            if x < self.width - 2:
                neighbours.append((x + 2, y))
            if x > 1:
                neighbours.append((x - 2, y))

            if y < self.height - 1 and x < self.width - 1:
                neighbours.append((x + 1, y + 1))
            if y > 0 and x < self.width - 1:
                neighbours.append((x + 1, y - 1))
            if x < self.width - 1 and y > 0:
                neighbours.append((x + 1, y - 1))
            if x > 0 and y > 0:
                neighbours.append((x - 1, y - 1))

        return neighbours
        