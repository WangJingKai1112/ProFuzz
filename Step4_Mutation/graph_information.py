import numpy as np
from tree_sitter import Language, Parser


parser = Parser()
parser.set_language(Language("Libs/tree_sitter/parser/my-languages.so", "c"))


def node_counter(cursor, code: str, factors: int, vertex_num: list, vertex_type: list, subgraph_type: list, initial_vertex: list) -> tuple:
    """
    Recursively counts AST nodes for graph.
    """
    node = cursor.node
    operators = ["+", "-", "*", "/"]
    comparisons = ["<", ">", "<=", ">=", "==", "!="]

    if node.type == "assignment_expression" or node.type == "binary_expression":
        for child in node.children:
            if child.type in operators:
                factors += 1
                vertex_num.append(4)
                vertex_type.append("op")
                subgraph_type.append("complete")
                initial_vertex.append(operators.index(child.type))
    elif node.type in comparisons:
        factors += 1
        vertex_num.append(6)
        vertex_type.append("compare")
        subgraph_type.append("complete")
        initial_vertex.append(comparisons.index(node.type))
    elif node.type == "if_statement":
        factors += 1
        vertex_num.append(3 if len(node.named_children) > 2 else 1)
        vertex_type.append("if")
        subgraph_type.append("complete")
        initial_vertex.append(0)
    
    if cursor.goto_first_child():
        while True:
            factors, vertex_num, vertex_type, subgraph_type, initial_vertex = node_counter(cursor, code, factors, vertex_num, vertex_type, subgraph_type, initial_vertex)
            if not cursor.goto_next_sibling():
                break
        cursor.goto_parent()
    return factors, vertex_num, vertex_type, subgraph_type, initial_vertex


def vertex_info(code: str) -> tuple:
    """
    Extracts vertex information.
    """
    tree = parser.parse(code.encode())
    root = tree.root_node
    cursor = root.walk()
    factors, vertex_num, vertex_type, subgraph_type, initial_vertex = node_counter(cursor, code, 0, [], [], [], [])
    return factors, np.array(vertex_num), np.array(vertex_type), np.array(subgraph_type), np.array(initial_vertex)