import os
import shutil
from pathlib import Path


env_path = "Step7_Coverage/env/code_0/sim"
new_test_path = "cov_work/design/newtest"
all_test_path = "cov_work/design/all_test"
new_all_test_path = "cov_work/design/new_all_test"
ucd_path = "cov_work/design/ucd"


def merge(results_path: str, start_idx: int, size: int) -> None:
    """
    Merges coverage data into a report.
    """
    cwd = os.getcwd()
    os.chdir(env_path)

    if start_idx == 0:
        if os.path.exists(new_test_path):
            shutil.rmtree(new_test_path)
        os.makedirs(new_test_path)

        if os.path.exists(all_test_path):
            shutil.rmtree(all_test_path)
        os.makedirs(all_test_path)
        shutil.copy2(Path(ucd_path) / "test_0.ucd", Path(all_test_path) / "icc.ucd")
    
    for i in range(start_idx, start_idx + size):
        if not os.path.exists(Path(ucd_path) / f"test_{i}.ucd"):
            continue
        shutil.copy2(Path(ucd_path) / f"test_{i}.ucd", Path(new_test_path) / "icc.ucd")
        os.system("YOUR_MERGE_COMMAND")
        shutil.rmtree(all_test_path)
        os.rename(new_all_test_path, all_test_path)
        os.system("YOUR_MERGE_REPORT_COMMAND")

    os.chdir(cwd)
    shutil.copy2(Path(env_path) / "summary/summary.rpt", Path(results_path) / "summary_merged.rpt")