import argparse
from NumberAllocation import *
from TowerBuilding import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'problem',
        help="--problem : the problem you want to do",
        type=int,
        choices=[1, 2]
    )
    parser.add_argument(
        'file',
        help="--file : the name of the file you want to be read in",
        type=str
    )
    parser.add_argument(
        'time',
        help="--time : the amount of time to run the problem",
        type=int
    )

    args = parser.parse_args()
    print("Problem: " + str(args.problem))
    print("Filename: " + args.file)
    print("Time: " + str(args.time))

    if args.problem == 1:
        list = number_allocation_parser(args.file)
        best_solution, best_fitness, gen_num, gen_found = find_best_allocation(list, args.time)
        print("Best Solution: ")
        print(best_solution)
        print("Best fitness: ", best_fitness)
        print("Generations ran through: ", gen_num)
        print("Generation found on: ", gen_found)
    elif args.problem == 2:
        print("Do problem 2!")
        geneticAlgorithmTB(args.file, args.time)
