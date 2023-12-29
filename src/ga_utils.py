import random


# Get elite states to save through elitism
def elitism(population, elite_num):
    elites = []
    for index in range(elite_num):
        elites.append(population[-index - 1])
    return elites


# Remove weakest states through culling
def culling(population, culling_num):
    not_culled = []
    for index in range(len(population) - culling_num):
        not_culled.append(population[-index - 1])
    return not_culled


# Get summed fitness for given population
def get_summed_fitness(population, fit_func):
    total = 0
    for state in population:
        fit_val = fit_func(state)
        total = total + abs(fit_val)
    return total


# Get chance of parent selection for given population
def get_selection_chances(population, total_fitness, fit_func):
    sel_chances = []
    for state in population:
        fit_val = fit_func(state)
        sel_chances.append(fit_val / total_fitness)
    return sel_chances


# Select parents with weighting towards higher fitness
def selection(population, fit_func, towers=True):
    parents = []
    total_fitness = get_summed_fitness(population, fit_func)
    sel_chances = get_selection_chances(population, total_fitness, fit_func)

    parent_indexes = []
    while len(parents) < 2:
        random_num = random.random()
        cumulative_prob = 0
        for index in range(len(sel_chances)):
            cumulative_prob = cumulative_prob + sel_chances[index]
            if random_num < cumulative_prob and len(parents) == 1 and\
                    ((towers and parents[0].id != population[index].id) or
                     (not towers and index not in parent_indexes)):
                parents.append(population[index])
                parent_indexes.append(index)
                break
            elif random_num < cumulative_prob and len(parents) == 0:
                parents.append(population[index])
                parent_indexes.append(index)
                break

    return parents
