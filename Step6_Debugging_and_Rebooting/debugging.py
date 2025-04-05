import time
from pathlib import Path
from Utils.client_config import client_config
from Utils.file_utils import count_files, read_files, read_file, write_file, write_log
from Step5_Compilation.compilation import compilation
from Step6_Debugging_and_Rebooting.prompt import extractLogFormat, extract_log_prompt
from Step6_Debugging_and_Rebooting.prompt import fixSuggestionsFormat, fix_suggestions_prompt
from Step6_Debugging_and_Rebooting.prompt import fixCodeFormat, fix_code_prompt


client = client_config()
population_path = "Step5_Compilation/Population"
results_path = "Step5_Compilation/Results"
log_path = "log.txt"


def debug_loop(idx: int, max_debug_loop: int) -> int:
    max_retries = 10
    retry_delay = 10
    curr_debug_loop = 0
    test_path = Path(results_path) / f"test_{idx}"
    while True:
        if curr_debug_loop >= max_debug_loop:
            return 0
        elif count_files(test_path) > 1:
            return 1
        code = read_file(Path(population_path) / f"test_{idx}.c")
        log = read_file(Path(test_path) / "test_llm_build.case.log")

        write_log(log_path, f"Debugging test_{idx}.c loop: {curr_debug_loop}.")

        log_message = extract_log_prompt(log)
        for attempt in range(max_retries):
            try:
                log_response = client.beta.chat.completions.parse(
                    model = "YOUR_MODEL_NAME",
                    messages = [
                        {"role": "user", "content": log_message}
                    ],
                    temperature = 0.2,
                    response_format = extractLogFormat,
                    max_completion_tokens = 16384,
                )
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    write_log(log_path, f"Error: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise e
        log = log_response.choices[0].message.parsed.log

        suggestions_message = fix_suggestions_prompt(code, log)
        for attempt in range(max_retries):
            try:
                suggestions_response = client.beta.chat.completions.parse(
                    model = "YOUR_MODEL_NAME",
                    messages = [
                        {"role": "user", "content": suggestions_message}
                    ],
                    temperature = 0.2,
                    response_format = fixSuggestionsFormat,
                    max_completion_tokens = 16384,
                )
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    write_log(log_path, f"Error: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise e
        suggestions = suggestions_response.choices[0].message.parsed.suggestions

        for suggestion in suggestions:
            debug_message = fix_code_prompt(code, suggestion)
            for attempt in range(max_retries):
                try:
                    debug_response = client.beta.chat.completions.parse(
                        model = "YOUR_MODEL_NAME",
                        messages = [
                            {"role": "user", "content": debug_message}
                        ],
                        temperature = 0.2,
                        response_format = fixCodeFormat,
                        max_completion_tokens = 16384,
                    )
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        write_log(log_path, f"Error: {e}. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        raise e
            code = debug_response.choices[0].message.parsed.fixed_code

        write_file(code, Path(population_path) / f"test_{idx}.c")
        compilation()
        curr_debug_loop += 1


def debugging(max_debug_loop: int) -> tuple:
    """
    Debugging the individuals if they can not be compiled.
    """
    results, offspring = [], []
    count = count_files(population_path)
    for i in range(count):
        results.append(debug_loop(i, max_debug_loop))
    offspring, _ = read_files(population_path)
    write_log(log_path, f"Step6_1 finished. Debugging completed and results: {results}.\n")
    return results, offspring