import random
import copy
import time
import math

# Constants
SAMPLE_SIZE = 800
ELITISM = 160
CULLING = 240
FITNESS = 20

# Class for piece objects
class Piece:
    def __init__(self, type, width, strength, cost, id):
        self.type = type
        self.width = width
        self.strength = strength
        self.cost = cost
        self.id = id

# Class for tower objects
class Tower:
    def __init__(self, id):
        self.pieces = []
        self.id = id

# File parser for getting pieces
def towerBuildingParser(filepath):
    piecesList = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        f.close()
    count = 0
    for line in lines:
        str = line.replace('\n', '').split()
        piece = Piece(str[0], int(str[1]), int(str[2]), int(str[3]), count)
        piecesList.append(piece)
        count = count + 1
    return piecesList

# Helper function for printing given pieces
def printPieces(piecesList):
    for piece in piecesList:
        print(piece.type + " " + str(piece.width) + " " + str(piece.strength) + " " + str(piece.cost) + " " + str(piece.id))

# Generate random population states with given pieces
def generateStates(pieces):
    towers = []
    for towerNum in range(SAMPLE_SIZE):
        tower = Tower(random.random())
        towerSize = random.randrange(1, len(pieces) + 1)
        piecesToPick = list(range((len(pieces))))
        for pieceNum in range(towerSize):
            pieceRand = random.choice(piecesToPick)
            tower.pieces.append(pieces[pieceRand])
            piecesToPick.remove(pieceRand)
        towers.append(tower)
    return towers

# Print population states
def printStates(towers):
    for tower in towers:
        printState(tower)
        print()

# Print specified tower state
def printState(tower):
    print("Tower ID: " + str(tower.id))
    for piece in tower.pieces:
        print(piece.type + " " + str(piece.width) + " " + str(piece.strength) + " " + str(piece.cost))
    print("Score: " + str(fitness(tower) - FITNESS))

# Tower fitness function
def fitness(tower):
    pieces = tower.pieces
    height = len(pieces)
    totalCost = 0
    # Bottom piece must be a door and top piece must be a lookout
    if pieces[0].type != "Door" or pieces[-1].type != "Lookout":
        return FITNESS
    for index in range(height):
        # Pieces between top and bottom must be wall segments
        if index != 0 and index != height - 1 and pieces[index].type != "Wall":
            return FITNESS
        # Pieces can, at most, be as wide as the piece below it
        if index != 0 and pieces[index - 1].width < pieces[index].width:
            return FITNESS
        # Pieces can support its strength value in pieces placed above it
        if pieces[index].strength + index - height + 1 < 0:
            return FITNESS
        totalCost += pieces[index].cost
    # Valid tower fitness calculation
    return 10 + pow(height, 2) - totalCost + FITNESS

# Get summed fitness for given towers
def getSummedFitness(towers):
    total = 0
    for tower in towers:
        total = total + fitness(tower)
    return total

# Get chance of parent selection for given towers
def getSelectionChances(towers, totalFitness):
    selChances = []
    for tower in towers:
        selChances.append((fitness(tower)) / (totalFitness))
    return selChances

# Get elite states to save through elitism
def elitism(towers):
    elites = []
    for index in range(ELITISM):
        elites.append(towers[-index - 1])
    return elites

# Remove weakest states through culling
def culling(towers):
    notCulled = []
    for index in range(len(towers) - CULLING):
        notCulled.append(towers[-index - 1])
    return notCulled

# Select parents with weighting towards higher fitness
def selection(towers):
    parents = []
    totalFitness = getSummedFitness(towers)
    selChances = getSelectionChances(towers, totalFitness)
    while len(parents) < 2:
        randomNum = random.random()
        cumulativeProb = 0
        for index in range(len(selChances)):
            cumulativeProb = cumulativeProb + selChances[index]
            if randomNum < cumulativeProb and len(parents) == 1 and parents[0].id != towers[index].id:
                parents.append(towers[index])
                break
            elif randomNum < cumulativeProb and len(parents) == 0:
                parents.append(towers[index])
                break
    return parents

# Check if given piece is already on given tower
def validAddPiece(tower, newPiece):
    retVal = 1
    for piece in tower.pieces:
        if piece.id == newPiece.id:
            retVal = 0
    return retVal

