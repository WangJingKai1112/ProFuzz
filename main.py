import time
import argparse
from Step1_Initialization.initialization import initialize
from Step2_Mating.mating import mating
from Step3_Crossover.crossover import crossover
from Step4_Mutation.mutation import mutation
from Step5_Compilation.compilation import compilation
from Step6_Debugging_and_Rebooting.debugging import debugging
from Step6_Debugging_and_Rebooting.rebooting import rebooting
from Step7_Coverage.coverage import coverage
from Step8_Selection.selection import selection
from Utils.file_utils import write_log

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--population_size", type = int, default = 60) # Number of population
    parser.add_argument("--max_generation", type = int, default = 40) # Maximum number of generations

    parser.add_argument("--mating_pairs", type = int, default = 30) # Number of parent pairs (offspring = 2 * mating_pairs)

    parser.add_argument("--mutation_steps", type = int, default = 3) # Maximum step of mutation
    
    parser.add_argument("--max_debug_loop", type = int, default = 3) # Maximum round of debugging

    parser.add_argument("--core_num", type = int, default = 15) # Number of parallel processes for coverage testing

    parser.add_argument("--bc_weight", type = float, default = 0.34) # Weight of coverage metrics
    parser.add_argument("--ec_weight", type = float, default = 0.33)
    parser.add_argument("--tc_weight", type = float, default = 0.33)

    parser.add_argument("--start_ratio", type = float, default = 0.1)  # Initial elite selection ratio
    parser.add_argument("--end_ratio", type = float, default = 0.8)  # Final elite selection ratio

    args = parser.parse_args()
    population_size = args.population_size
    max_generation = args.max_generation
    mating_pairs = args.mating_pairs
    mutation_steps = args.mutation_steps
    max_debug_loop = args.max_debug_loop
    core_num = args.core_num
    bc_weight = args.bc_weight
    ec_weight = args.ec_weight
    tc_weight = args.tc_weight
    start_ratio = args.start_ratio
    end_ratio = args.end_ratio

    population, offspring, next_generation = [], [], []
    reboot_idx = []
    start_idx = 0
    log_path = "log.txt"
    with open(log_path, "w"):
        pass

    start_time = time.time()

    population = initialize("csmith", population_size)
    # population = initialize("llm", population_size)

    for curr_generation in range(max_generation):
        write_log(log_path, f"---------- Generation {curr_generation + 1} / {max_generation} ----------\n")

        pairs = mating(population_size, mating_pairs)

        while True:
            offspring = crossover(population, pairs, offspring, reboot_idx)
            offspring = mutation(offspring, mutation_steps, reboot_idx)

            compilation(offspring)

            debug_res, offspring = debugging(max_debug_loop)
            reboot_idx, reboot_pairs = rebooting(debug_res, pairs, population_size)
            if len(reboot_idx) == 0:
                break
            pairs = reboot_pairs

        compilation(offspring, population, start_idx)
        coverage(core_num, start_idx, len(offspring))

        next_gen = selection(curr_generation, max_generation, population_size, bc_weight, ec_weight, tc_weight, start_ratio, end_ratio, start_idx)

        if start_idx == 0:
            start_idx += population_size
        start_idx += mating_pairs * 2

        cost_time = int(time.time() - start_time)
        write_log(log_path, f"Merge size = {start_idx}, Merge time = {cost_time // 3600} h {(cost_time % 3600) // 60} m {cost_time % 60} s.\n")