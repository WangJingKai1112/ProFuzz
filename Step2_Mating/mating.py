import random
from Utils.file_utils import write_log


log_path = "log.txt"


def random_select(size: int, idx_1: int) -> int:
    """
    Randomly select an index from the population.
    """
    idx_2 = random.choice(range(size))
    while idx_2 == idx_1:
        idx_2 = random.choice(range(size))
    return idx_2


def mating(population_size: int, num_pairs: int) -> list:
    """
    Select pairs of indices for mating.
    """
    pairs = []
    for _ in range(num_pairs):
        idx_1 = random_select(population_size, -1)
        idx_2 = random_select(population_size, idx_1)
        pairs.append([idx_1, idx_2])

    if pairs != []:
        write_log(log_path, f"Selected pairs: {pairs}.")
        write_log(log_path, f"Step2 finished. Selected {len(pairs)} pairs.\n")
    return pairs
