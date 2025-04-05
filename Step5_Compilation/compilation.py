import os
import shutil
from pathlib import Path
from Utils.file_utils import write_files, read_files, write_log

test_case = "test_profuzz"
base_path = "Step5_Compilation"
population_path = Path(base_path) / "Population"
results_path = Path(base_path) / "Results"
case_path = Path(base_path) / f"openc910/smart_run/tests/cases/{test_case}/{test_case}.c"
makefile_path = Path(base_path) / "openc910/smart_run"
data_path = Path(makefile_path) / "work/data.pat"
inst_path = Path(makefile_path) / "work/inst.pat"
obj_path = Path(makefile_path) / f"work/{test_case}.obj"
runtime_log_path = Path(makefile_path) / f"work/{test_case}_build.case.log"
log_path = "log.txt"


def single_compilation(test_path: str, output_folder: str) -> int:
    """
    Compile a single test case and check if the compilation is successful.
    """
    shutil.copy(test_path, case_path)
    os.system(f"make -s -C {makefile_path} buildcase CASE={test_case}")
    if output_folder == "":
        if os.path.exists(data_path):
            return 1
        else:
            return 0
    else:
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
        os.makedirs(output_folder)
        if os.path.exists(inst_path):
            shutil.copy(inst_path, output_folder)
        if os.path.exists(obj_path):
            shutil.copy(obj_path, output_folder)
        if os.path.exists(runtime_log_path):
            shutil.copy(runtime_log_path, output_folder)
        if os.path.exists(data_path):
            shutil.copy(data_path, output_folder)
            return 1
        else:
            return 0


def compilation(population_new: list = [], population_ori: list = [], start_idx: int = None) -> None:
    """
    Compile the test cases in the population.
    """
    if os.path.exists(results_path):
        shutil.rmtree(results_path)
    os.makedirs(results_path)
    
    population = population_new + population_ori
    if len(population) == 0:
        population, _ = read_files(population_path)
    else:
        if os.path.exists(population_path):
            shutil.rmtree(population_path)
        write_files(population, population_path)

    if start_idx is not None:
        for idx in range(len(population_new)):
            if start_idx == 0:
                shutil.copy2(Path(population_path) / f"test_{idx}.c", f"Results/Population/test_{start_idx + len(population_ori) + idx}.c")
            else:
                shutil.copy2(Path(population_path) / f"test_{idx}.c", f"Results/Population/test_{start_idx + idx}.c")

    results = []
    for i in range(len(population)):
        test_path = Path(population_path) / f"test_{i}.c"
        output_folder = Path(results_path) / f"test_{i}"
        results.append(single_compilation(test_path, output_folder))
    write_log(log_path, f"Step5 finished. Compilation completed and results: {results}.\n")