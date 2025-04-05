import re
import tree_sitter
from tree_sitter import Language, Parser


LANGUAGE = Language("Libs/tree_sitter/parser/my-languages.so", "c")
parser = Parser()
parser.set_language(LANGUAGE)


def extract_func_and_decl(node: tree_sitter.Node) -> tuple:
    """
    Extract function definitions and global declarations from the AST node.
    """
    func_def, global_decl = [], []
    for child in node.children:
        if child.type == "function_definition":
            func_def.append(child)
        if child.type == "declaration":
            global_decl.append(child)
    return func_def, global_decl


def get_swap_list(func_def: list) -> list:
    """
    Capture the list of nodes that can be swapped.
    """
    swap_list = []
    with open("Step3_Crossover/Query_Swap_List.scm", "r") as f:
        query_text = f.read()
    query = LANGUAGE.query(query_text)
    for i in range(len(func_def)):
        node = func_def[i]
        captures = query.captures(node)
        for n, _ in captures:
            swap_list.append((i, n))
    return swap_list


def get_var_name(node: tree_sitter.Node, code: str) -> list:
    """
    Capture the variable names from the AST node.
    """
    var_name = []
    with open("Step3_Crossover/Query_Var_Name.scm", "r") as f:
        query_text = f.read()
    query = LANGUAGE.query(query_text)
    captures = query.captures(node)
    for n, _ in captures:
        var_name.append((n.start_point, code[n.start_byte: n.end_byte]))
    return var_name


def get_declaration(node: tree_sitter.Node, code: str) -> list:
    """
    Capture the declaration statements from the AST node.
    """
    declaration = []
    query_text_1 = LANGUAGE.query("(declaration) @declaration1")
    query_text_2 = LANGUAGE.query("(parameter_declaration) @declaration2")
    captures_1 = query_text_1.captures(node)
    captures_2 = query_text_2.captures(node)
    for n, _ in captures_1:
        declaration.append(code[n.start_byte: n.end_byte])
    for n, _ in captures_2:
        if code[n.start_byte: n.end_byte] == "void":
            continue
        declaration.append(code[n.start_byte: n.end_byte] + ";")
    return declaration


def extract_decl_name(decl_stmt: str) -> list:
    """
    Extract variable names from a declaration statement.
    """
    pattern = r"\b[a-zA-Z_]\w*\b(?=\s*(?:=|,|;|\[|&|\}))"
    decl_name = []
    unique_name = set()
    matches = re.findall(pattern, decl_stmt)
    for var in matches:
        if var and var.strip() not in unique_name:
            decl_name.append(var.strip())
            unique_name.add(var.strip())
    return decl_name


def split_declaration(decl_stmt: str) -> list:
    """
    Split a complex declaration statement into individual declarations.
    """
    func_pattern = r"^[\w\s\*]+\([\w\s,\*]*\)\s*;"
    if re.match(func_pattern, decl_stmt.strip()):
        return []
    decl_pattern = r"([a-zA-Z_][\w\s\*\[\]]+)\s+(.+);"
    split_decl = []
    matches = re.match(decl_pattern, decl_stmt)
    if matches:
        var_type = matches.group(1).strip()
        var_list = matches.group(2).split()
        var_decl_pairs = []
        depth = 0
        curr_var = ""
        for char in var_list:
            if char == "," and depth == 0:
                var_decl_pairs.append(curr_var.strip())
                curr_var = ""
            else:
                curr_var += char
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
        var_decl_pairs.append(curr_var.strip())
        for var_decl in var_decl_pairs:
            split_decl.append(f'{var_type} {var_decl};')
    else:
        split_decl.append(decl_stmt)
    return split_decl