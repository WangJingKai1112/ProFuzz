import torch
import numpy as np
import tree_sitter
from tree_sitter import Language, Parser


parser = Parser()
parser.set_language(Language("Libs/tree_sitter/parser/my-languages.so", "c"))


class graphInfo():
    def __init__(self, factors: int, vertex_num: np.array, vertex_type: np.array, subgraph_type: np.array, initial_vertex: np.array):
        assert factors == len(vertex_num)
        self.factors = factors
        self.vertex_num = vertex_num
        self.vertex_type = vertex_type
        self.suggest_init = torch.Tensor(initial_vertex).long().unsqueeze(0)
        self.adjacency_matrix, self.fourier_freq, self.fourier_basis = [], [], []

        for i in range(len(self.vertex_num)):
            vertex = self.vertex_num[i]
            if subgraph_type[i] == "path":
                adj_mat = torch.diag(torch.ones(vertex - 1), -1) + torch.diag(torch.ones(vertex - 1), 1)
                adj_mat *= (vertex - 1.0)
            elif subgraph_type[i] == "complete":
                adj_mat = torch.ones(vertex, vertex) - torch.eye(vertex)
                adj_mat *= (vertex - 1.0)
            self.adjacency_matrix.append(adj_mat)
            deg_mat = torch.sum(adj_mat, dim = 0)
            laplacian = (torch.diag(deg_mat) - adj_mat)
            eig_val, eig_vec = torch.linalg.eigh(laplacian)
            self.fourier_freq.append(eig_val)
            self.fourier_basis.append(eig_vec)


class graphMutaton:
    def __init__(self, code: str, tree, vertex_num: np.array, vertex_type: np.array, eval_input: torch.Tensor):
        self.code = code
        self.tree = tree
        self.vertex_num = vertex_num
        self.vertex_type = vertex_type
        self.eval_input = eval_input
        self.operators = ["+", "-", "*", "/"]
        self.comparisons = ["<", ">", "<=", ">=", "==", "!="]
        self.num = len(vertex_num) - 1

    def mutate(self, node: tree_sitter.Node) -> str:
        if node.child_count:
            for child in reversed(node.children):
                self.code = self.mutate(child)
                if self.code == "":
                    return ""
        mutate_code = self.code

        self.tree = parser.parse(mutate_code.encode(), self.tree)
        x = self.tree.root_node.descendant_for_byte_range(node.start_byte, node.start_byte + 1)
        while x and x.type != node.type:
            x = x.parent
        if x and x.type == node.type:
            node = x
        
        if node.type == "assignment_expression" or node.type == "binary_expression":
            for child in node.children:
                if child.type in self.operators:
                    if self.vertex_type[self.num] != "op":
                        print("operator type error")
                        return ""
                    assert self.eval_input[self.num] < self.vertex_num[self.num]
                    mutate_text = self.operators[self.eval_input[self.num]]
                    self.num -= 1
                    start_byte, end_byte = child.start_byte, child.end_byte
                    mutate_code = mutate_code[:start_byte] + mutate_text + mutate_code[end_byte:]

                    ret_start_byte, ret_end_byte = start_byte, start_byte + len(mutate_text)
                    self.tree.edit(
                        start_byte = start_byte,
                        old_end_byte = end_byte,
                        new_end_byte = start_byte + len(mutate_text),
                        start_point = child.start_point,
                        old_end_point = child.end_point,
                        new_end_point = (
                            child.start_point[0],
                            child.start_point[1] + len(mutate_text)
                        )
                    )
                    self.tree = parser.parse(mutate_code.encode(), self.tree)
                    child = self.tree.root_node.descendant_for_byte_range(ret_start_byte, ret_end_byte)

        elif node.type in self.comparisons:
            if self.vertex_type[self.num] != "compare":
                print("comparison type error")
                return ""
            assert self.eval_input[self.num] < self.vertex_num[self.num]
            mutate_text = self.comparisons[self.eval_input[self.num]]
            self.num -= 1
            start_byte, end_byte = node.start_byte, node.end_byte
            mutate_code = mutate_code[:start_byte] + mutate_text + mutate_code[end_byte:]

            ret_start_byte, ret_end_byte = start_byte, start_byte + len(mutate_text)
            self.tree.edit(
                start_byte=start_byte,
                old_end_byte=end_byte,
                new_end_byte=start_byte + len(mutate_text),
                start_point=node.start_point,
                old_end_point=node.end_point,
                new_end_point=(
                    node.start_point[0],
                    node.start_point[1] + len(mutate_text)
                )
            )
            self.tree = parser.parse(mutate_code.encode(), self.tree)
            node = self.tree.root_node.descendant_for_byte_range(ret_start_byte, ret_end_byte)

        elif node.type == "if_statement":
            if self.vertex_type[self.num] != "if":
                print("if type error")
                return ""
            assert self.eval_input[self.num] < self.vertex_num[self.num]
            choice = self.eval_input[self.num]
            self.num -= 1
            if choice == 0:
                pass

            elif choice == 1:
                if_text = node.child_by_field_name("consequence")
                else_branch = node.child_by_field_name("alternative")
                mutate_code = mutate_code[:if_text.end_byte] + mutate_code[else_branch.end_byte:]

                ret_start_byte, ret_end_byte = node.start_byte, node.end_byte - (else_branch.end_byte - if_text.end_byte)
                self.tree.edit(
                    start_byte=node.start_byte,
                    old_end_byte=node.end_byte,
                    new_end_byte=node.end_byte - (else_branch.end_byte - if_text.end_byte),
                    start_point=node.start_point,
                    old_end_point=node.end_point,
                    new_end_point=(
                        if_text.end_point[0],
                        node.end_point[1]
                    )
                )
                self.tree = parser.parse(mutate_code.encode(), self.tree)
                node = self.tree.root_node.descendant_for_byte_range(ret_start_byte, ret_end_byte)

            else:
                if_text = node.child_by_field_name("consequence")
                else_branch = node.child_by_field_name("alternative")
                if else_branch.children[1].type == "compound_statement":
                    else_text = else_branch.children[1]
                else:
                    else_text = else_branch.children[1].child_by_field_name("consequence")
                mutate_code = mutate_code[:if_text.start_byte] + mutate_code[else_text.start_byte:else_text.end_byte] + mutate_code[else_text.end_byte:]

                ret_start_byte, ret_end_byte = node.start_byte, node.end_byte - (else_text.start_byte - if_text.start_byte)
                self.tree.edit(
                    start_byte=node.start_byte,
                    old_end_byte=node.end_byte,
                    new_end_byte=node.end_byte - (else_text.start_byte - if_text.start_byte),
                    start_point=node.start_point,
                    old_end_point=node.end_point,
                    new_end_point=(
                        node.start_point[0] + (if_text.start_point[0] - node.start_point[0]) + (else_text.end_point[0] - else_text.start_point[0]),
                        node.end_point[1]
                    )
                )
                self.tree = parser.parse(mutate_code.encode(), self.tree)
                node = self.tree.root_node.descendant_for_byte_range(ret_start_byte, ret_end_byte)

        self.code = mutate_code
        return self.code