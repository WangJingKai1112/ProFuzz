import math
from Step2_Mating.mating import mating
from Utils.file_utils import write_log


log_path = "log.txt"


def rebooting(debug_result: list, pairs: list, population_size: int) -> tuple:
    """
    Rebooting the inidividuals if they can not debugged.
    """
    reboot_idx, reboot_pairs = [], []
    reboot_num = 0
    for i in range(len(debug_result)):
        if debug_result[i] == 0:
            reboot_idx.append(i)
            reboot_num += 1
    
    reboot_pairs = mating(population_size, [], math.ceil(reboot_num / 2))
    
    if reboot_idx != []:
        write_log(log_path, f"Rebooting results: {reboot_idx}; {reboot_num}; {reboot_pairs}")
        write_log(log_path, "Step6_2 finished. Rebooting required.\n")
    else:
        write_log(log_path, "Step6_2 finished. No rebooting required.\n")

    return reboot_idx, reboot_pairs