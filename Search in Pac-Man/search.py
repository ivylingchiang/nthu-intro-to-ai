# search.py
# ---------
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


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
from util import Stack 

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem: SearchProblem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    "*** YOUR CODE HERE ***"
    # TODO: Implement depthFirstSearch (Q1)
    """
    thoughts:
    1. get the node in stack (last in first out)
    2. check if the node is the goal state => Yes, then return
    3. if not, visited the node, put the unvisited neighber into the stack
    """
    curPath = [] 
    curNode = problem.getStartState() 
    
    # if the start state is the goal state => return
    if problem.isGoalState(curNode):
        return curPath
    
    # create a buffer to store the node we want to visit
    Buffer = Stack()
    Buffer.push((curNode, curPath))
    
    # create a set to store the visited node
    visited = set()
    while not Buffer.isEmpty():
        # get the node in the buffer
        curNode, curPath = Buffer.pop()
        
        # check if the node is the goal state
        if problem.isGoalState(curNode):
            return curPath # if the goal state is found, return the path
        
        visited.add(curNode) # mark the node as visited
        
        for s in problem.getSuccessors(curNode): # get the neighbors of the node
            if s[0] not in visited:
                Buffer.push((s[0], curPath + [s[1]]))
        
    return [] # if the goal state is not found, return []
    # util.raiseNotDefined()

def breadthFirstSearch(problem: SearchProblem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    # TODO: Implement breadthFirstSearch (Q2)
    """
    thoughts:
    1. get the node in queue (first in first out)
    2. check if the node is the goal state => Yes, then return
    3. if not, visited the node, put the unvisited neighber into the queue
    """
    curPath = []
    curNode = problem.getStartState()
    
    # if the start state is the goal state => return
    if problem.isGoalState(curNode):
        return curPath
    
    # create a queue to store the node we want to visit
    Buffer = util.Queue()
    Buffer.push((curNode, curPath))
    
    # create a set to store the visited node
    visited = set()
    visited.add(curNode) # mark the start node as visited
    
    while not Buffer.isEmpty():
        # get the node in the buffer
        curNode, curPath = Buffer.pop()
        
        # check if the node is the goal state
        if problem.isGoalState(curNode):
            return curPath # if the goal state is found, return the path
        
        for s in problem.getSuccessors(curNode): # get the neighbors of the node
            if s[0] not in visited:
                visited.add(s[0])
                Buffer.push((s[0], curPath + [s[1]]))
    
    return [] # if the goal state is not found, return []
    # util.raiseNotDefined()

def uniformCostSearch(problem: SearchProblem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    # TODO: Implement uniformCostSearch (Q4)
    """
    thoughts:
    1. get the node in priority queue ()
    2. check if the node is the goal state => Yes, then return
    3. if not, visited the node, put the unvisited neighber into the priority queue count the cost
    4. if the node is visited, check if the cost is less than the previous one, if yes, update the cost
    """
    curPath = []
    curNode = problem.getStartState()
    
    Buffer = util.PriorityQueue()
    Buffer.push((curNode, curPath), 0) # push the start node into the priority queue(Node, Path, Cost)
    
    visited = set()
    
    while not Buffer.isEmpty():
        curNode, curPath = Buffer.pop() # get the node in the priority queue(cost less first)
        
        if problem.isGoalState(curNode):
            return curPath # if the goal state is found, return the path
        visited.add(curNode) # mark the node as visited
        
        PathBuffer = [i[2][0] for i in Buffer.heap] # get the path of the node in the priority queue(the idea from #pspanoudakis)
        
        for s in problem.getSuccessors(curNode): # get the neighbors of the node
            NewPath = curPath + [s[1]]
            if s[0] not in visited and s[0] not in PathBuffer:
                Buffer.push((s[0], NewPath),problem.getCostOfActions(NewPath)) # push
            else:
                # same node but different path
                for i in range(0, len(PathBuffer)):
                    if s[0] == PathBuffer[i]:
                        NewCost = problem.getCostOfActions(NewPath)
                        OldCost = Buffer.heap[i][0]
                        if OldCost > NewCost:
                            # update the cost of the node
                            Buffer.heap[i] = (OldCost, Buffer.heap[i][1], (s[0], NewPath))
                            Buffer.update((s[0], NewPath), NewCost)
    return []
    # util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0


def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    # TODO: Implement aStarSearch (Q4)
    """
    thoughts:
    1. get the node in priority queue ()
    2. use Manhattan Distance as the heuristic function
    3. check if the node is the goal state => Yes, then return
    4. if not, visited the node, put the unvisited neighber into the priority queue count the cost
    """
    curPath = []
    curNode = problem.getStartState()
    
    Buffer = util.PriorityQueue()
    Buffer.push((curNode, curPath), heuristic(curNode,problem)) # push the start node into the priority queue(Node, Path, Cost)
    
    visited = set()
    
    while not Buffer.isEmpty():
        curNode, curPath = Buffer.pop()
        
        if problem.isGoalState(curNode):
            return curPath
        visited.add(curNode)
        
        PathBuffer = {item[2][0]: item[0] for item in Buffer.heap}  # Dictionary of states and their costs(idea from #pspanoudakis)
        
        for neighbor, action, cost in problem.getSuccessors(curNode):
            if neighbor in visited:
                continue  # already visited nodes
            
            #! Important Part
            newPath = curPath + [action]  # Extend the current path
            newCost = problem.getCostOfActions(newPath) + heuristic(neighbor, problem) # Calculate the cost of the new path
            
            if neighbor not in PathBuffer or PathBuffer[neighbor] > newCost:
                Buffer.push((neighbor, newPath), newCost) # Push the new path into the priority queue
    
    return []
    # util.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
