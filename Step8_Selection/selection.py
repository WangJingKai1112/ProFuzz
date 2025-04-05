import os
import csv
import shutil
import random
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from Utils.file_utils import read_files, write_files, write_log
from Step8_Selection.merge import merge

step5_path = "Step5_Compilation/Population"
step7_folder_path = "Step7_Coverage/Population"
step7_file_path = Path(step7_folder_path) / "coverage.csv"
results_path = "Results"
ucd_path = "Step7_Coverage/env/code_0/sim/cov_work/design/ucd"
log_path = "log.txt"

def parse_ratio(ratio: str) -> float:
    numerator, denominator = map(int, ratio.split("/"))
    return round(numerator / denominator, 4)

def cal_coverage_score(coverage_path: str, w_bc: float, w_ec: float, w_tc: float) -> list:
    coverage_score = []
    with open(coverage_path, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            bc_ratio = parse_ratio(row[2])
            ec_ratio = parse_ratio(row[4])
            tc_ratio = parse_ratio(row[6])
            score = w_bc * bc_ratio + w_ec * ec_ratio + w_tc * tc_ratio
            coverage_score.append(score)
    return coverage_score

def selection(curr_iter: int, max_iter: int, population_size: int, w_bc: float, w_ec: float, w_tc: float, start_ratio: float = 0.1, end_ratio: float = 0.8, start_idx: int = 0) -> list:
    coverage_score = cal_coverage_score(step7_file_path, w_bc, w_ec, w_tc)
    population, _ = read_files(step5_path)

    if not os.path.exists(results_path):
        os.makedirs(results_path)
    curr_time = datetime.now().strftime("%m%d_%H%M")
    folder_path = f"{results_path}/{curr_time}_{curr_iter + 1}_{max_iter}"

    # 存储selection之前的种群信息
    shutil.copytree(step7_folder_path, folder_path)
    write_log(log_path, f"{curr_iter + 1} / {max_iter} finished.")

    if not coverage_score:
        return random.sample(population, population_size)

    size = min(population_size, len(coverage_score))
    ratio = start_ratio + (end_ratio - start_ratio) * (curr_iter / max_iter)

    # elite selection
    elite_size = int(size * ratio)
    elite_indices = sorted(range(len(coverage_score)), key = lambda k: coverage_score[k], reverse = True)[: elite_size]
    elite_members = [population[i] for i in elite_indices]

    remaining_indices = [i for i in range(len(population)) if i not in elite_indices]
    remaining_score = [coverage_score[i] for i in remaining_indices]

    # roulette wheel selection
    roulette_size = size - elite_size
    if roulette_size > 0 and remaining_score:
        total_score = sum(remaining_score)
        probabilities = [score / total_score for score in remaining_score]
        roulette_indices = np.random.choice(remaining_indices, size = roulette_size, replace = False, p = probabilities)
        roulette_members = [population[i] for i in roulette_indices]
        selected_indices = elite_indices + list(roulette_indices)
    else:
        roulette_members = []
        selected_indices = elite_indices
    
    df = pd.read_csv(step7_file_path)
    selected_rows = df.iloc[selected_indices]

    selected_coverage_score = []
    for i in selected_indices:
        bc_ratio = parse_ratio(df.iloc[i][2])
        ec_ratio = parse_ratio(df.iloc[i][4])
        tc_ratio = parse_ratio(df.iloc[i][6])
        score = w_bc * bc_ratio + w_ec * ec_ratio + w_tc * tc_ratio
        selected_coverage_score.append(score)
    
    selected_path = Path(folder_path) / "selected_coverage.csv"
    selected_rows.to_csv(selected_path, index = False)

    next_population = elite_members + roulette_members

    stimuli_path = Path(folder_path) / "stimuli"
    write_files(next_population, stimuli_path)

    if start_idx == 0:
        merge_size = len(population)
    else:
        merge_size = size
    if os.path.exists(ucd_path):
        shutil.rmtree(ucd_path)
    os.makedirs(ucd_path)
    for i in range(start_idx, start_idx + merge_size):
        if os.path.exists(Path(results_path) / f"ucd/test_{i}.ucd"):
            shutil.copy2(Path(results_path) / f"ucd/test_{i}.ucd", Path(ucd_path) / f"test_{i}.ucd")
    merge(folder_path, start_idx, merge_size)

    write_log(log_path, f"Step8 finished. Select {len(next_population)} members.\n")

    return next_population