import os
import shutil
import tiktoken
from pathlib import Path
from Utils.format_utils import remove_comments, format_code


def count_files(path: str) -> int:
    """
    Count the number of files in the given path.
    """
    files = os.listdir(path)
    count = 0
    for file in files:
        if os.path.isfile(Path(path) / file):
            count += 1
    return count


def count_folders(path: str) -> int:
    """
    Count the number of folders in the given path.
    """
    folders = os.listdir(path)
    count = 0
    for folder in folders:
        if os.path.isdir(Path(path) / folder):
            count += 1
    return count


def read_file(path: str) -> str:
    """
    Read the given file and return its content.
    For .c files, remove comments and format the code.
    """
    if os.path.exists(path):
        with open(path, "r") as f:
            file = f.read()
        if path.suffix == ".c":
            file = remove_comments(file)
            file = format_code(file)
        return file
    return ""


def read_files(path: str) -> tuple:
    """
    Read all files in the given path and return their content as a list.
    """
    files = []
    count = count_files(path)
    for i in range(count):
        file_path = Path(path) / f"test_{i}.c"
        file = read_file(file_path)
        files.append(file)
    return files, count


def write_file(file: str, path: str) -> None:
    """
    Write a file to the given path.
    For .c files, remove comments and format the code.
    """
    if os.path.exists(path):
        os.remove(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if path.suffix == ".c":
        file = remove_comments(file)
        file = format_code(file)
    with open(path, "w") as f:
        f.write(file)


def write_files(files: list, path: str, idx: list = []) -> None:
    """
    Write multiple files to the given path.
    """
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    if len(idx) == 0:
        idx = list(range(len(files)))
    for i in idx:
        file_path = Path(path) / f"test_{i}.c"
        write_file(files[i], file_path)


def count_tokens(text: str, model: str = "YOUR_MODEL_NAME") -> int:
    """
    Count the number of tokens in the given text.
    """
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def write_log(path: str, content: str) -> None:
    """
    Write the given content to the log file.
    """
    print(content)
    with open(path, "a") as f:
        f.write(content + "\n")