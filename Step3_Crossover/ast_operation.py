import re
import random
import tree_sitter
from tree_sitter import Language, Parser
from Step3_Crossover.ast_information import get_var_name, get_declaration, extract_decl_name, split_declaration


parser = Parser()
parser.set_language(Language("Libs/tree_sitter/parser/my-languages.so", "c"))


def select_nodes(ex_list_a: list, ex_list_b: list) -> tuple:
    """
    Selects two nodes of the same type from given lists.
    """
    while ex_list_a:
        node_a = random.choice(ex_list_a)
        type_b = [n for n in ex_list_b if n[1].type == node_a[1].type]
        if not type_b:
            ex_list_a.remove(node_a)
            continue
        node_b = random.choice(type_b)
        return node_a, node_b
    return None, None


def get_var_and_decl_info(root: tree_sitter.Node, global_node: list, select: tree_sitter.Node, code: str) -> tuple:
    """
    Get variable and declaration information from the AST.
    """
    var_all, decl_all = [], []
    for node in global_node:
        var_all.extend([v[1] for v in get_var_name(node, code)])
        decl_all.extend(get_declaration(node, code))
    var_all.extend([v[1] for v in get_var_name(root, code)])
    decl_all.extend(get_declaration(root, code))
    return var_all, decl_all


def rename_nodes(var_exist: list, decl_new: list, select: tree_sitter.Node, code: str) -> tuple:
    """
    Renames variables in declarations and code segment to avoid conflicts.
    """
    var_exist.extend([x.strip() for x in open("Libs/tree_sitter/keywords/c.txt", "r", encoding = "utf-8").readlines()])
    cross_segment = code[select.start_byte: select.end_byte]
    step1_decls, step2_decls, step3_decls = [], [], []
    decl_map = {}
    count = 0

    decl_new = list(dict.fromkeys(decl_new))
    for decl_stmt in decl_new:
        decl_map[decl_stmt] = extract_decl_name(decl_stmt)

    changed = True
    while changed:
        changed = False
        for decl_stmt, decl_name in decl_map.items():
            for var in decl_name:
                if (var in cross_segment) or any(var in extract_decl_name(d) for d in step1_decls):
                    if decl_stmt not in step1_decls:
                        step1_decls.append(decl_stmt)
                        changed = True

    step1_decls = list(dict.fromkeys(step1_decls))
    for i in decl_new:
        if i in step1_decls:
            step2_decls.append(i)

    for i, decl_stmt in enumerate(step2_decls):
        decl_name = decl_map[decl_stmt]
        for name in decl_name:
            if name in var_exist:
                while True:
                    new_name = f"var_{count}"
                    count += 1
                    if new_name not in var_exist:
                        var_exist.append(new_name)
                        break
                step2_decls = [re.sub(r"\b" + re.escape(name) + r"\b", new_name, decl) for decl in step2_decls]
                cross_segment = re.sub(r"\b" + re.escape(name) + r"\b", new_name, cross_segment)

    for i in step2_decls:
        split_decls = split_declaration(i)
        for j in split_decls:
            step3_decls.append(j)
    step3_decls = list(dict.fromkeys(step3_decls))
    return step3_decls, cross_segment


def cross_nodes(code: str, select: tree_sitter.Node, func_def: tree_sitter.Node, segment: str, decl: list) -> str:
    """
    Inserts code segment and declarations into target function.
    """
    compound_stmt = None
    for child in func_def.children:
        if child.type == "compound_statement":
            compound_stmt = child
            break
    if not compound_stmt:
        return code

    first_child = compound_stmt.children[1] if compound_stmt.children else None
    if not first_child:
        return code

    insert_line, insert_column = first_child.start_point
    code = code[: select.start_byte] + segment + code[select.end_byte:]
    lines = code.split("\n")
    new_lines = [
        *lines[: insert_line],
        *[decl_stmt for decl_stmt in decl],
        *lines[insert_line:]
    ]
    new_code = "\n".join(new_lines)
    return new_code