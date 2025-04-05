import os
import re
import shutil
import pandas as pd
import multiprocessing as mp
from pathlib import Path
from Utils.file_utils import count_folders, read_file, write_log


base_path = "Step7_Coverage"
step5_path = "Step5_Compilation/Results"
poj_path = Path(base_path) / "code/sim/pojPat_profuzz"
step7_rpt_path = Path(base_path) / "Population/rpt"
step7_ucd_path = Path(base_path) / "Population/ucd"
log_path = "log.txt"


def process_data(file_path: str) -> list:
    """
    Process the coverage data from the given file path.
    """
    coverage_data = []
    content = read_file(file_path)
    if content == "":
        return coverage_data
    ct_core_selection = re.search(r'ct_core\n[-]+\n(.*?)(?=\nct_|$)', content, re.DOTALL)
    if ct_core_selection:
        ct_core_content = ct_core_selection.group(1)
        patterns = {
            'BC': r'BC:\s+(\d+%)\s+\((\d+/\d+)\)',
            'EC': r'EC:\s+(\d+%)\s+\((\d+/\d+)\)',
            'TFC': r'TFC:\s+(\d+%)\s+\((\d+/\d+)\)'
        }
        for _, pattern in patterns.items():
            match = re.search(pattern, ct_core_content)
            if match:
                coverage_data.extend([match.group(1), match.group(2)])
        return coverage_data
    else:
        return coverage_data


def process_summary(count: int) -> None:
    """
    Process all coverage reports and generate a summary CSV file.
    """
    coverage_summary = []
    for i in range(count):
        file_path = Path(step7_rpt_path) / f"summary-{i}.rpt"
        coverage_data = process_data(file_path)
        if len(coverage_data) > 0:
            coverage_summary.append([i] + coverage_data)
        else:
            coverage_summary.append([i, '0%', '0/1', '0%', '0/1', '0%', '0/1'])
    
    columns = ['', 'BC_Percentage', 'BC_Ratio', 'EC_Percentage', 'EC_Ratio', 'TC_Percentage', 'TC_Ratio']
    df = pd.DataFrame(coverage_summary, columns = columns)
    df.to_csv(Path(base_path) / "Population/coverage.csv", index = False)
    write_log(log_path, "Step7 finished. Coverage test finished.\n")


def run_coverage(args) -> None:
    """
    Run the coverage test for a specific instance.
    """
    i, core_num, start_idx, offspring_size = args
    env_version = f"env/code_{str(int(i) % int(core_num))}"
    inst_path = Path(poj_path) / f"test_{i}/inst.pat"
    data_path = Path(poj_path) / f"test_{i}/data.pat"
    rtl_path = Path(base_path) / f"{env_version}/rtl"

    shutil.copy(inst_path, rtl_path)
    shutil.copy(data_path, rtl_path)

    cwd = os.getcwd()
    try:
        os.chdir(Path(base_path) / f"{env_version}/sim")
        os.system("YOUR_SIMULATION_COMMAND")
        os.system("YOUR_COVERAGE_COMMAND")
        os.rename("./single_summary/summary.rpt", f"./single_summary/summary-{i}.rpt")
    finally:
        os.chdir(cwd)

    ucd_path = Path(base_path) / f"{env_version}/sim/cov_work/design/newtest/icc.ucd"
    if os.path.exists(ucd_path):
        shutil.copy2(ucd_path, Path(step7_ucd_path) / f"test_{i}.ucd")
        if start_idx == 0:
            shutil.copy2(ucd_path, f"Results/ucd/test_{start_idx + i}.ucd")
        elif start_idx is not None:
            if i < offspring_size:
                shutil.copy2(ucd_path, f"Results/ucd/test_{start_idx + i}.ucd")


def coverage(core_num: int, start_idx: int = None, offspring_size: int = None) -> None:
    """
    Run the coverage test for the population.
    """
    if os.path.exists(poj_path):
        shutil.rmtree(poj_path)
    shutil.copytree(step5_path, poj_path)

    count = count_folders(poj_path)
    core_num = min(core_num, count)

    paths = [step7_rpt_path, step7_ucd_path]
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

    cwd = os.getcwd()
    for i in range(core_num):
        try:
            os.chdir(Path(base_path) / f"env/code_{i}/sim")
            os.system("YOUR_SIMULATION_INITIALIZATION_COMMAND")
        finally:
            os.chdir(cwd)

    for i in range(core_num):
        coverage_path = Path(base_path) / f"env/code_{i}/sim/single_summary"
        if os.path.exists(coverage_path):
            shutil.rmtree(coverage_path)
        os.makedirs(coverage_path)

    pool = mp.Pool(processes = core_num)
    for i in range(0, count, core_num):
        batch = range(i, min(i + core_num, count))
        pool.map(run_coverage, [(j, core_num, start_idx, offspring_size) for j in batch])
    pool.close()
    pool.join()

    for i in range(core_num):
        coverage_path = Path(base_path) / f"env/code_{i}/sim/single_summary"
        if os.path.exists(coverage_path):
            for file in os.listdir(coverage_path):
                source_file = Path(coverage_path) / file
                if os.path.isfile(source_file):
                    shutil.copy2(source_file, step7_rpt_path)
    process_summary(count)