import copy
import time
import numpy as np
import random

from ga_utils import elitism, culling, selection

# Constants
SAMPLE_SIZE = 300
ELITISM = 75
CULLING = 175
MUTATION = 0.75

def number_allocation_parser(filepath):
    numbers = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        f.close()
    for line in lines:
        numbers.append(float(line.replace('\n', '')))
    return numbers


def print_numbers(numbers):
    for number in numbers:
        print(number)


def initialize_population(list):
    population = []

    for i in range(SAMPLE_SIZE):
        temp = np.array(list)
        np.random.shuffle(temp)
        temp = temp.reshape((4, 10))
        population.append(temp)

    return population


def gen_occurrence_dict(pop_list):
    occur_dict = {}
    for num in pop_list:
        if num in occur_dict:
            occur_dict[num] += 1
        else:
            occur_dict[num] = 1

    return occur_dict


def gen_occurrence_dict_from_bins(bins):
    pop_list = bins.reshape(40)
    return gen_occurrence_dict(pop_list)


# Calculate the fitness score of the bins
def fitness(bins):
    binOne = 1
    binTwo = 0
    for x in bins[0]:
        binOne = binOne * x

    for y in bins[1]:
        binTwo += y

    binThree = max(bins[2]) - min(bins[2])

    score = binOne + binTwo + binThree
    return score if score > 0 else 0


# # Select Parents and returns the rows of the parents
# def select_parent_rows(fitness):
#     parents = []
#     if fitness[0] > fitness[1] and fitness[0] > fitness[2] and fitness[0] > fitness[3]:
#         parents.append(0)
#         if fitness[1] > fitness[2] and fitness[1] > fitness[3]:
#             parents.append(1)
#         elif fitness[2] > fitness[3]:
#             parents.append(2)
#         else:
#             parents.append(3)
#     elif fitness[1] > fitness[2] and fitness[1] > fitness[3]:
#         parents.append(1)
#         if fitness[2] > fitness[3]:
#             parents.append(2)
#         else:
#             parents.append(3)
#     else:
#         parents.append(2)
#         parents.append(3)
#
#     return parents


# Creates offspring of the parents
def generate_offspring(parents: np.array, occurrences: dict):
    offsprings = []

    # Crossover sections of the parent to form the offspring
    for index, parent in enumerate(parents):
        offsprings.append(parent.copy())

        offsprings[index][0] = parents[(index + 1) % len(parents)][0]
        offsprings[index][2] = parents[(index + 1) % len(parents)][2]

    # Resolve illegal children crossover issues
    for offspring in offsprings:
        offspring_occurs = gen_occurrence_dict_from_bins(offspring)

        # Based on how many occurrences there should in the bins
        # determine if there are any bins that have too many numbers occurring
        too_many_nums = []
        too_few_nums = []
        for value in occurrences.keys():
            # Correct amount of occurrences are taking place for this value
            if value in offspring_occurs and occurrences[value] == offspring_occurs[value]:
                continue
            # There is an incorrect number of occurrences for this value
            else:
                # There are zero occurrences of this value
                if value not in offspring_occurs:
                    offspring_occurs[value] = 0

                # Determine if there is too many of the current value, or too few
                needed_count = occurrences[value] - offspring_occurs[value]
                curr_list = too_few_nums
                if needed_count < 0:
                    curr_list = too_many_nums

                # Add the value to the corresponding too many/few list
                curr_list.extend([value] * abs(needed_count))

        # Resolve illegal children if there are any
        np.random.shuffle(too_many_nums)
        np.random.shuffle(too_few_nums)
        while len(too_many_nums) > 0 or len(too_few_nums) > 0:
            few_value = too_few_nums.pop()
            many_value = too_many_nums.pop()

            # Randomly select one of the values that is occurring too many times
            many_value_indexes = np.where(offspring == many_value)
            chosen_many_index = random.randrange(len(many_value_indexes))
            chosen_row = many_value_indexes[0][chosen_many_index]
            chosen_col = many_value_indexes[1][chosen_many_index]

            # Replace the too many occurring value with the too few value
            offspring[chosen_row][chosen_col] = few_value

    return offsprings


def mutation(population, elites):
    for bins in population:
        mut_rand = random.random()
        # Continue if a mutation should randomly occur
        if mut_rand < MUTATION:
            # Skip over the elites
            for elite in elites:
                if np.array_equal(bins, elite):
                    return population

            # Randomly determine positions to swap two values
            row_1, row_2 = 0, 0
            col_1, col_2 = 0, 0
            while row_1 == row_2:
                row_1, row_2 = random.randrange(len(bins)), random.randrange(len(bins))
                col_1, col_2 = random.randrange(len(bins[0])), random.randrange(len(bins[0]))

            # Reassign and swap values
            temp_val = bins[row_1][col_1]
            bins[row_1][col_1] = bins[row_2][col_2]
            bins[row_2][col_2] = temp_val

    return population


def find_best_allocation(number_list, run_time):
    start = time.time()
    generation = 0

    # Generate population of bins
    occur_map = gen_occurrence_dict(number_list)
    population = initialize_population(number_list)
    population.sort(key=fitness)

    # Output for the program
    best_generation = 0
    best_population = population[len(population) - 1]
    best_fitness = fitness(best_population)

    # while generation < 20:
    # print("Best fitness: ", best_fitness)
    # print("Generations ran through: ", generation)
    # print("Generation found on: ", best_generation)

    while run_time > (time.time() - start):
        # Elitism and culling
        next_pop = elitism(population, ELITISM)
        remaining_bins = culling(population, CULLING)

        # Get parents (selection) and add offspring to next generation (crossover)
        while len(next_pop) < SAMPLE_SIZE:
            parents = selection(remaining_bins, fitness, False)
            next_pop.extend(generate_offspring(parents, occur_map))

        # Apply chance mutations for each tower
        next_pop.sort(key=fitness)
        elites = elitism(next_pop, ELITISM)
        next_pop = mutation(next_pop, elites)

        generation += 1

        # Get best tower in next generation
        next_pop.sort(key=fitness)
        curr_best_pop = next_pop[-1]
        curr_best_fit = fitness(curr_best_pop)
        if curr_best_fit > best_fitness:
            best_generation = generation
            best_fitness = curr_best_fit
            best_population = copy.copy(curr_best_pop)

        # Reset population and increment generations
        population = copy.copy(next_pop)

        # print("Best fitness: ", best_fitness)
        # print("Generations ran through: ", generation)
        # print("Generation found on: ", best_generation)

    return best_population, best_fitness, generation, best_generation

if __name__ == "__main__":
    print(fitness(list([
        [-1,-2,-3,-1,-2,-5,1,8,0,7],
        [0,-9,1,-3,-4,3,7,-5,5,1],
        [-3,10,-8,2,3,4,-7,1,-8,-5],
        [2,-7,5,4,-2,-9,-8,6,-6,4]
    ])))

