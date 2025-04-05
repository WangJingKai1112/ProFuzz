import os
import shutil
from pathlib import Path
from Step1_Initialization.prompt import llmFormat, llm_prompt
from Step5_Compilation.compilation import single_compilation
from Utils.client_config import client_config
from Utils.file_utils import read_file, read_files, write_file, count_tokens, write_log


population_path = "Results/Population"
log_path = "log.txt"
CSMITH_MIN_TOKENS = 1024
CSMITH_MAX_TOKENS = 6192
LLM_MIN_TOKENS = 2048
client_config = client_config()


def generate_csmith(size: int) -> None:
    """
    Generate C code using Csmith.
    """
    package_path = "Libs/csmith"
    os.system(f"cd {package_path}")
    for idx in range(size):
        c_file = Path(population_path) / f"test_{idx}.c"
        while True:
            os.system(f"csmith > {c_file}")
            code = read_file(c_file)
            if count_tokens(code) <= CSMITH_MAX_TOKENS and count_tokens(code) >= CSMITH_MIN_TOKENS:
                if single_compilation(c_file, "") == 1:
                    write_file(code, c_file)
                    write_log(log_path, f"Generated test_{idx}.c by Csmith, token count: {count_tokens(code)}.")
                    break


def generate_llm(size: int) -> None:
    """
    Generate C code using LLM.
    """
    for idx in range(size):
        c_file = Path(population_path) / f"test_{idx}.c"
        while True:
            user_message = llm_prompt()
            response = client_config.beta.chat.completions.parse(
                model = "YOUR_MODEL_NAME",
                messages = [
                    {"role": "user", "content": user_message}
                ],
                temperature = 0.8,
                response_format = llmFormat,
                max_tokens = LLM_MIN_TOKENS,
            )
            code = response.choices[0].message.parsed.code
            write_file(code, c_file)
            if single_compilation(c_file, "") == 1:
                write_log(log_path, f"Generated test_{idx}.c by LLM.")
                break


def initialize(gen_type: str, gen_size: int) -> list:
    """
    Initialize the population using the specified generator.
    """
    generators = {
        "csmith": generate_csmith,
        "llm": generate_llm,
    }
    if os.path.exists(population_path):
        shutil.rmtree(population_path)
    os.makedirs(population_path)

    if gen_type in generators:
        generators[gen_type](gen_size)
    else:
        raise ValueError(f"Invalid generator type: {gen_type}")

    population, _ = read_files(population_path)
    write_log(log_path, f"Step1 finished. Generated {len(population)} programs.\n")
    return population