# apply crossover to top, middle, and bottom components
def crossover(parents):
    # initialize children array and child towers
    children = []
    child1 = Tower(random.random())
    child2 = Tower(random.random())
    # Apply crossover for top components
    child1.pieces.append(parents[0].pieces[0])
    child2.pieces.append(parents[1].pieces[0])
    # Apply crossover for middle components
    flag = 1
    for index in range(1, len(parents[0].pieces) - 1):
        if flag == 1 and validAddPiece(child1, parents[0].pieces[index]) == 1:
            child1.pieces.append(parents[0].pieces[index])
            flag = 2
        elif validAddPiece(child2, parents[0].pieces[index]) == 1:
            child2.pieces.append(parents[0].pieces[index])
            flag = 1
    for index in range(1, len(parents[1].pieces) - 1):
        if flag == 1 and validAddPiece(child1, parents[1].pieces[index]) == 1:
            child1.pieces.append(parents[1].pieces[index])
            flag = 2
        elif validAddPiece(child2, parents[1].pieces[index]) == 1:
            child2.pieces.append(parents[1].pieces[index])
            flag = 1
    # Apply crossover for bottom components
    if validAddPiece(child1, parents[1].pieces[-1]) == 1:
        child1.pieces.append(parents[1].pieces[-1])
    elif validAddPiece(child1, parents[0].pieces[-1]) == 1:
        child1.pieces.append(parents[0].pieces[-1])
    if validAddPiece(child2, parents[0].pieces[-1]) == 1:
        child2.pieces.append(parents[0].pieces[-1])
    elif validAddPiece(child2, parents[1].pieces[-1]) == 1:
        child2.pieces.append(parents[1].pieces[-1])
    # Append children to children list
    children.append(child1)
    children.append(child2)
    return children

# randomly swap a piece between two towers
def mutation(towers, elites):
    for tower in towers:
        mutRand = random.random()
        if mutRand < 0.2:
            swapTower = random.randrange(len(towers))
            for elite in elites:
                if tower.id == elite.id or towers[swapTower].id == elite.id:
                    return towers
            insertPos = random.randrange(len(tower.pieces))
            pieceNum = random.randrange(len(towers[swapTower].pieces))
            piece = towers[swapTower].pieces[pieceNum]
            if validAddPiece(tower, piece) == 1:
                towers[swapTower].pieces.pop(pieceNum)
                tower.pieces.insert(insertPos, piece)
    return towers

# Print final statistics function
def printStatistics(bestTower, generations, foundGen):
    print("Best Solution:")
    printState(bestTower)
    print("Generations ran through: " + str(generations))
    print("Generation found on: " + str(foundGen))
    print()

# Main genetic algorithm function
def geneticAlgorithmTB(file, runTime, analysis=False):
    # Parse tower building file and randomly generate states
    pieces = towerBuildingParser(file)
    towers = generateStates(pieces)
    # Initialize best tower
    towers.sort(key = lambda tower: fitness(tower))
    bestTower = towers[len(towers) - 1]
    # Initialize timer and number of generations
    endTime = time.time() + runTime
    generations = 0
    foundGen = 0
    while time.time() < endTime:
    # while loop used for generating analysis
    # while generations < 20:
        # Add best towers to next generation (elitism) and cull worst (culling)
        nextTowers = elitism(towers)
        towers = culling(towers)
        # Get parents (selection) and add offspring to next generation (crossover)
        while len(nextTowers) < SAMPLE_SIZE:
            parents = selection(towers)
            nextTowers.extend(crossover(parents))
        # Apply chance mutations for each tower
        nextTowers.sort(key = lambda tower: fitness(tower))
        elites = elitism(nextTowers)
        nextTowers = mutation(nextTowers, elites)
        # Get best tower in next generation
        nextTowers.sort(key = lambda tower: fitness(tower))
        prevBestTower = copy.copy(bestTower)
        bestTower = nextTowers[-1]
        if fitness(bestTower) > fitness(prevBestTower) and bestTower.id != prevBestTower.id:
            foundGen = generations
        # print statistics every 10 generations
        # if analysis and generations % 1 == 0:
        printStatistics(bestTower, generations, foundGen)
        # Reset towers and increment generations
        towers = copy.copy(nextTowers)
        generations = generations + 1
    # print final statistics
    # printStatistics(bestTower, generations, foundGen)

if __name__ == "__main__":
    # genetic algorithm testing without command line arguments
    geneticAlgorithmTB("TowerBuilding.txt", 10, True)
